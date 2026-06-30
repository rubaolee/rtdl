# Handoff: Review Goal3306 Prepared Point-Probe Columns

Please perform a read-only review and write the result to:

`docs/reviews/goal3307_claude_review_goal3306_prepared_point_probe_columns_2026-06-04.md`

## Current Commit

`3d78eb3e`

## Context

Goal3306 added a generic prepared point-probe-column handle for repeated
OptiX point/closed-shape scalar-count queries. This responds to the Goal3305
review conclusion that the next RayJoin target should be generic
scalar-count launch/packing/residency overhead.

The measured result is intentionally modest:

- same-commit old mode PIP: 0.343 ms, RTDL/RayJoin 1.56x;
- same-commit prepared-points PIP: 0.317 ms, RTDL/RayJoin 1.43x;
- native count pass remains about 0.261 ms in both modes;
- point upload is removed from the timed lane, but point-column preparation is
  about 0.035 ms and is outside repeated-query timing.

This should be treated as a repeated-query overhead improvement, not a
one-shot win, not a RayJoin win, and not a release/speedup claim.

## Files To Inspect

- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/__init__.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py`
- `docs/reports/goal3306_prepared_point_probe_columns_scalar_count_2026-06-04.md`
- `docs/reports/goal3306_prepared_points_rayjoin_same_slice_pod_2026-06-04.json`
- `docs/reports/goal3306_baseline_device_filtered_same_slice_pod_2026-06-04.json`
- `tests/goal3306_prepared_point_probe_columns_scalar_count_test.py`
- `docs/research/future_version_to_do_list.md`

## Questions

1. Is the new native/Python surface generic and app-agnostic?
2. Does the RayJoin app preserve exact validation and inclusive boundary
   semantics?
3. Does the report correctly state the result as a modest repeated-query win,
   not a one-shot win or RayJoin-beating claim?
4. Do the artifacts support the 0.343 ms to 0.317 ms PIP improvement and the
   conclusion that native traversal/count remains the bottleneck?
5. Are claim-boundary flags, timing units, mode labels, counts, and route names
   consistent?
6. Is the recommended next direction sound: persistent launch/count buffers,
   batched/replayed scalar-count launches, or a compact generic predicate-count
   path?

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. Lead with findings by severity, then summarize.
