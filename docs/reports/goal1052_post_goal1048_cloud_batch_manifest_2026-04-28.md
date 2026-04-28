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
| `prepared_pose_flags` | `robot_collision_screening` | `python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py --mode optix --pose-count 200000 --obstacle-count 1024 --iterations 10 --input-mode packed_arrays --result-mode pose_count --output-json docs/reports/goal1052_post_goal1048_cloud_batch/prepared_pose_flags.json` |

## Same-Semantics Review Candidates

| Path | App | Command |
| --- | --- | --- |
| `prepared_db_session_sales_risk` | `database_analytics` | `python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario sales_risk --copies 20000 --iterations 10 --output-mode compact_summary --strict --output-json docs/reports/goal1052_post_goal1048_cloud_batch/prepared_db_session_sales_risk.json` |
| `prepared_db_session_regional_dashboard` | `database_analytics` | `python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario regional_dashboard --copies 20000 --iterations 10 --output-mode compact_summary --strict --output-json docs/reports/goal1052_post_goal1048_cloud_batch/prepared_db_session_regional_dashboard.json` |
| `graph_visibility_edges_gate` | `graph_analytics` | `python3 scripts/goal889_graph_visibility_optix_gate.py --copies 20000 --output-mode summary --validation-mode analytic_summary --chunk-copies 0 --strict --output-json docs/reports/goal1052_post_goal1048_cloud_batch/graph_visibility_edges_gate.json` |
| `prepared_count_summary` | `event_hotspot_screening` | `python3 scripts/goal811_spatial_optix_summary_phase_profiler.py --scenario event_hotspot_screening --mode optix --copies 20000 --output-json docs/reports/goal1052_post_goal1048_cloud_batch/prepared_count_summary.json` |
| `road_hazard_native_summary_gate` | `road_hazard_screening` | `python3 scripts/goal933_prepared_segment_polygon_optix_profiler.py --scenario road_hazard_prepared_summary --copies 20000 --iterations 5 --mode run --output-json docs/reports/goal1052_post_goal1048_cloud_batch/road_hazard_native_summary_gate.json` |
| `polygon_pair_overlap_optix_native_assisted_phase_gate` | `polygon_pair_overlap_area_rows` | `python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app pair_overlap --mode optix --copies 20000 --output-mode summary --validation-mode analytic_summary --chunk-copies 100 --output-json docs/reports/goal1052_post_goal1048_cloud_batch/polygon_pair_overlap_optix_native_assisted_phase_gate.json` |
| `polygon_set_jaccard_optix_native_assisted_phase_gate` | `polygon_set_jaccard` | `python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode optix --copies 20000 --output-mode summary --validation-mode analytic_summary --chunk-copies 20 --output-json docs/reports/goal1052_post_goal1048_cloud_batch/polygon_set_jaccard_optix_native_assisted_phase_gate.json` |
| `directed_threshold_prepared` | `hausdorff_distance` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario hausdorff_threshold --mode optix --copies 20000 --iterations 10 --radius 0.4 --output-json docs/reports/goal1052_post_goal1048_cloud_batch/directed_threshold_prepared.json` |
| `node_coverage_prepared` | `barnes_hut_force_app` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario barnes_hut_node_coverage --mode optix --body-count 200000 --iterations 10 --radius 10.0 --output-json docs/reports/goal1052_post_goal1048_cloud_batch/node_coverage_prepared.json` |

## Summary

- diagnostic reruns: `2`
- same-semantics review candidates: `9`
- total commands after bootstrap: `11`
- diagnostic rows with skip-validation: `[]`
- duplicate output JSON paths: `[]`

## Boundary

This manifest prepares cloud execution only. It does not run cloud, authorize release, or authorize new public RTX speedup wording.
