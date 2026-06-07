# Goal3782 HIPRT Graph-Cycle Scalar Count

Status: implemented locally; clean-pod validation pending.

## Purpose

Goal3782 closes the last v2.10 AMD/HIPRT benchmark-parity planning gap by adding
a generic HIPRT scalar-count path for canonical graph-cycle witnesses. The target
is the triangle-counting benchmark lane, but the native contract is not an app
or benchmark function: it counts canonical ascending graph-cycle candidates under
the existing graph CSR + edge-seed shape.

## Implementation

- Added `RtdlTriangleProbeCountKernel` beside the existing row-producing
  `RtdlTriangleProbeKernel`.
- Added direct and prepared C ABI calls:
  - `rtdl_hiprt_count_triangle_cycle_candidates`
  - `rtdl_hiprt_count_prepared_triangle_cycle_candidates`
- Added Python front doors:
  - `triangle_cycle_count_hiprt(graph, seeds, order="id_ascending")`
  - `PreparedHiprtGraphCSR.triangle_cycle_count(seeds, order="id_ascending")`
- Added canonical seed validation: scalar count requires canonical ascending unique seed edges.
  The old row path remains available for witness rows and duplicate-seed behavior.
- Promoted `graph_triangle_count` for HIPRT from `compatibility_fallback` to
  `native` in the engine feature matrix.
- Added `reduction.graph_cycle_count` to the primitive hierarchy and regenerated
  `docs/rtdl_primitive_catalog.md`.

## Current Parity Position

The v2.10 AMD/HIPRT benchmark parity map now reports:

| stage | count |
| --- | ---: |
| `ready_for_amd_functional_pod` | 10 |
| `compatibility_only_not_amd_perf_ready` | 0 |
| `needs_generic_hiprt_extension` | 0 |

This means all 10 benchmark lanes have app-agnostic HIPRT contracts ready for
AMD functional validation. It does not mean AMD hardware validation has happened.

## Boundary

This goal does not authorize release, AMD performance claims, broad RT-core
claims, whole-app speedup claims, paper-reproduction claims, or app-specific
native engine logic. NVIDIA CUDA/Orochi HIPRT evidence, when collected, is
functional implementation evidence only and is not AMD hardware evidence.

## Validation

Local focused validation target:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3782_hiprt_graph_cycle_count_test tests.goal3753_amd_hiprt_benchmark_parity_plan_test tests.goal3775_hiprt_ray_triangle_closest_hit_3d_test tests.goal3776_hiprt_collect_k_bounded_i64_test tests.goal3777_hiprt_aggregate_frontier_collect_2d_test tests.goal3779_hiprt_grouped_i64_count_sum_test tests.goal3780_hiprt_grouped_vector_sum_f64x2_test tests.goal3781_hiprt_columnar_i64_predicate_scan_test
```

Clean pod validation should build HIPRT from a clean checkout, run the focused
test, and write:

`docs/reports/goal3782_hiprt_graph_cycle_count_a5000.json`
