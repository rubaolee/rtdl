# Goal3882 Prepared-Session Residency Metadata For Remaining Profiled Apps

## Purpose

Goal3880 added prepared-session residency metadata to RTNN. Goal3882 applies the
same app-level metadata pattern to the other current prepared-session residency
profile rows:

- Hausdorff/X-HD prepared threshold;
- LibRTS prepared AABB index;
- triangle-counting RT-Graph 2A1 prepared generic RT summary.

## What Changed

Updated:

- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py`
- `examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py`
- `examples/v2_0/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py`

Each prepared payload now emits `prepared_session_residency` with:

- a generic prepared-session cache key;
- a non-authorizing residency policy;
- `explicit_reuse_helper = get_or_prepare_explicit_session`;
- `cache_enabled_by_default = false`;
- `cold_hot_phase_split_required = true`;
- `prepare_once_query_many_pattern = true`;
- false claim-boundary flags.

## Boundary

This is metadata and ergonomics. It does not change the compute path, enable a
hidden cache, or choose a backend/partner automatically.

Guardrails:

- no hidden automatic partner/backend selection;
- not a true-zero-copy or public speedup claim;
- app-specific native-engine logic remains forbidden.

The emitted primitive names remain generic:

- `fixed_radius_threshold_2d`
- `aabb_index_query_2d`
- `ray_triangle_weighted_any_hit_sum_3d`

## Validation

Added `tests/goal3882_prepared_session_residency_metadata_remaining_profiled_apps_test.py`.

The test uses mocks for native/expensive calls and verifies that each app
payload includes the prepared-session residency metadata without enabling
claims or altering the existing high-level payload contract.
