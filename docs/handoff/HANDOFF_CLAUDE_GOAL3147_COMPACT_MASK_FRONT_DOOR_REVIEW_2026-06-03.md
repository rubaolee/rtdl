# Handoff: Claude Review Request for Goal3147

Please perform an independent read-only review of Goal3147, which exposes `compact_mask_i64` through the v2.8 segmented typed stream partner-consumer front door.

## Files to Review

- `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`
- `tests/goal3111_v2_8_segmented_typed_stream_adapter_test.py`
- `tests/goal3145_segmented_minmax_front_door_canonical_compaction_test.py`
- `tests/goal3147_compact_mask_front_door_test.py`
- `scripts/goal3147_compact_mask_front_door_pod_probe.py`
- `docs/reports/goal3147_compact_mask_front_door_2026-06-03.md`
- `docs/reports/goal3147_pod_artifacts/compact_mask_front_door_pod_probe_2026-06-03.json`

## Review Questions

1. Does Goal3147 correctly promote `compact_mask_i64` from the v2.8 deferred map into the supported partner-consumer front-door operations?
2. Is the operation honestly modeled as a stable candidate-stream filter, not as a grouped reduction?
3. Is the implementation app-agnostic and composed from existing generic compact-mask / mask-index / take helpers rather than benchmark-app logic?
4. Is the canonical output schema (`values`, `original_indices`) correct and stable for reference and partner paths?
5. Does the RTX 4000 Ada artifact prove only correctness/availability, while keeping host-prefix-sum, non-promoted-performance, no-speedup, no-RT-core, no-zero-copy, no-release boundaries intact?

## Expected Output

Write the review to:

`docs/reviews/goal3148_claude_review_goal3147_compact_mask_front_door_2026-06-03.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`. Lead with findings by severity, then answer the five review questions explicitly. If you find a blocker, state the exact file/line and the minimal required fix.

## Boundary

This review must not authorize v2.8 release, public speedup claims, RT-core claims, true-zero-copy claims, hidden dispatch, automatic partner selection, or app-specific engine logic. It is an internal preview review only.
