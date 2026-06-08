# Goal3880 RTNN Prepared-Session Residency Metadata

## Purpose

Goal3877 added an explicit prepared-session reuse helper. Goal3880 wires the
same contract into a real benchmark app without changing runtime behavior:
RTNN's `prepared_optix_ranked_summary` payload now emits a prepared-session
cache key and residency policy for the actual input arguments.

## What Changed

Updated:

`examples/v2_0/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py`

The prepared OptiX ranked-summary payload now includes
`prepared_session_residency` with:

- `cache_key`;
- `policy`;
- `explicit_reuse_helper = get_or_prepare_explicit_session`;
- `cache_enabled_by_default = false`;
- `cold_hot_phase_split_required = true`;
- `prepare_once_query_many_pattern = true`;
- claim-boundary flags set to false.

The benchmark command and runner path are unchanged. This is honest app-level
metadata for user ergonomics, not a hidden cache and not a performance reroute.

## Boundary

- no hidden automatic partner/backend selection;
- not a true-zero-copy or public speedup claim;
- app-specific native-engine logic remains forbidden;
- cache use remains opt-in and caller-owned;
- the native primitive name remains generic:
  `fixed_radius_neighbors_3d_ranked_summary`.

## Validation

Added `tests/goal3880_rtnn_prepared_session_residency_metadata_test.py`.

The test mocks the historical RTNN runner so it can validate the payload locally
without requiring OptiX. It checks the cache key, policy, helper name, false
claim flags, and unchanged runner contract.
