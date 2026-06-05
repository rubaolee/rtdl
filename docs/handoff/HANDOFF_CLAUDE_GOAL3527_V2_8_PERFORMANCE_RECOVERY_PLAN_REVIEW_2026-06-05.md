# Handoff: Claude Review For Goal3527 v2.8 Performance Recovery Plan

Please perform an independent review of:

`docs/reports/goal3527_v2_8_performance_recovery_and_promoted_path_plan_2026-06-05.md`

Write the review to:

`docs/reviews/goal3528_claude_review_goal3527_v2_8_performance_recovery_plan_2026-06-05.md`

## Context

The user rejected treating the Goal3524 same-runner table as a satisfying v2.8
performance outcome. The weak rows include Barnes-Hut 0.401x, Contact 0.973x,
RayDB count 0.987x, Robot 0.990x, Triangle 0.992x, and awkward small wins for
RayJoin/DBSCAN/RTNN/LibRTS. Goal3527 proposes a consensus gate before any more
implementation.

## Files To Read

- `docs/reports/goal3527_v2_8_performance_recovery_and_promoted_path_plan_2026-06-05.md`
- `docs/reports/goal3524_v2_8_vs_v2_3_same_runner_optix_results_2026-06-05.md`
- `docs/reports/goal3524_pod_artifacts/goal3524_compact_results.json`
- `docs/reviews/goal3526_gemini_review_goal3524_v2_8_vs_v2_3_same_runner_optix_results_2026-06-05.md`
- `tests/goal3527_v2_8_performance_recovery_plan_test.py`

## Review Questions

1. Is Goal3527 the right next engineering move after the disappointing
   same-runner table?
2. Is the two-table strategy correct: same-runner diagnostic plus promoted-v2.8
   optimized path table?
3. Are Barnes-Hut P0 and RayJoin P1 prioritized correctly?
4. Does the plan preserve RTDL's app-agnostic engine boundary and avoid
   app-specific native shortcuts?
5. Does it handle partner language correctly: CuPy where selected, no hidden
   PyTorch in current v2.8 performance paths?
6. What must change before implementation starts?

## Required Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Lead with findings by severity. Do not edit files other than the requested
review file.
