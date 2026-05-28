# Goal2640 Implementation Report: Generic RT-Core Point/Expanded-AABB Row Primitive

Date: 2026-05-27

Status: CPU/Embree/reference implementation complete; OptiX native symbol
implemented, built, parity-tested, and benchmarked on an RTX A5000 pod.

## Purpose

Barnes-Hut previously had a narrow RT-core-backed node-coverage decision
subpath, but the newer `AGGREGATE_FRONTIER_COLLECT_2D` row collector is
host-side traversal inside the OptiX library. Goal2640 starts the missing
RT-core bridge without putting Barnes-Hut semantics in the engine.

The implemented primitive is:

```text
EXPANDED_AABB_POINT_MEMBERSHIP_2D
```

Contract:

```text
generic_expanded_aabb_point_membership_rows_2d_v1
```

Row schema:

```text
source_id, box_id, metadata_flags
```

Current `metadata_flags` value:

```text
0 = no flags set
```

## Engine Boundary

Allowed in native/runtime code:

- source points;
- indexed 2-D AABBs;
- caller-provided symmetric expansion values;
- generic point/AABB membership;
- row offsets;
- fail-closed row capacity;
- Embree/OptiX acceleration structures.

Forbidden and not added:

- Barnes-Hut names;
- force law;
- mass/weight interpretation;
- inverse-square math;
- N-body semantics;
- contact/collision semantics;
- DB/graph/application semantics.

The app or lowering may use the rows as a near/exclusion candidate set, but the
engine only emits app-free IDs.

## How This Uses RT Cores

The intended OptiX execution path is the existing generic AABB RT traversal
path, extended from count-only `point_contains` to row-emitting
`point_contains_rows`.

Mechanism:

1. The caller prepares 2-D indexed boxes after applying caller-owned expansion.
2. The OptiX backend builds a custom-primitive GAS/BVH over those AABBs.
3. Each source point becomes a short probe ray through the point.
4. The OptiX raygen launches one probe per source point.
5. The device code calls `optixTrace` against the prepared AABB GAS.
6. The custom intersection program checks point-in-AABB membership.
7. The any-hit program emits generic `(source_id, box_id)` rows.

This is RT-core-relevant because the workload uses OptiX GAS traversal through
`optixTrace`. It is still not app-specific: the native code does not know
Barnes-Hut, theta, mass, force, inverse-square math, or aggregate-frontier
semantics.

## Expected Embree vs OptiX Performance Shape

Expected behavior before pod evidence:

- Tiny workloads may favor Embree because OptiX pays launch, upload/download,
  and GAS-build overhead.
- One-shot medium workloads may be mixed because traversal speed competes with
  host/device transfer and row materialization cost.
- Large prepared/reused workloads should be the strongest OptiX case: if the
  AABB GAS is reused and many source queries are issued, traversal should
  dominate enough for RT hardware to help.
- Dense outputs may reduce or erase the RT advantage because row
  materialization, atomics, sorting/deduplication, and download can dominate.

The pod benchmark must therefore separate:

- prepare/GAS build time;
- query/traversal time;
- row materialization and download time;
- total one-shot time;
- prepared/reused-query time.

If OptiX loses on large prepared workloads, the likely issue is not the
frontier app itself but the row-output path: atomics, output density,
download, or missing device-resident continuation. The next optimization would
then be count/flag/compact or device-resident continuation, not adding
Barnes-Hut-specific native logic.

## Implemented Files

- `src/rtdsl/aabb_index.py`
  - Adds the public `expanded_aabb_point_membership_rows_2d` function.
  - Adds `ExpandedAabbPointMembershipOverflowError`.
  - Adds CPU and Embree row emission over expanded boxes.
  - Adds exact fail-closed total and per-source capacity checks.

- `src/rtdsl/optix_runtime.py`
  - Adds `PreparedOptixAabbIndex2D.collect_point_contains_rows`.
  - Adds `collect_aabb_point_membership_pair_rows_2d_optix`.
  - Wires the new native symbol through ctypes.

- `src/rtdsl/runtime.py`
  - Fixes dataclass field probing so 2-D dataclass records are not
    misclassified as 3-D records requiring `z`.

- `src/native/optix/rtdl_optix_workloads.cpp`
  - Extends the existing generic AABB any-hit kernel to emit rows for
    `point_contains`.
  - Adds `collect_prepared_aabb_index_2d_point_contains_rows_optix`.
  - Uses existing `optixTrace` AABB traversal path.

- `src/native/optix/rtdl_optix_api.cpp`
  - Exports `rtdl_optix_collect_prepared_aabb_index_2d_point_contains_rows`.

- `src/native/optix/rtdl_optix_prelude.h`
  - Declares the new native symbol.

- `src/rtdsl/primitive_hierarchy.py`
  - Adds `rows.expanded_aabb_point_membership_rows` under row emission.

- `docs/rtdl_primitive_catalog.md`
  - Documents the primitive and boundary.

- `tests/goal2640_expanded_aabb_point_membership_test.py`
  - Adds CPU correctness, fail-closed overflow, Embree parity, export, and
    app-boundary source tests.

- `scripts/goal2640_expanded_aabb_point_membership_perf.py`
  - Adds reproducible Embree-vs-OptiX timing for prepared and one-shot row
    emission paths.

## Local Verification

Command:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal2640_expanded_aabb_point_membership_test \
  tests.goal2580_optix_aabb_index_native_symbol_test \
  tests.goal2623_optix_aabb_pair_rows_test \
  tests.goal2624_primitive_hierarchy_test
```

Result:

```text
Ran 23 tests
OK (skipped=4)
```

Skipped rows require a local/pod OptiX backend library.

Compile smoke:

```bash
PYTHONPATH=src:. python3 -m py_compile \
  src/rtdsl/aabb_index.py src/rtdsl/optix_runtime.py
```

Result: passed.

## Pod Validation

Pod:

```text
ssh root@194.68.245.16 -p 22072 -i ~/.ssh/id_ed25519_rtdl_codex
```

Environment:

```text
GPU: NVIDIA RTX A5000, driver 565.57.01, 24564 MiB
CUDA: 12.8, nvcc V12.8.93
OptiX SDK: 8.1.0, extracted to /workspace/optix-8.1
Embree: 4.3.0 from libembree-dev
RTDL pod workdir: /workspace/rtdl_goal2640_min
```

Native build:

```bash
make build-optix \
  OPTIX_PREFIX=/workspace/optix-8.1 \
  CUDA_PREFIX=/usr/local/cuda-12.8 \
  NVCC=/usr/local/cuda-12.8/bin/nvcc
```

Export check:

```text
0000000000099110 T rtdl_optix_collect_prepared_aabb_index_2d_point_contains_rows
```

Parity test:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
  python3 -m unittest -v \
  tests.goal2640_expanded_aabb_point_membership_test \
  tests.goal2580_optix_aabb_index_native_symbol_test
```

Result:

```text
Ran 9 tests
OK
```

This validates CPU, Embree, and OptiX row parity for the deterministic fixture
and confirms the native OptiX symbol is app-name-free.

## Performance Evidence

Artifacts:

- `docs/reports/goal2640_perf_smoke.json`
- `docs/reports/goal2640_perf_262k.json`
- `docs/reports/goal2640_perf_1m_prepared.json`

The benchmark scene uses non-overlapping 2-D AABBs and point queries placed at
box centers, so expected output is exactly one row per query. This stresses
generic row emission while keeping correctness easy to check.

| Boxes | Queries / Rows | Mode | Embree ms | OptiX ms | OptiX vs Embree |
|---:|---:|---|---:|---:|---:|
| 1,024 | 65,536 | prepared query | 3,167.398 | 43.058 | 73.56x |
| 1,024 | 65,536 | public one-shot wrapper | 2,952.314 | 652.727 | 4.52x |
| 4,096 | 262,144 | prepared query | 18,861.329 | 236.325 | 79.81x |
| 4,096 | 262,144 | public one-shot wrapper | 19,362.985 | 2,592.775 | 7.47x |
| 16,384 | 1,048,576 | prepared query | 213,865.296 | 944.825 | 226.35x |

All measured rows matched between Embree and OptiX.

Interpretation:

- Prepared/reused OptiX is now the right path for this generic row primitive:
  the RTX A5000 path is 73x to 226x faster than the current Embree prepared
  row path on these row-emission workloads.
- Public one-shot wrapper speedups are smaller, but still positive on the
  measured cases, because they include OptiX GAS preparation, Python record
  construction, row grouping, and result construction.
- The result supports RT-core use for generic expanded-AABB/point membership
  rows, but it does not yet prove whole Barnes-Hut speedup. Barnes-Hut still
  needs a lowering from aggregate-frontier collection onto this generic row
  primitive plus app-owned/partner-owned force evaluation.

## Remaining Work

The native primitive itself is validated. The next work is integration:

1. Lower the Barnes-Hut aggregate-frontier app path onto
   `EXPANDED_AABB_POINT_MEMBERSHIP_2D` where the semantics match.
2. Keep force/mass/theta math in app or partner code.
3. Add a device-resident continuation path if row download/materialization
   becomes the next bottleneck.
4. Run Barnes-Hut app-level perf after the lowering, without adding
   Barnes-Hut-specific native engine logic.

## Current Claim Boundary

This implementation authorizes this narrow statement:

> RTDL now has a generic source-level primitive and native OptiX RT-core path
> for point/expanded-AABB membership rows, with CPU/Embree/OptiX parity tests
> and pod performance evidence on an RTX A5000.

It does not yet authorize:

- Barnes-Hut whole-app speedup claims;
- same-contract aggregate-frontier RT-core parity claims;
- broad public performance wording beyond the exact primitive/path/workloads
  measured here.
