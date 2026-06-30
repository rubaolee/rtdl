# Handoff: Claude Review for Fused Segment-Pair Count Chain

Date: 2026-06-03

Please perform an independent review of Goals 3210-3213 and write the review to:

`docs/reviews/goal3214_claude_review_fused_segment_pair_count_chain_2026-06-03.md`

## Scope

Review the new generic fused count path:

- Goal3210: native/runtime ABI for
  `rtdl_optix_prepared_segment_pair_left_id_count_device_columns`
- Goal3211: pod smoke evidence for dense count columns and overflow failure
- Goal3212: app route `run_packed_left_dense_count(...)`
- Goal3213: timing evidence comparing dense fused count with prior compact
  routes.

## Files to Inspect

- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/rtdsl/optix_runtime.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/README.md`
- `docs/reports/goal3211_segment_pair_left_id_count_device_columns_smoke_2026-06-03.md`
- `docs/reports/goal3211_segment_pair_left_id_count_device_columns_smoke_2026-06-03.json`
- `docs/reports/goal3213_rayjoin_dense_left_id_count_route_timing_2026-06-03.md`
- `docs/reports/goal3213_rayjoin_dense_left_id_count_route_timing_2026-06-03.json`
- Tests: `tests/goal3210_*`, `tests/goal3211_*`, `tests/goal3213_*`,
  plus `tests/goal3204_*` for the app route.

## Review Questions

1. Does the new native ABI remain app-agnostic and avoid RayJoin-specific
   native logic?
2. Is the fused count semantics correct and bounded: count hits by remapped
   pair-column `left_id`, direct-address `group_capacity`, overflow fail-closed?
3. Is the Python runtime front door correctly scoped as a generic
   segment-pair dense count column output?
4. Does the app route keep RayJoin interpretation, ID remapping, and route
   choice in Python?
5. Does Goal3213's performance interpretation follow from the artifact without
   making public speedup, release, true-zero-copy, or paper-reproduction claims?
6. What must be fixed before stronger RayJoin comparison or before promoting
   this primitive in public docs?

## Expected Verdict

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.

This review must not authorize release, public speedup claims, broad RT-core
claims, true-zero-copy claims, or RayJoin paper reproduction claims.
