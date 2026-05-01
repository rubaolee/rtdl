# Goal1141 RTX Single-Session Pod Bundle

Date: 2026-04-29

Valid: `true`

Goal1141 prepares one consolidated RTX pod session for Goal1116 current-source reruns plus Goal1135 changed-path artifacts. It does not create cloud resources, does not run cloud locally, does not authorize release, and does not authorize public RTX speedup or broad whole-app acceleration claims.

## Cloud Policy

Run this bundle only after a pod is already running. Do not start/stop a pod per app. The generated shell keeps going after individual entry failures, writes a status TSV, and asks for copying back the whole report directory before stopping the pod.

## Setup Commands

- `bash -lc 'apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y libgeos-dev pkg-config'`
- `python3 scripts/goal763_rtx_cloud_bootstrap_check.py --skip-tests --output-json docs/reports/goal1141_rtx_single_session_bundle/bootstrap_preflight.json`
- `python3 scripts/goal763_rtx_cloud_bootstrap_check.py --output-json docs/reports/goal1141_rtx_single_session_bundle/bootstrap_full.json`

## Entries

| Label | Source | App | Output | Command |
| --- | --- | --- | --- | --- |
| `goal1116_facility_knn_assignment_same_scale_validation_and_timing` | `goal1116` | `facility_knn_assignment` | `docs/reports/goal1116_current_source_rtx_rerun_packet/facility_recentered_coverage_threshold_2_5m_optix_validation.json` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario facility_service_coverage_recentered --mode optix --copies 2500000 --iterations 5 --radius 1.0 --output-json docs/reports/goal1116_current_source_rtx_rerun_packet/facility_recentered_coverage_threshold_2_5m_optix_validation.json` |
| `goal1116_robot_collision_screening_correctness_validation` | `goal1116` | `robot_collision_screening` | `docs/reports/goal1116_current_source_rtx_rerun_packet/robot_prepared_pose_flags_validation.json` | `python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py --mode optix --pose-count 4096 --obstacle-count 256 --iterations 3 --input-mode python_objects --result-mode pose_flags --output-json docs/reports/goal1116_current_source_rtx_rerun_packet/robot_prepared_pose_flags_validation.json` |
| `goal1116_robot_collision_screening_large_timing_repeat` | `goal1116` | `robot_collision_screening` | `docs/reports/goal1116_current_source_rtx_rerun_packet/robot_prepared_pose_flags_8m_timing.json` | `python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py --mode optix --pose-count 8000000 --obstacle-count 4096 --iterations 7 --input-mode packed_arrays --result-mode pose_count --skip-validation --output-json docs/reports/goal1116_current_source_rtx_rerun_packet/robot_prepared_pose_flags_8m_timing.json` |
| `goal1116_barnes_hut_force_app_correctness_validation` | `goal1116` | `barnes_hut_force_app` | `docs/reports/goal1116_current_source_rtx_rerun_packet/barnes_hut_depth8_4096_validation.json` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario barnes_hut_node_coverage --mode optix --body-count 4096 --iterations 3 --radius 0.1 --barnes-tree-depth 8 --hit-threshold 4 --output-json docs/reports/goal1116_current_source_rtx_rerun_packet/barnes_hut_depth8_4096_validation.json` |
| `goal1116_barnes_hut_force_app_large_timing_repeat` | `goal1116` | `barnes_hut_force_app` | `docs/reports/goal1116_current_source_rtx_rerun_packet/barnes_hut_depth8_20m_timing.json` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario barnes_hut_node_coverage --mode optix --body-count 20000000 --iterations 3 --radius 0.1 --barnes-tree-depth 8 --hit-threshold 4 --skip-validation --output-json docs/reports/goal1116_current_source_rtx_rerun_packet/barnes_hut_depth8_20m_timing.json` |
| `goal1135_database_analytics_compact_summary` | `goal1135` | `database_analytics` | `docs/reports/goal1135_changed_path_rtx_pod/database_analytics_compact_summary.json` | `python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario all --copies 20000 --iterations 5 --output-mode compact_summary --strict --output-json docs/reports/goal1135_changed_path_rtx_pod/database_analytics_compact_summary.json` |
| `goal1135_graph_visibility_edges_gate` | `goal1135` | `graph_analytics` | `docs/reports/goal1135_changed_path_rtx_pod/graph_visibility_edges_gate.json` | `python3 scripts/goal889_graph_visibility_optix_gate.py --copies 20000 --output-mode summary --validation-mode analytic_summary --chunk-copies 0 --strict --output-json docs/reports/goal1135_changed_path_rtx_pod/graph_visibility_edges_gate.json` |
| `goal1135_road_hazard_native_summary_count` | `goal1135` | `road_hazard_screening` | `docs/reports/goal1135_changed_path_rtx_pod/road_hazard_native_summary_count.json` | `python3 scripts/goal888_road_hazard_native_optix_gate.py --copies 20000 --output-mode summary --strict --output-json docs/reports/goal1135_changed_path_rtx_pod/road_hazard_native_summary_count.json` |
| `goal1135_polygon_pair_overlap_phase_gate` | `goal1135` | `polygon_pair_overlap_area_rows` | `docs/reports/goal1135_changed_path_rtx_pod/polygon_pair_overlap_phase_gate.json` | `python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app pair_overlap --mode optix --copies 20000 --output-mode summary --validation-mode analytic_summary --chunk-copies 20 --output-json docs/reports/goal1135_changed_path_rtx_pod/polygon_pair_overlap_phase_gate.json` |
| `goal1135_polygon_set_jaccard_phase_gate` | `goal1135` | `polygon_set_jaccard` | `docs/reports/goal1135_changed_path_rtx_pod/polygon_set_jaccard_phase_gate.json` | `python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode optix --copies 20000 --output-mode summary --validation-mode analytic_summary --chunk-copies 20 --output-json docs/reports/goal1135_changed_path_rtx_pod/polygon_set_jaccard_phase_gate.json` |
| `goal1135_hausdorff_threshold_phase_gate` | `goal1135` | `hausdorff_distance` | `docs/reports/goal1135_changed_path_rtx_pod/hausdorff_threshold_phase_gate.json` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario hausdorff_threshold --mode optix --copies 20000 --iterations 5 --radius 0.4 --output-json docs/reports/goal1135_changed_path_rtx_pod/hausdorff_threshold_phase_gate.json` |

## Boundary

Goal1141 prepares one consolidated RTX pod session for Goal1116 current-source reruns plus Goal1135 changed-path artifacts. It does not create cloud resources, does not run cloud locally, does not authorize release, and does not authorize public RTX speedup or broad whole-app acceleration claims.

