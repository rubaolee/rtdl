# Handoff: Gemini Review For Goal3527 v2.8 Performance Recovery Plan

Please perform an independent review of:

`docs/reports/goal3527_v2_8_performance_recovery_and_promoted_path_plan_2026-06-05.md`

Write the review to:

`docs/reviews/goal3529_gemini_review_goal3527_v2_8_performance_recovery_plan_2026-06-05.md`

## Context

Goal3524's A5000 same-runner table is fair but not a satisfying v2.8
performance result. Goal3527 proposes the next engineering move before
implementation: keep Goal3524 as a diagnostic table, build a promoted-v2.8 path
table, and repair or classify weak rows, starting with Barnes-Hut.

## Files To Read

- `docs/reports/goal3527_v2_8_performance_recovery_and_promoted_path_plan_2026-06-05.md`
- `docs/reports/goal3524_v2_8_vs_v2_3_same_runner_optix_results_2026-06-05.md`
- `docs/reports/goal3524_pod_artifacts/goal3524_compact_results.json`
- `tests/goal3527_v2_8_performance_recovery_plan_test.py`

## Review Questions

1. Does this plan answer the user's concern that the current same-runner result
   is too weak to be the v2.8 story?
2. Is the distinction between diagnostic same-runner rows and promoted v2.8
   optimized rows clear?
3. Are the priorities correct: Barnes-Hut P0, RayJoin promoted-path evidence
   P1, then DBSCAN/RTNN/LibRTS/flat rows?
4. Does the plan keep the engine app-agnostic and partner choice explicit?
5. Does the plan avoid release/public speedup overclaiming?
6. What must be changed before Codex starts implementation?

## Required Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Do not edit files other than the requested review file.
