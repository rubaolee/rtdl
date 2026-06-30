# Goal1068 Next RTX Pod Efficiency Batch

Date: 2026-04-28

Valid: `true`

Goal1068 prepares a larger one-pod evidence batch for facility, robot, and Barnes-Hut. It does not run cloud, does not create resources, does not authorize release, does not change public wording, and does not authorize public RTX speedup claims.

## Preconditions

- Run only from an already-running RTX-class NVIDIA pod checkout.
- Build the OptiX backend from the checked-out commit before commands.
- Export RTDL_SOURCE_COMMIT or keep .rtdl_source_commit populated.
- Copy the whole report directory back before stopping or terminating the pod.
- Treat this as evidence collection only; no public wording changes are authorized by this runner.

## Rows

| App | Path | Phase | Source | Skip validation | Timing floor | Output | Command |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| `facility_knn_assignment` | `coverage_threshold_prepared` | `correctness_validation` | `Goal1062` | `False` | `` | `docs/reports/goal1068_next_rtx_pod_efficiency_batch/facility_coverage_threshold_validation.json` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario facility_service_coverage --mode optix --copies 20000 --iterations 10 --radius 1.0 --output-json docs/reports/goal1068_next_rtx_pod_efficiency_batch/facility_coverage_threshold_validation.json` |
| `facility_knn_assignment` | `coverage_threshold_prepared` | `large_timing_repeat` | `Goal1062` | `True` | `0.100` | `docs/reports/goal1068_next_rtx_pod_efficiency_batch/facility_coverage_threshold_large_timing.json` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario facility_service_coverage --mode optix --copies 800000 --iterations 7 --radius 1.0 --skip-validation --output-json docs/reports/goal1068_next_rtx_pod_efficiency_batch/facility_coverage_threshold_large_timing.json` |
| `robot_collision_screening` | `prepared_pose_flags` | `correctness_validation` | `Goal1062` | `False` | `` | `docs/reports/goal1068_next_rtx_pod_efficiency_batch/robot_prepared_pose_flags_validation.json` | `python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py --mode optix --pose-count 4096 --obstacle-count 256 --iterations 3 --input-mode python_objects --result-mode pose_flags --output-json docs/reports/goal1068_next_rtx_pod_efficiency_batch/robot_prepared_pose_flags_validation.json` |
| `robot_collision_screening` | `prepared_pose_flags` | `large_timing_repeat` | `Goal1062` | `True` | `0.100` | `docs/reports/goal1068_next_rtx_pod_efficiency_batch/robot_prepared_pose_flags_large_timing.json` | `python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py --mode optix --pose-count 8000000 --obstacle-count 4096 --iterations 7 --input-mode packed_arrays --result-mode pose_count --skip-validation --output-json docs/reports/goal1068_next_rtx_pod_efficiency_batch/robot_prepared_pose_flags_large_timing.json` |
| `barnes_hut_force_app` | `node_coverage_prepared` | `correctness_validation` | `Goal1067` | `False` | `` | `docs/reports/goal1068_next_rtx_pod_efficiency_batch/barnes_hut_node_coverage_validation.json` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario barnes_hut_node_coverage --mode optix --body-count 200000 --iterations 3 --radius 10.0 --output-json docs/reports/goal1068_next_rtx_pod_efficiency_batch/barnes_hut_node_coverage_validation.json` |
| `barnes_hut_force_app` | `node_coverage_prepared` | `large_timing_repeat` | `Goal1067` | `True` | `0.100` | `docs/reports/goal1068_next_rtx_pod_efficiency_batch/barnes_hut_node_coverage_1m_timing.json` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario barnes_hut_node_coverage --mode optix --body-count 1000000 --iterations 7 --radius 10.0 --skip-validation --output-json docs/reports/goal1068_next_rtx_pod_efficiency_batch/barnes_hut_node_coverage_1m_timing.json` |

## Boundary

Goal1068 prepares a larger one-pod evidence batch for facility, robot, and Barnes-Hut. It does not run cloud, does not create resources, does not authorize release, does not change public wording, and does not authorize public RTX speedup claims.
