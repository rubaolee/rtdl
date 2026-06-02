# Handoff: Gemini Review For Goal3042 Active-Frontier Hausdorff Performance

Please perform an independent read-only review of Goal3042. This is a parallel
external review request; Claude may also be reviewing the same goal.

Read:

- `docs/handoff/HANDOFF_CLAUDE_GOAL3042_ACTIVE_FRONTIER_PERF_REVIEW_2026-06-02.md`
- `docs/reports/goal3042_point_group_active_frontier_witness_selection_2026-06-02.md`
- `docs/reports/goal3042_active_frontier_perf_a4000_2026-06-02.json`
- `tests/goal3042_point_group_active_frontier_witness_selection_test.py`

Also spot-check the source files named in the Claude handoff.

Review questions:

1. Does the native OptiX change remain generic and app-agnostic?
2. Do the Python app and lab preserve exact Hausdorff semantics and original
   input witness indices?
3. Are the A4000 timing ratios in the summary artifact correct?
4. Is the claim language properly bounded as internal v2.6 evidence rather
   than public release/speedup/true-zero-copy authorization?
5. What should Codex do next before a public Hausdorff RT-core performance
   claim?

Write your review to:

```text
docs/reviews/goal3043_gemini_review_goal3042_active_frontier_perf_2026-06-02.md
```

Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.
