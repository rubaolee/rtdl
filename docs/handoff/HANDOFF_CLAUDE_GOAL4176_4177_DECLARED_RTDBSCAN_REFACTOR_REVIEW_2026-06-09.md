# Handoff: Review Goal4176/4177 Declared RTDBSCAN Refactor

Please perform a read-only external review of the current `main` branch after
Goal4176 and Goal4177.

## Files To Inspect

- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `scripts/goal4177_rt_dbscan_declared_all_items_direct_status_probe.py`
- `tests/goal4172_declared_all_predicate_rtdbscan_route_test.py`
- `tests/goal4176_declared_rtdbscan_all_items_direct_status_refactor_test.py`
- `tests/goal4177_rt_dbscan_declared_all_items_direct_status_probe_runner_test.py`
- `docs/reports/goal4176_declared_rtdbscan_all_items_direct_status_refactor_2026-06-09.md`
- Existing context:
  - `docs/reports/goal4173_declared_all_predicate_rtdbscan_2m_probe_2026-06-09.md`
  - `docs/reviews/goal4174_claude_review_goal4172_4173_declared_rtdbscan_2026-06-09.md`
  - `docs/reviews/goal4174_gemini_review_goal4172_4173_declared_rtdbscan_2026-06-09.md`

## Questions

1. Does Goal4176 correctly refactor the caller-declared all-predicate RTDBSCAN route from synthetic predicate/neighbor columns to the generic all-items direct-status component-signature primitive?
2. Does the declared route still preserve the external-proof boundary and avoid RT-count-threshold, broad RT-core, release, whole-app, and paper-reproduction claims?
3. Does the Goal4177 runner provide a reliable large-scale pod timing harness with progress markers and enough metadata to compare current grouped-stream, measured all-true predicate direct-status, and declared all-items direct-status?
4. Are there any machine-checkability, metadata, naming, or timing-boundary issues that should be fixed before pod timing evidence is accepted?
5. Does this work change the next major runtime direction for mixed-predicate RTDBSCAN, or should mixed rows remain blocked on a separate border-assignment/policy primitive?

## Requested Output

Write your review to:

`docs/reviews/goal4178_claude_review_goal4176_4177_declared_rtdbscan_refactor_2026-06-09.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

This is not a release authorization review.
