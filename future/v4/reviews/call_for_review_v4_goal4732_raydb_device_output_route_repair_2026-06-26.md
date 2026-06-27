# Call For Review: V4 Goal4732 RayDB Device-Output Route Repair

Please review:

- `future/v4/v4_goal4732_raydb_device_output_route_repair_2026-06-26.md`
- `future/v4/evidence/v4_goal4732_raydb_device_output_route_repair_2026-06-26.json`
- `examples/current/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
- `scripts/v4_goal4669_full_app_level_pod_benchmark.py`
- `tests/v4_goal4732_raydb_device_output_route_test.py`
- `tests/v4_goal4669_full_app_runner_test.py`
- `future/v4/evidence/v4_goal4732_raydb_focused_20260626/summary.json`
- `future/v4/evidence/v4_goal4732_raydb_focused_20260626/summary.md`

## Context

Goal4669 measured `raydb_style` as V4/V2.14 hot `0.974x`, but the raw V4 row
used the legacy `paper_rt_optix_prepared_grouped_reduction` route. Goal4732 adds
and binds an app-level V4 route:

`paper_rt_v4_cupy_device_grouped_reduction`

through:

`v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`

## Questions For Reviewer

1. Is the root-cause statement correct: Goal4669's RayDB V4 row measured the
   legacy route, not the V4 device-output surface?
2. Does the new backend remain generic runtime/operator work rather than a
   RayDB-specific native kernel?
3. Is it correct that the old 0.974x row is not erased, but must be superseded
   by the focused same-hardware rerun before updating the 10-app matrix?
4. Does the runner correctly bind only `v4_current/raydb_style` to the new V4
   route while leaving V2.14 and V3.0.2 baselines unchanged?
5. Is the focused result correctly classified as no-regression repair, not a
   high-performance win, given V4/V2.14 hot `0.985x` and V4/V3.0.2 hot `0.954x`?
6. Are the non-authorization boundaries sufficient?

## Requested Verdict Labels

- `accept_goal4732_route_repair_pending_pod_rerun`
- `accept_with_required_amendments`
- `reject_goal4732_not_generic_or_not_v4_route`

## Non-Authorization

This review must not authorize final V4 tag, public speed claims, whole-app
high-performance claims, all-benchmark speedups, geomean headlines, arbitrary
callbacks, raw OptiX callbacks, app-specific native kernels, true-zero-copy
wording, or replacement of the 10-app matrix before a focused POD rerun.
