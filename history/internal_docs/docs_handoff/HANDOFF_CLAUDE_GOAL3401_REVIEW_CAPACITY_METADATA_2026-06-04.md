# Handoff: Goal3401 Capacity Metadata Review

Please perform an independent read-only review of Goal3401 and write the result
to:

`docs/reviews/goal3402_claude_review_goal3401_capacity_metadata_2026-06-04.md`

## Context

Goal3399 flagged that the exact device-column bridge looked as if it allocated
the full point-by-shape worst-case capacity. Goal3401 fixed the native OptiX
status metadata so successful exact streams report allocated exact-row capacity,
while overflow still reports the caller-requested bounded capacity.

## Files To Inspect

- `src/native/optix/rtdl_optix_workloads.cpp`
- `docs/reports/goal3401_exact_device_columns_capacity_metadata_fix_2026-06-04.md`
- `tests/goal3401_exact_device_columns_capacity_metadata_fix_test.py`
- `docs/reports/goal3394_optix_exact_membership_device_columns_live_probe_2026-06-04.json`
- `docs/reports/goal3398_full_br_county_exact_device_columns_2026-06-04.json`
- `docs/reports/goal3400_exact_device_columns_overflow_probe_2026-06-04.json`
- `docs/reports/goal3394_optix_exact_membership_device_columns_bridge_2026-06-04.md`
- `docs/reports/goal3398_full_br_county_exact_stream_and_grouped_count_2026-06-04.md`
- `docs/reports/goal3400_exact_device_columns_overflow_probe_2026-06-04.md`

## Questions

1. Does the native bridge now report successful capacity as actual allocated
   exact rows, not point-by-shape worst-case capacity?
2. Does the overflow path still fail closed and preserve the requested `max_rows`
   capacity boundary?
3. Do the refreshed pod artifacts and tests prove the fix on the 4096 slice,
   full `br_county.cdb`, and forced-overflow probe?
4. Does any wording accidentally authorize release, public speedup,
   RayJoin-reproduction, RT-core speedup, true-zero-copy, hidden dispatch, or
   app-specific native-engine behavior?

## Required Verdict

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, `reject`.

Please lead with findings, then evidence, then release boundary. This review is
not a release authorization.
