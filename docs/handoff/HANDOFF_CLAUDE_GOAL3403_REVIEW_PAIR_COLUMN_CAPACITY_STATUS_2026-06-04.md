# Handoff: Goal3403 Pair Column Capacity Status Review

Please perform an independent read-only review of Goal3403 and write the result
to:

`docs/reviews/goal3405_claude_review_goal3403_pair_column_capacity_status_2026-06-04.md`

## Context

Goal3403 adds a generic `PairColumnStreamCapacityStatus` contract for OptiX
typed pair-column streams. It records bounded capacity, row count, required
capacity, overflow state, fail-closed policy, retry hint, and whether partial
rows were exposed. It does not automatically retry.

## Files To Inspect

- `src/rtdsl/optix_runtime.py`
- `scripts/goal3400_exact_device_columns_overflow_probe.py`
- `docs/reports/goal3403_pair_column_capacity_status_contract_2026-06-04.md`
- `tests/goal3403_pair_column_capacity_status_contract_test.py`
- `docs/reports/goal3394_optix_exact_membership_device_columns_live_probe_2026-06-04.json`
- `docs/reports/goal3398_full_br_county_exact_device_columns_2026-06-04.json`
- `docs/reports/goal3400_exact_device_columns_overflow_probe_2026-06-04.json`

## Questions

1. Is the capacity-status contract generic and app-agnostic?
2. Does it correctly distinguish successful streams from fail-closed overflowed
   streams?
3. Does it preserve explicit caller choice rather than hidden automatic retry or
   dispatch?
4. Do the refreshed pod artifacts prove success and overflow status metadata?
5. Does any wording overclaim release, speedup, RT-core use, true zero-copy,
   RayJoin reproduction, hidden dispatch, or app-specific native-engine behavior?

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, `reject`.
