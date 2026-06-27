# Goal754 Windows Review: OptiX Robot Pose-Flags Performance Plan

## Verdict

ACCEPT_WITH_NOTES.

The plan is fair and useful, and it has the required 2+ AI consensus shape: Mac/Linux reports Gemini Flash `ACCEPT`, and this is an independent Windows Codex review. I do not see a blocker. The main refinements are to make pose-flag validation exact, keep pose-index construction out of the native execute timing, and document that GTX 1070 results are correctness/whole-call evidence only.

## Reviewed Inputs

- Request: `Z:\extra-1\rtdl_codex_bridge\to_windows\GOAL754_WINDOWS_REVIEW_OPTIX_POSE_FLAGS_PERF_PLAN.md`
- Referenced Mac/Linux plan: `/Users/rl2025/rtdl_python_only/docs/reports/goal754_optix_robot_pose_flags_perf_plan_2026-04-21.md`
- Prior Windows context: Goal753 candidate review reply and scratch checkout `C:\Users\Lestat\rtdl_goal753_pose_flags_review`
- Second AI signal: Gemini Flash review reported in the request as `ACCEPT`

No commit or push was made.

## Review Answers

1. The comparison is fair and useful if each backend's output shape is labeled clearly. Comparing Embree rows, OptiX rows, OptiX prepared scalar count, and OptiX prepared pose flags should expose the intended distinction: row materialization cost versus native app-summary outputs.
2. Pose-flag correctness should compare exact pose flags and the derived count. Counts alone are insufficient because two wrong poses can preserve the same count. The harness should report at least `matches_oracle_pose_flags`, `oracle_colliding_pose_ids`, `colliding_pose_ids`, `colliding_pose_count`, and `oracle_colliding_pose_count`.
3. The planned phases are good, but I recommend one explicit additional phase or field for `pose_index_construction`. The pose-index tuple/dense mapping is app-side summary preparation, not OptiX traversal. Keeping it separate from `native_execute` will make the prepared pose-flags timing easier to interpret.
4. The no-RTX-speedup boundary is sufficient if it appears in both the JSON payload and any written report. Suggested wording: GTX 1070 validates OptiX traversal correctness and whole-call behavior, but does not support RTX RT-core speedup claims.
5. Missing tests/docs to include in the planned goal: `--list-backends` includes `optix_prepared_pose_flags`; portable non-OptiX or missing-OptiX path records `skipped_or_failed` instead of failing unless `--strict` is set; small CPU-validating case verifies exact pose flags and count for `optix_prepared_pose_flags` when native OptiX is available; public/closure report states that prepared pose flags omit edge-level witnesses and hit-ray IDs.

## Notes Applied

- The Goal754 harness now compares exact pose IDs for `optix_prepared_pose_flags` when oracle validation is enabled.
- The harness records `pose_index_construction_sec` separately from native execute timing.
- The JSON payload and written report keep the GTX 1070 no-RT-core boundary.

## Blockers

None.
