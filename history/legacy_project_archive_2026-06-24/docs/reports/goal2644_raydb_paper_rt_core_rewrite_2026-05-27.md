# Goal2644 RayDB Paper-Shaped RT-Core Rewrite

Date: 2026-05-27

## Purpose

The earlier RayDB-style benchmark path was a useful Python+partner+RTDL grouped
reduction benchmark, but it did not reproduce the RayDB paper's RT-core
execution shape. It used columnar grouped-reduction paths and therefore must not
be reported as an RT-core RayDB result.

Goal2644 starts the rewrite toward the paper path: Python owns the RayDB query
encoding, while RTDL must provide a generic RT primitive that can be lowered to
OptiX without any RayDB-specific native code.

## Reference Implementation Intake

Reference code:

- repository: `https://github.com/rubaolee/RayDB-i0`
- branch: `fin`
- commit reviewed locally: `a610c00d7334d8907435cc0a124f9ca8392ee456`
- key files: `src/raydb/raydb.cu`, `src/raydb/raydb.cpp`

Observed reference execution shape:

- each data record is encoded as one triangle;
- the aggregation value is encoded on the triangle `X` coordinate;
- the group id is encoded on the triangle `Y` coordinate;
- the scan predicate tuple is encoded on the triangle `Z` coordinate;
- the ray generator launches dense `+Z` rays through the query region;
- ray spacing follows the paper/reference guarantee: `Sx/2` by `Sy/2`;
- the any-hit shader reads `optixGetPrimitiveIndex()`;
- primitive hits are deduplicated with an atomic primitive flag;
- grouped aggregation is performed by atomic add into the group result buffer;
- the GAS build uses `OPTIX_GEOMETRY_FLAG_REQUIRE_SINGLE_ANYHIT_CALL`.

## Implemented Local Contract

Added backend:

```text
paper_rt_cpu_reference
```

This backend is a CPU contract reference for the paper-shaped path:

- one fixture row becomes one `Triangle3D` primitive;
- scan fields are mixed-radix encoded onto `Z`;
- the dense group key is encoded onto `Y`;
- aggregate payload is encoded onto `X`;
- query scan values launch dense `+Z` rays;
- primitive hit ids are deduplicated before grouped reduction through the
  generic CPU reference primitive
  `generic_ray_triangle_primitive_grouped_i64_reduction_3d`;
- grouped `count`, `sum`, `min`, `max`, and `avg_as_sum_count` match the
  existing columnar CPU oracle.

This is deliberately not a performance path. It is a correctness and lowering
contract for the native RT-core implementation.

## Native Boundary

The CPU reference primitive now used by the app is:

```text
generic_ray_triangle_primitive_grouped_i64_reduction_3d
```

The missing piece is its OptiX native lowering. The primitive must remain
app-name-free. It should accept:

- `Ray3D` queries;
- `Triangle3D` build primitives;
- per-primitive ids;
- per-primitive dense group ids;
- per-primitive integer payload values;
- a deduplication policy;
- a grouped reduction operation such as count, sum, min, max, or sum_count.

It must be no RayDB-specific native implementation: no RayDB, SQL, table, SSB,
database, or benchmark-specific vocabulary in the native engine.

The app remains responsible for RayDB-specific lowering:

- SQL-like predicate interpretation;
- column-to-axis encoding;
- query-region/ray-grid generation;
- output row naming and formatting;
- comparison against database or authors-code baselines.

## Current Results

Local command:

```bash
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py --backend paper_rt_cpu_reference --mode all
```

Result:

- all modes match the existing CPU grouped-aggregate oracle;
- the tiny fixture has 8 triangles;
- the predicate matches 4 rows;
- hit deduplication reduces 18 raw hit events to 4 primitive hits for the
  revenue-valued modes;
- no RT-core speedup claim is authorized.

The legacy `optix` columnar payload path is now marked
`rt_core_accelerated=false` for this app because it is not the paper-shaped
RayDB traversal path.

## OptiX Backend Status

Added backend:

```text
paper_rt_optix
```

It lowers through the generic native symbol
`rtdl_optix_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction` when a
rebuilt OptiX library is available. On this Mac it is expected to fail before
runtime validation because there is no Linux CUDA driver library. Pod build/run
validation remains required before any correctness or performance claim.

## Verification

Local verification:

```bash
PYTHONPATH=src:. python3 -m py_compile examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py --backend paper_rt_cpu_reference --mode all
```

Unit tests:

```bash
PYTHONPATH=src:. python3 -m unittest -v tests.goal2644_raydb_paper_rt_contract_test
PYTHONPATH=src:. python3 -m unittest -v tests.goal2495_raydb_style_cpu_reference_fixture_test tests.goal2498_raydb_style_optix_count_sum_parity_test tests.goal2517_partner_resident_fused_sum_count_i64_test tests.goal2644_raydb_paper_rt_contract_test
```

Observed local result: 25 tests passed, 2 skipped because local macOS has no
Linux CUDA driver library for OptiX. A direct local `paper_rt_optix` run fails
at CUDA driver loading as expected on this Mac.

## Next Work

The next engineering task is native implementation and pod validation:

1. Build the generic OptiX lowering for
   `generic_ray_triangle_primitive_grouped_i64_reduction_3d` on a CUDA pod.
2. Validate it uses GAS triangle traversal, `optixTrace`, any-hit primitive-id
   deduplication, and grouped reductions.
3. Keep the native ABI generic and app-name-free.
4. Validate `paper_rt_optix` against the CPU paper-shaped contract.
5. Compare OptiX query time against the existing CPU/Embree/partner baselines
   and, only if feasible, authors-code runs under a comparable input/query/result
   contract.

## Verdict

The RayDB benchmark is no longer considered complete as an RT-core benchmark.
It now has the correct paper-shaped contract reference, but the RT-core
implementation remains pending. The old partner-resident path remains useful as
a grouped-reduction benchmark subpath, not as the RayDB paper reproduction.
