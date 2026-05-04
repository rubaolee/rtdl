# Goal1052 Post-Goal1048 Cloud Batch Manifest

Date: 2026-04-28

Valid: `True`

This manifest prepares cloud execution only. It does not run cloud, authorize release, or authorize new public RTX speedup wording.

## Policy

Do not start or stop a cloud pod per app. Run this as one batched session, copy artifacts after each row or small group, and stop the pod before local review.

## Bootstrap

`python3 scripts/goal763_rtx_cloud_bootstrap_check.py --output-json docs/reports/goal1052_post_goal1048_cloud_batch/goal763_rtx_cloud_bootstrap_check.json`

## Diagnostic Validation Reruns

| Path | App | Command |
| --- | --- | --- |
| `coverage_threshold_prepared` | `facility_knn_assignment` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario facility_service_coverage --mode optix --copies 20000 --iterations 10 --radius 1.0 --output-json docs/reports/goal1052_post_goal1048_cloud_batch/coverage_threshold_prepared.json` |
| `prepared_pose_flags` | `robot_collision_screening` | `python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py --mode optix --pose-count 4096 --obstacle-count 256 --iterations 3 --input-mode python_objects --result-mode pose_flags --output-json docs/reports/goal1052_post_goal1048_cloud_batch/prepared_pose_flags.json` |

## Same-Semantics Review Candidates

| Path | App | Command |
| --- | --- | --- |
| `prepared_db_session_sales_risk` | `database_analytics` | `python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario sales_risk --copies 20000 --iterations 10 --output-mode compact_summary --strict --output-json docs/reports/goal1052_post_goal1048_cloud_batch/prepared_db_session_sales_risk.json` |
| `prepared_db_session_regional_dashboard` | `database_analytics` | `python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario regional_dashboard --copies 20000 --iterations 10 --output-mode compact_summary --strict --output-json docs/reports/goal1052_post_goal1048_cloud_batch/prepared_db_session_regional_dashboard.json` |
| `polygon_set_jaccard_optix_native_assisted_phase_gate` | `polygon_set_jaccard` | `python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode optix --copies 20000 --output-mode summary --validation-mode analytic_summary --chunk-copies 20 --output-json docs/reports/goal1052_post_goal1048_cloud_batch/polygon_set_jaccard_optix_native_assisted_phase_gate.json` |

## Summary

- diagnostic reruns: `2`
- same-semantics review candidates: `3`
- total commands after bootstrap: `5`
- diagnostic rows with skip-validation: `[]`
- duplicate output JSON paths: `[]`

## Boundary

This manifest prepares cloud execution only. It does not run cloud, authorize release, or authorize new public RTX speedup wording.
