# External Review Handoff: Goal3572 Grouped i64 Full-Reduction Fast Path

Date: 2026-06-06

## Task

Please perform an independent review of Goal3572, the app-agnostic grouped-i64
small-group fast-path extension after the v2.9 internal closeout.

Write your review to one of these paths:

- Claude: `docs/reviews/goal3573_claude_review_goal3572_grouped_i64_fastpath_2026-06-06.md`
- Gemini: `docs/reviews/goal3574_gemini_review_goal3572_grouped_i64_fastpath_2026-06-06.md`

Use one of the allowed verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

## Primary Files To Read

- `docs/reports/goal3572_grouped_i64_full_reduction_fastpath_2026-06-06.md`
- `docs/reports/goal3572_grouped_i64_full_reduction_fastpath_preserve_long_a5000/summary.json`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `scripts/goal3572_grouped_i64_full_reduction_fastpath_probe.py`
- `tests/goal3572_grouped_i64_full_reduction_fastpath_a5000_test.py`
- `tests/goal3572_grouped_i64_small_group_full_reduction_fastpath_test.py`
- `tests/goal3564_grouped_i64_small_group_sum_fastpath_test.py`

## Context

v2.9 closed internally at commit `f5090057` with a generic grouped-i64
small-group fast path for `sum` and `sum_count`. Goal3572 expands the same
generic primitive family so small dense groups also use shared-memory reduction
for `count`, `min`, `max`, and `stats`.

The final implementation deliberately keeps the original
`device_column_grouped_i64_small_group_kernel` path for `sum` and `sum_count`,
and adds `device_column_grouped_i64_small_group_reduction_kernel` for the new
operations. This avoided earlier branch-heavy generalized-kernel regressions.
The native selector also structurally covers `stats`, but the RayDB-style probe
does not expose a separate fused stats mode; do not treat this packet as a
measured stats speedup claim.

Final committed evidence is from an RTX A5000 pod:

- baseline commit: `f5090057`
- candidate commit: `bfcb943c`
- candidate native dirty: `false`
- copies: `120000`
- warmup: `3`
- repeat: `5000`
- trials: `5`
- all modes correct: `true`
- geomean speedup: `1.157044x`
- median speedup: `1.245297x`

Per-mode speedups:

- `count`: `1.324430x`
- `min`: `1.245297x`
- `max`: `1.263298x`
- `avg_as_sum_count`: `1.007569x`
- `sum`: `0.987797x`

The report intentionally treats `sum` as preserved near parity, not as a new
speedup claim.

## Review Questions

1. Does the native implementation remain app-agnostic, with no RayDB/database
   vocabulary or app-specific branch in the engine?
2. Is the split-kernel design justified by the evidence and by the need to
   preserve the old sum/sum-count hot path?
3. Is the A5000 artifact clean enough for internal engineering evidence
   despite the near-parity `sum` row?
4. Does the report avoid overclaiming, especially around release/public
   speedup/broad RT-core/whole-app/zero-copy claims?
5. Are there any required fixes before this goal can be considered internally
   closed?

## Boundary

This is an internal primitive-performance goal only. It must not authorize:

- release or tag action;
- public speedup claims;
- whole-app acceleration claims;
- broad RT-core speedup claims;
- true zero-copy claims;
- paper reproduction claims;
- package-install claims.
