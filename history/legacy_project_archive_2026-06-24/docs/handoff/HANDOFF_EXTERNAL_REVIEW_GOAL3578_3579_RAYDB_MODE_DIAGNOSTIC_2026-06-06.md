# External Review Handoff: Goal3578/3579 RayDB Grouped-i64 Mode Diagnostic

Date: 2026-06-06

Please perform an independent read-only review of the Goal3578 and Goal3579
chain.

## Scope

Review these files:

- `docs/reports/goal3578_raydb_grouped_i64_mode_reprobe_2026-06-06.md`
- `docs/reports/goal3578_raydb_grouped_i64_mode_reprobe_current_a5000/*.json`
- `tests/goal3578_raydb_grouped_i64_mode_reprobe_test.py`
- `docs/reports/goal3579_raydb_fused_stats_vs_separate_reductions_2026-06-06.md`
- `tests/goal3579_raydb_fused_stats_vs_separate_reductions_test.py`
- `examples/v2_0/research_benchmarks/raydb_style/README.md`

## Questions

1. Does Goal3578 correctly diagnose the Goal3575 tiny all-mode smoke as
   integration-only evidence rather than a native `count`/`sum` regression?
2. Do the Goal3578 A5000 artifacts support the stated current-head long-run
   medians and one-native-launch rows for all six modes?
3. Does Goal3579 correctly compute the fused `stats` vs separate
   `count`+`sum`+`min`+`max` ratio as `3.604830411x` from the Goal3578
   artifacts?
4. Is the README recommendation sound: use fused `stats` when the user needs
   `count`, `sum`, `min`, and `max` together, while keeping separate modes for
   single-output queries and diagnostics?
5. Do the reports avoid unauthorized release, public-speedup, whole-app,
   broad-RT-core, true-zero-copy, paper-reproduction, and package-install
   claims?

## Output

Write the review to:

- Claude: `docs/reviews/goal3580_claude_review_goal3578_3579_raydb_mode_diagnostic_2026-06-06.md`
- Gemini: `docs/reviews/goal3581_gemini_review_goal3578_3579_raydb_mode_diagnostic_2026-06-06.md`

Use one of the allowed verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

This review does not authorize release action or public claims.
