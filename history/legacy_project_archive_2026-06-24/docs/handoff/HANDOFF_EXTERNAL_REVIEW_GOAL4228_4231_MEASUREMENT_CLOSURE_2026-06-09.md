# External Review Request: Goals4228-4231 Measurement Closure

Date: 2026-06-09

Reviewer role: independent Claude/Gemini reviewer, distinct from Codex authoring.

Please review the Goal4228-4231 measurement-closure chain and write your review
to one of these paths:

- Claude: `docs/reviews/goal4232_claude_review_goal4228_4231_measurement_closure_2026-06-09.md`
- Gemini: `docs/reviews/goal4233_gemini_review_goal4228_4231_measurement_closure_2026-06-09.md`

Use one of these verdicts only: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

## Scope

Review these artifacts:

- `examples/v2_0/apps/simulation/rtdl_barnes_hut_force_app.py`
- `docs/reports/goal4228_rtdbscan_long_repeat_measurement_2026-06-09.md`
- `docs/reports/goal4228_rtdbscan_long_repeat_rtx4000ada/summary.json`
- `docs/reports/goal4229_barnes_hut_force_summary_aggregate_timing_2026-06-09.md`
- `docs/reports/goal4229_barnes_hut_numba_long_repeat_rtx4000ada/summary.json`
- `docs/reports/goal4230_ten_app_measurement_adequacy_closure_2026-06-09.md`
- `src/rtdsl/current_major_performance_targets.py`
- `docs/reports/goal4231_major_performance_target_map_after_measurement_closure_2026-06-09.md`
- `tests/goal4228_rtdbscan_long_repeat_measurement_test.py`
- `tests/goal4229_barnes_hut_force_summary_aggregate_timing_test.py`
- `tests/goal4230_ten_app_measurement_adequacy_closure_test.py`
- `tests/goal4219_major_performance_target_map_test.py`

## Questions To Answer

1. Does Goal4228 legitimately close the RT-DBSCAN hot-path measurement-floor gap without changing the route policy or overclaiming?
2. Does Goal4229 correctly harden Barnes-Hut force-summary timing by exposing real aggregate timing fields rather than relying on median-times-repeat proxy evidence?
3. Does Goal4230 accurately show that all ten promoted benchmark apps now have at least one second-level measurement source above the one-second hot-path or representative-profile floor?
4. Does Goal4231 update the major performance target map honestly: measurement adequacy is internally closed, while release action, public claims, docs audit, consensus, and AMD/HIPRT hardware evidence remain unapproved or pending?
5. Are the tests strong enough to catch measurement-floor regressions and claim-boundary leakage?
6. What should be the next major engineering target before any user-requested formal release packet?

## Required Boundary

This review must not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, paper-reproduction wording,
true-zero-copy wording, automatic partner selection, AMD performance wording, or
app-specific native-engine logic.

Recommended verdict if you find no defect: `accept-with-boundary`, because this
is internal measurement-readiness evidence, not release authorization.
