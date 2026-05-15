# Goal2026 External Review Task

Please perform an independent read-only review of:

- `docs/reports/goal2026_all_app_v18_v2_pod_comparison_2026-05-14.md`
- `docs/reports/goal2026_all_app_v18_v2_pod_comparison_2026-05-14.json`
- `docs/reports/goal2026_all_app_v18_v2_pod_comparison_936aff2f_retry2/`
- `tests/goal2026_all_app_v18_v2_pod_comparison_test.py`

Questions:

1. Does Goal2026 honestly distinguish fresh pod reruns from latest accepted
   matrix evidence?
2. Are the v1.8 vs v2.0 ratios copied and interpreted correctly?
3. Does it correctly preserve the fixed-radius PTX blocker and segment
   capacity-overflow diagnostic instead of hiding them?
4. Does it avoid overclaiming v2.0 release authorization, whole-app speedup,
   broad RT-core speedup, package install, or unbounded domain solver claims?
5. Is the conclusion fair: v2.0 has all-app positive or bounded-positive
   evidence, but final release still needs final packet/gate/consensus?

Write the review to:

`docs/reviews/goal2027_gemini_review_goal2026_all_app_perf_comparison_2026-05-14.md`

Use one of these verdicts exactly: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

Do not edit source files other than the requested review file.
