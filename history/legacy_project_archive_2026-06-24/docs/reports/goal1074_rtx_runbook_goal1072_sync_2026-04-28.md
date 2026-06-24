# Goal1074 RTX Runbook Goal1072 Sync

Date: 2026-04-28

## Scope

This goal updates the paid RTX cloud runbook after Goal1071 scale-up evidence
and the Goal1072/Goal1073 local planning work.

## Changes

- The current primary pod runner is now
  `scripts/goal1072_post_scale_up_rtx_pod_batch_runner.sh`.
- The active pod rows are the two remaining facility/robot rows only:
  `facility_knn_assignment / coverage_threshold_prepared` and
  `robot_collision_screening / prepared_pose_flags`.
- The timing scales are the Goal1071 scales that crossed the 100 ms review
  floor: 2,500,000 facility copies and 36,000,000 robot poses.
- Barnes-Hut is explicitly absent from the current runner and remains blocked
  for benchmark-contract redesign because the current one-level four-node
  contract is not a meaningful RTX traversal benchmark.
- The runbook now instructs local regeneration of Goal1072 and Goal1073 before
  cloud start and Goal1073 intake after artifact copyback.

## Boundary

This is documentation/runbook synchronization only. It does not run cloud,
create resources, authorize release, change public wording, or authorize public
RTX speedup claims.

## Verification

Ran:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1072_post_scale_up_rtx_pod_batch_test \
  tests.goal1073_goal1072_artifact_intake_test \
  tests.goal829_rtx_cloud_single_session_runbook_test
```

Result: 18 tests OK.
