# Goal3780 HIPRT Grouped Vector Sum F64x2

## Purpose

Goal3780 adds a generic HIPRT grouped vector-sum materializer:

`rtdl_hiprt_grouped_vector_sum_f64x2`

The contract takes dense group ids plus two float64 value columns, then returns
dense per-group `sum_x` and `sum_y` arrays. It is a reusable grouped reduction
primitive. It does not contain Barnes-Hut, force-law, mass, opening-angle, or
inverse-square semantics; force laws remain app code.

## What Changed

- Added the app-name-free HIPRT native ABI
  `rtdl_hiprt_grouped_vector_sum_f64x2`.
- Added `rtdsl.grouped_vector_sum_f64x2_hiprt`.
- Added the generic engine feature `grouped_vector_sum_f64x2` with HIPRT status
  `native`.
- Updated the v2.10 AMD/HIPRT parity map so `barnes_hut` no longer lists
  `grouped_vector_force_reduction` as missing.

## Barnes-Hut Impact

This closes the Barnes-Hut generic HIPRT contract gap for functional AMD pod
planning, but it does not provide AMD hardware evidence.

Closed by Goal3780:

- generic dense grouped float64 vector-sum materialization;
- HIPRT symbol parity for the grouped vector continuation piece;
- fail-closed validation for out-of-range dense group ids.

Still open:

- AMD hardware functional validation;
- AMD performance evidence;
- any public speedup, Barnes-Hut paper-reproduction, or release wording.

The parity stage for `barnes_hut` moves to `ready_for_amd_functional_pod`.
The overall AMD/HIPRT parity map still has two compatibility-only apps:
`raydb_style` and `triangle_counting`.

## Validation

Local focused validation target:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3780_hiprt_grouped_vector_sum_f64x2_test tests.goal3753_amd_hiprt_benchmark_parity_plan_test tests.goal3773_hiprt_point_group_nearest_witness_test tests.goal3774_hiprt_point_group_nearest_device_columns_test tests.goal3775_hiprt_ray_triangle_closest_hit_3d_test tests.goal3776_hiprt_collect_k_bounded_i64_test tests.goal3777_hiprt_aggregate_frontier_collect_2d_test tests.goal3779_hiprt_grouped_i64_count_sum_test
```

Clean pod validation should build HIPRT from a clean checkout, run the focused
test, and write:

`docs/reports/goal3780_hiprt_grouped_vector_sum_f64x2_a5000.json`

## Boundary

Goal3780 does not authorize AMD hardware evidence, AMD performance claims,
RT-core speedup claims, whole-app Barnes-Hut claims, paper reproduction claims,
zero-copy claims, release claims, or app-specific native-engine logic.

The NVIDIA CUDA/Orochi HIPRT path is useful functional implementation evidence,
not AMD hardware evidence.
