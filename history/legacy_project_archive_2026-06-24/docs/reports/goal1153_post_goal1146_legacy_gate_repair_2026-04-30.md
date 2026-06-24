# Goal1153 Post-Goal1146 Legacy Gate Repair

Date: 2026-04-30

## Summary

Goal1153 repairs legacy local gates that still encoded pre-Goal1146 public RTX wording state.

Current truth after Goal1146:

- `facility_knn_assignment` is `public_wording_reviewed`.
- `barnes_hut_force_app` is `public_wording_reviewed`.
- `robot_collision_screening` remains `public_wording_blocked`.
- Robot public wording is blocked pending same-total-work or explicitly normalized-baseline review; it is not blocked merely because of the older generic 100 ms timing-floor phrase.

## Changes

- Updated Goal1051, Goal1052, Goal1053, Goal1056, Goal1062, Goal1063, Goal1065, and Goal1125 gates to match the current 9 reviewed / 1 blocked / 6 not-reviewed public RTX wording state.
- Reduced Goal1062 blocked rerun scope from facility plus robot to robot only.
- Updated Goal1065 artifact intake to require one robot validation artifact and one robot large-timing artifact.
- Updated older robot-boundary assertions in Goal971 to expect the current normalized-baseline boundary.
- Updated Goal808 road-hazard native-mode propagation test to mock the current prepared OptiX hit-count API.
- Updated Goal979 CPU timing repair dry-run to treat current Barnes-Hut summary diagnostics as a superset of the saved historical artifact summary.
- Updated Goal1022 refresh-context check so it verifies stable operating-memory rules, not release/version facts that do not belong in `REFRESH_LOCAL`.

## Regenerated Current Artifacts

- `docs/reports/goal1051_post_goal1048_followup_plan_2026-04-28.json`
- `docs/reports/goal1051_post_goal1048_followup_plan_2026-04-28.md`
- `docs/reports/goal1052_post_goal1048_cloud_batch_manifest_2026-04-28.json`
- `docs/reports/goal1052_post_goal1048_cloud_batch_manifest_2026-04-28.md`
- `docs/reports/goal1053_post_goal1048_cloud_batch_runner_2026-04-28.json`
- `scripts/goal1053_post_goal1048_cloud_batch_runner.sh`
- `docs/reports/goal1062_blocked_rtx_wording_rerun_manifest_2026-04-28.json`
- `docs/reports/goal1062_blocked_rtx_wording_rerun_manifest_2026-04-28.md`
- `scripts/goal1062_blocked_rtx_wording_rerun_runner.sh`
- `docs/reports/goal1063_pre_pod_local_completion_audit_2026-04-28.json`
- `docs/reports/goal1063_pre_pod_local_completion_audit_2026-04-28.md`
- `docs/reports/goal1065_goal1062_artifact_intake_2026-04-28.json`
- `docs/reports/goal1065_goal1062_artifact_intake_2026-04-28.md`
- `docs/reports/goal1125_unresolved_rtx_public_wording_prioritization_2026-04-29.json`
- `docs/reports/goal1125_unresolved_rtx_public_wording_prioritization_2026-04-29.md`
- `docs/reports/goal1022_history_release_drift_audit_2026-04-26.json`
- `docs/reports/goal1022_history_release_drift_audit_2026-04-26.md`

## Verification

Focused repaired gate suite:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1005_post_a5000_speedup_candidate_audit_test tests.goal1007_larger_scale_rtx_repeat_plan_test tests.goal971_post_goal969_baseline_speedup_review_package_test tests.goal1051_post_goal1048_followup_plan_test tests.goal1052_post_goal1048_cloud_batch_manifest_test tests.goal1053_post_goal1048_cloud_batch_runner_test tests.goal1056_post_goal1048_artifact_intake_test tests.goal1062_blocked_rtx_wording_rerun_manifest_test tests.goal1063_pre_pod_local_completion_audit_test tests.goal1125_unresolved_rtx_public_wording_prioritization_test tests.goal808_segment_polygon_app_native_mode_propagation_test tests.goal979_deferred_cpu_timing_repair_test tests.goal1022_history_release_drift_audit_test -v
```

Result:

```text
Ran 46 tests in 8.593s
OK
```

Full discovery:

```text
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py' -q
```

Result:

```text
Ran 2222 tests in 416.524s
OK (skipped=196)
```

## Boundary

This goal repairs stale local gates and regenerated current artifacts. It does not run cloud, authorize release, authorize new public RTX speedup wording, or change the current robot public-wording block.
