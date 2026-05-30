# Goal2690 Post-Goal2689 Contract Honesty Fixes

Date: 2026-05-30

Status: implemented; ready for external re-review.

## Purpose

Goal2689 accepted Goal2688 with boundary and identified six follow-up issues
before native CUDA hit-column implementation should begin. Goal2690 closes the
local, non-pod blockers:

- F1: `caller_asserted` group-id bounds were reported as validated.
- F2: CUDA-shaped native-column metadata could claim the host-materialization
  bottleneck was removed without hardware proof.
- F3: neighboring RayDB paths still used `ready` / promoted wording.
- F5: `deferred_device_check` metadata existed but was untested.
- F6: RayDB v2.5 result parity still used exact row equality with no float
  tolerance policy.

F4 remains a hardware evidence boundary: the Torch/CUDA gather branch is still
skip-guarded until an `sm_70+` pod is available.

## Code Changes

`src/rtdsl/hit_stream_handoff.py`

- Added `native_device_column_output_proven_on_hardware` to
  `RtdlHitStreamColumnHandoff`.
- Gated `removes_host_materialization_bottleneck` on:
  - `source_mode == "native_device_columns"`;
  - CUDA-resident columns;
  - no host-row bridge;
  - `native_device_column_output_proven_on_hardware=True`.
- Added a fail-closed constructor guard: hardware proof cannot be asserted for
  CPU columns, bridge paths, or non-native source modes.
- Added `device_resident_but_unproven_native_output` so synthetic CUDA-shaped
  tests and future prototype paths are machine-readable without implying proof.
- Changed payload metadata so `group_id_bounds_validated=True` only means an
  actual host scan ran.
- Added explicit:
  - `group_id_bounds_caller_asserted`;
  - `group_id_bounds_asserted_not_verified`;
  - existing `device_group_id_validation_pending`.

`examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`

- Added a named CPU-reference comparison policy:
  - ordered rows;
  - exact equality for integral values;
  - `math.isclose` for non-integral numerics;
  - `abs_tol=1e-9`, `rel_tol=1e-9`.
- Replaced exact tuple equality in RayDB result paths with
  `_rows_match_cpu_reference`.
- Added `cpu_reference_match_policy` metadata to RayDB v2.5/native result
  payloads.
- Replaced remaining Boolean `native_rt_core_lowering_ready=True` in the RayDB
  paper/native paths with:
  - `native_rt_core_lowering_path_present=True`;
  - `native_rt_core_lowering_ready=False`;
  - explicit validation text.
- Changed the prior promoted phase-timing flag in the RayDB paper/native path to
  `promoted_performance_path=False`, preserving the project rule that these
  paths are evidence-bearing but not public promotion by metadata alone.

`tests/goal2685_device_resident_hit_stream_handoff_test.py`

- Added a CUDA-shaped fake column to test device-shaped metadata without a GPU.
- Locked that CUDA-shaped, unproven native columns do **not** claim the
  materialization bottleneck was removed.
- Locked that hardware proof cannot be asserted for CPU columns.
- Locked that `caller_asserted` means asserted but not validated.
- Added `deferred_device_check` metadata coverage.

`tests/goal2690_post_goal2689_contract_honesty_test.py`

- Added a named regression test for Goal2689 follow-up closure:
  - RayDB v2.5 paths no longer contain `native_rt_core_lowering_ready=True`;
  - no `promoted_performance_path=True` remains in the RayDB app source;
  - hit-stream and device-hit-stream paths expose the tolerance policy;
  - readiness remains false while path-present metadata remains true.

## What Remains Blocked

These require design/native work or pod evidence and are intentionally not
claimed here:

1. Real OptiX CUDA-resident `ray_ids:int64` and `primitive_ids:int64` output.
2. Native buffer ownership/lifetime state machine.
3. Device-side group-id validation/error-flag kernel.
4. Executed Torch/CUDA gather evidence on `sm_70+`.
5. Triton continuation pod evidence across count, sum, min, max, and
   avg-as-sum-count.
6. Neutral multi-partner buffer seam work, including DLPack /
   `__cuda_array_interface__` decisions.

## Validation

Windows focused suite:

```text
PYTHONPATH=src;. py -3 -m unittest ^
  tests.goal2690_post_goal2689_contract_honesty_test ^
  tests.goal2685_device_resident_hit_stream_handoff_test ^
  tests.goal2644_raydb_paper_rt_contract_test ^
  tests.goal2684_generic_rt_hit_stream_handoff_test ^
  tests.goal2662_v2_5_partner_continuation_contract_test ^
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test ^
  tests.goal2681_v2_5_triton_partner_adapter_front_door_test
```

Result:

```text
Ran 57 tests in 7.654s
OK (skipped=5)
```

Compile check:

```text
py -3 -m py_compile src\rtdsl\hit_stream_handoff.py examples\v2_0\research_benchmarks\raydb_style\rtdl_raydb_style_benchmark_app.py tests\goal2685_device_resident_hit_stream_handoff_test.py tests\goal2690_post_goal2689_contract_honesty_test.py
```

Result: pass.

`git diff --check`: pass.

Local Linux `192.168.1.20` sync check after push:

```text
git reset --hard origin/main
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so PYTHONPATH=src:. python3 -m unittest \
  tests.goal2690_post_goal2689_contract_honesty_test \
  tests.goal2685_device_resident_hit_stream_handoff_test \
  tests.goal2644_raydb_paper_rt_contract_test \
  tests.goal2684_generic_rt_hit_stream_handoff_test \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test \
  tests.goal2681_v2_5_triton_partner_adapter_front_door_test
```

Result:

```text
Ran 57 tests in 2.917s
OK (skipped=5)
```

## Claim Boundary

Goal2690 is not a device-resident implementation goal and makes no speedup,
zero-copy, release, or broad RT-core claim. It closes metadata-honesty and
comparison-policy defects so the next design step can proceed without inheriting
known false-positive readiness signals.
