# Goal1074 Claude Review

Date: 2026-04-28
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **ACCEPT**

## Scope

Review of Goal1074 runbook sync: whether `docs/rtx_cloud_single_session_runbook.md`
correctly transitions the primary pod procedure from Goal1068 to Goal1072/Goal1073,
enforces facility 2.5M and robot 36M scales, excludes Barnes-Hut pending
benchmark-contract redesign, preserves no-public-speedup-claim boundaries, and
is backed by adequate tests.

---

## Findings

### 1. Primary pod path switch — PASS

The runbook introduces a dedicated "Current Post-Goal1072 Runner" section
(beginning at the heading on line 139) that explicitly instructs:

> "prefer the generated Goal1072 runner over the older Goal1068, Goal1053, or
> Goal759/Goal761 grouped paths"

The runner entry point is `bash scripts/goal1072_post_scale_up_rtx_pod_batch_runner.sh`.
Goal1068 is retained only as a historical reference and is explicitly superseded:
"Goal1071 superseded the Goal1068 facility/robot timing scales." The older
OOM-safe A–H groups are retained for historical fallback but are not the stated
current procedure.

`test_runbook_prefers_goal1072_for_current_post_goal1072_batch` (test line 40)
verifies the key phrases, including the supersession statement.

### 2. Scale values: facility 2.5M and robot 36M — PASS

The runbook states at the active-row list:

- "large timing-repeat `facility_knn_assignment / coverage_threshold_prepared` at **2,500,000 copies**"
- "large timing-repeat `robot_collision_screening / prepared_pose_flags` at **36,000,000 poses**"

The Goal1072 planning report confirms the exact commands: `--copies 2500000` for
facility and `--pose-count 36000000` for robot. The test asserts both strings
(`"2,500,000 copies"`, `"36,000,000 poses"`). The correctness-validation rows
correctly remain at smaller scales (20,000 copies / 4,096 poses) with
`skip_validation=False`.

### 3. Barnes-Hut exclusion — PASS

The runbook states:

> "Barnes-Hut is intentionally absent from the Goal1072 runner and remains
> blocked for benchmark-contract redesign."

The reason is grounded in Goal1071 evidence: the current four-node contract
yields a 0.004 s median RT query that measures input construction rather than
RTX traversal. The Goal1072 planning report lists Barnes-Hut as
`blocked_contract_reframe_required` with an explicit next-move instruction.
The Goal1073 intake echoes the same exclusion. The test checks both
`"Barnes-Hut is intentionally absent"` and `"blocked\nfor benchmark-contract redesign"`.

### 4. No-public-speedup-claim boundaries — PASS

All three documents (runbook, Goal1072 report, Goal1073 intake) carry explicit
boundary statements:

- Runbook "Claim Boundary" section: "This runbook collects evidence. It does
  not authorize public RTX speedup claims."
- Goal1072 report and Goal1073 intake both carry matching boundary language.
- Goal1073 intake: `public speedup claims authorized: 0`.
- The two large timing rows are marked `skip_validation=True` and the runbook
  instructs that those rows "require separate validation rows plus later review"
  before any claim authorization.
- The `REFRESH_LOCAL_2026-04-13.md` handoff confirms public RTX wording remains
  blocked and must follow `rtdsl.rtx_public_wording_matrix()`. The runbook is
  consistent with that boundary.

The test asserts `"does not authorize public RTX speedup claims"`.

### 5. Test adequacy — PASS

`tests/goal829_rtx_cloud_single_session_runbook_test.py` contains 8 test methods:

| Test | Coverage |
|---|---|
| `test_runbook_enforces_local_readiness_before_pod` | All prerequisite scripts (goal824, goal1025, goal1026, goal1062, goal1063, goal1067, goal1072, goal1073), manifest counts, valid-gate string |
| `test_runbook_prefers_goal1072_for_current_post_goal1072_batch` | Goal1072 primacy, runner script name, four active rows, scale values, Barnes-Hut absence, skip-validation guard, copyback instruction, Goal1068 supersession, Hausdorff block |
| `test_runbook_uses_bootstrap_and_artifact_audit` | Bootstrap, ABI version note, OptiX headers, RTDL_SOURCE_COMMIT chain |
| `test_runbook_has_deferred_batch_controls_and_shutdown_rule` | All 9 deferred apps, shutdown rule, claim boundary |
| `test_runbook_prefers_oom_safe_groups_and_targeted_retry` | All 8 OOM-safe groups A–H, density_count/core_count interpretation guard |
| `test_group_g_uses_validated_manifest_commands` | Group G skip-validation prohibition |
| `test_segment_polygon_group_uses_current_prepared_gates` | Prepared segment/polygon gate names |
| `test_prepared_db_optix_launch_has_traversal_start_timer` | C++ timing bracket in optix workloads |

The Goal1074 self-report records 17 tests OK across the three suites
(goal1072, goal1073, goal829). Coverage is tight and specific to the critical
boundaries. No gaps observed for the criteria under review.

---

## Summary

All five review criteria are satisfied. The runbook cleanly moves the primary
pod procedure to Goal1072/Goal1073, encodes the correct scale-up values from
Goal1071, explicitly excludes Barnes-Hut with a grounded reason and next-move
instruction, and preserves the no-public-speedup-claim boundary consistently
across the runbook, planning report, and intake report. Tests are specific and
comprehensive for the changed section.

**Verdict: ACCEPT**
