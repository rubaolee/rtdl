# Handoff: Claude Review Goal3882 Profiled App Residency Metadata

Please perform a read-only review of Goal3882, which extends prepared-session
residency metadata from RTNN to all remaining current profiled prepared-session
apps.

## Files To Inspect

- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py`
- `examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py`
- `examples/v2_0/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py`
- `docs/reports/goal3882_prepared_session_residency_metadata_remaining_profiled_apps_2026-06-08.md`
- `docs/reports/goal3882_profiled_apps_residency_metadata_a5000/summary.json`
- `tests/goal3882_prepared_session_residency_metadata_remaining_profiled_apps_test.py`
- `src/rtdsl/prepared_session_residency.py`

## Review Questions

1. Do the three newly patched apps emit `prepared_session_residency` metadata
   without changing their computation paths?
2. Are the primitive names generic and app-agnostic:
   `fixed_radius_threshold_2d`, `aabb_index_query_2d`,
   `ray_triangle_weighted_any_hit_sum_3d`?
3. Does the A5000 artifact prove all four profiled rows pass and all four live
   app payloads emit the metadata with false automatic-partner and zero-copy
   flags?
4. Did the triangle-counting boundary-key refresh improve machine checkability
   without authorizing any new claim?
5. What remains before this prepared-session pattern should become a tutorial
   or default user idiom?

## Validation To Run

If possible:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal3882_prepared_session_residency_metadata_remaining_profiled_apps_test tests.goal3880_rtnn_prepared_session_residency_metadata_test tests.goal3876_scale_runner_prepared_session_profile_integration_test
```

## Required Output

Write the review to:

`docs/reviews/goal3883_claude_review_goal3882_profiled_apps_residency_metadata_2026-06-08.md`

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. State explicitly that the review does not authorize release action,
public speedup wording, broad RT-core wording, true-zero-copy wording,
automatic partner/backend selection, or app-specific native-engine logic.
