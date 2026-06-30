# Handoff: Claude Review Request for Goal3145

Please perform an independent read-only review of Goal3145, which exposes `segmented_min_f64` and `segmented_max_f64` through the v2.8 segmented typed stream partner-consumer front door with canonical output compaction.

## Files to Review

- `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`
- `tests/goal3111_v2_8_segmented_typed_stream_adapter_test.py`
- `tests/goal3145_segmented_minmax_front_door_canonical_compaction_test.py`
- `scripts/goal3145_segmented_minmax_front_door_pod_probe.py`
- `docs/reports/goal3145_segmented_minmax_front_door_canonical_compaction_2026-06-03.md`
- `docs/reports/goal3145_pod_artifacts/segmented_minmax_front_door_pod_probe_2026-06-03.json`

## Review Questions

1. Does Goal3145 correctly move `segmented_min_f64` and `segmented_max_f64` from deferred to supported partner-consumer front-door operations while leaving `compact_mask_i64` deferred?
2. Is the implementation app-agnostic and composed from generic grouped primitives (`partner_group_count_by_key`, `partner_group_min_by_key`, `partner_group_max_by_key`) rather than benchmark-app-specific logic?
3. Is the canonical output schema (`group_ids` plus `mins`/`maxes` plus `missing_group_ids`) correct and stable for both reference and partner paths?
4. Is the host-side output compaction boundary honest, with no device-residency, true-zero-copy, RT-core, speedup, automatic-dispatch, or release overclaim?
5. Does the RTX 4000 Ada pod artifact support only correctness/availability evidence, not performance or release claims?

## Expected Output

Write your review to:

`docs/reviews/goal3146_claude_review_goal3145_segmented_minmax_front_door_2026-06-03.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`. Lead with findings by severity, then answer the five review questions explicitly. If you find a blocker, state the exact file/line and the minimal required fix.

## Boundary

This review must not authorize v2.8 release, public speedup claims, RT-core claims, true-zero-copy claims, hidden dispatch, or automatic partner selection. It is an internal preview review only.
