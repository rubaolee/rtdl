# Goal1116 Current-Source RTX Rerun Packet

Date: 2026-04-29

Valid: `true`

Goal1116 prepares current-source RTX reruns for Facility, Robot, and Barnes-Hut. It does not create cloud resources, does not run cloud locally, does not authorize release, does not change public wording, and does not authorize public RTX speedup claims.

## Preconditions

- Run only from an already-running RTX-class NVIDIA pod checkout.
- Use the current branch/commit containing Goal1114 and Goal1115.
- Build the OptiX backend before running the packet.
- Export RTDL_SOURCE_COMMIT or keep .rtdl_source_commit populated.
- Copy the whole report directory back before stopping or terminating the pod.
- Treat all outputs as evidence only until 2+ AI review and public wording review.

## Rows

| App | Path | Phase | Validation | Timing floor | Output | Command |
| --- | --- | --- | --- | ---: | --- | --- |
| `facility_knn_assignment` | `coverage_threshold_prepared_recentered` | `same_scale_validation_and_timing` | `True` | `0.100` | `docs/reports/goal1116_current_source_rtx_rerun_packet/facility_recentered_coverage_threshold_2_5m_optix_validation.json` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario facility_service_coverage_recentered --mode optix --copies 2500000 --iterations 5 --radius 1.0 --output-json docs/reports/goal1116_current_source_rtx_rerun_packet/facility_recentered_coverage_threshold_2_5m_optix_validation.json` |
| `robot_collision_screening` | `prepared_pose_flags` | `correctness_validation` | `True` | `` | `docs/reports/goal1116_current_source_rtx_rerun_packet/robot_prepared_pose_flags_validation.json` | `python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py --mode optix --pose-count 4096 --obstacle-count 256 --iterations 3 --input-mode python_objects --result-mode pose_flags --output-json docs/reports/goal1116_current_source_rtx_rerun_packet/robot_prepared_pose_flags_validation.json` |
| `robot_collision_screening` | `prepared_pose_flags` | `large_timing_repeat` | `False` | `0.100` | `docs/reports/goal1116_current_source_rtx_rerun_packet/robot_prepared_pose_flags_8m_timing.json` | `python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py --mode optix --pose-count 8000000 --obstacle-count 4096 --iterations 7 --input-mode packed_arrays --result-mode pose_count --skip-validation --output-json docs/reports/goal1116_current_source_rtx_rerun_packet/robot_prepared_pose_flags_8m_timing.json` |
| `barnes_hut_force_app` | `node_coverage_prepared_rich` | `correctness_validation` | `True` | `` | `docs/reports/goal1116_current_source_rtx_rerun_packet/barnes_hut_depth8_4096_validation.json` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario barnes_hut_node_coverage --mode optix --body-count 4096 --iterations 3 --radius 0.1 --barnes-tree-depth 8 --hit-threshold 4 --output-json docs/reports/goal1116_current_source_rtx_rerun_packet/barnes_hut_depth8_4096_validation.json` |
| `barnes_hut_force_app` | `node_coverage_prepared_rich` | `large_timing_repeat` | `False` | `0.100` | `docs/reports/goal1116_current_source_rtx_rerun_packet/barnes_hut_depth8_20m_timing.json` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario barnes_hut_node_coverage --mode optix --body-count 20000000 --iterations 3 --radius 0.1 --barnes-tree-depth 8 --hit-threshold 4 --skip-validation --output-json docs/reports/goal1116_current_source_rtx_rerun_packet/barnes_hut_depth8_20m_timing.json` |

## Boundary

Goal1116 prepares current-source RTX reruns for Facility, Robot, and Barnes-Hut. It does not create cloud resources, does not run cloud locally, does not authorize release, does not change public wording, and does not authorize public RTX speedup claims.
