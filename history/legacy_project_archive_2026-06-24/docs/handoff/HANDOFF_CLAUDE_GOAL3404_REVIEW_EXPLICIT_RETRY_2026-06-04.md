# Handoff: Goal3404 Explicit Retry Review

Please perform an independent read-only review of Goal3404 and write the result
to:

`docs/reviews/goal3407_claude_review_goal3404_exact_device_columns_explicit_retry_2026-06-04.md`

## Context

Goal3404 proves the explicit recovery path for `PairColumnStreamCapacityStatus`:
a bounded exact device-column call overflows at `max_rows=100`, exposes
`retry_capacity_hint=11316`, and an explicit caller retry with that capacity
produces a device-resident exact stream whose pairs match exact host-refined
rows.

## Files To Inspect

- `scripts/goal3404_exact_device_columns_explicit_retry_probe.py`
- `docs/reports/goal3404_exact_device_columns_explicit_retry_probe_2026-06-04.json`
- `docs/reports/goal3404_exact_device_columns_explicit_retry_probe_2026-06-04.md`
- `tests/goal3404_exact_device_columns_explicit_retry_probe_test.py`
- `src/rtdsl/optix_runtime.py`

## Questions

1. Does the probe show explicit caller-controlled retry rather than hidden
   dispatch or automatic retry?
2. Does the overflow status correctly expose required capacity and no partial
   rows?
3. Does the retried stream match exact rows and remain device-resident?
4. Are all claim boundaries still closed?

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, `reject`.
