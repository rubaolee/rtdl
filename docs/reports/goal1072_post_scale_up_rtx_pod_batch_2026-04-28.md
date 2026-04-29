# Goal1072 Post-Scale-Up RTX Pod Batch

Date: 2026-04-28

Valid: `true`

Goal1072 is a local superseding pod-batch plan based on Goal1071 evidence. It does not run cloud, does not create resources, does not authorize release, does not change public wording, and does not authorize public RTX speedup claims.

## Preconditions

- Run only from an already-running RTX-class NVIDIA pod checkout.
- Build the OptiX backend from the checked-out commit before commands.
- Export RTDL_SOURCE_COMMIT or keep .rtdl_source_commit populated.
- Copy the whole Goal1072 report directory back before stopping or terminating the pod.
- Treat this as evidence collection only; no public wording changes are authorized by this runner.

## Active Rows

| App | Path | Phase | Source | Skip validation | Timing floor | Output | Command |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| `facility_knn_assignment` | `coverage_threshold_prepared` | `correctness_validation` | `Goal1068` | `False` | `` | `docs/reports/goal1072_post_scale_up_rtx_pod_batch/facility_coverage_threshold_validation.json` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario facility_service_coverage --mode optix --copies 20000 --iterations 10 --radius 1.0 --output-json docs/reports/goal1072_post_scale_up_rtx_pod_batch/facility_coverage_threshold_validation.json` |
| `facility_knn_assignment` | `coverage_threshold_prepared` | `large_timing_repeat` | `Goal1071` | `True` | `0.100` | `docs/reports/goal1072_post_scale_up_rtx_pod_batch/facility_coverage_threshold_2_5m_timing.json` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario facility_service_coverage --mode optix --copies 2500000 --iterations 5 --radius 1.0 --skip-validation --output-json docs/reports/goal1072_post_scale_up_rtx_pod_batch/facility_coverage_threshold_2_5m_timing.json` |
| `robot_collision_screening` | `prepared_pose_flags` | `correctness_validation` | `Goal1068` | `False` | `` | `docs/reports/goal1072_post_scale_up_rtx_pod_batch/robot_prepared_pose_flags_validation.json` | `python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py --mode optix --pose-count 4096 --obstacle-count 256 --iterations 3 --input-mode python_objects --result-mode pose_flags --output-json docs/reports/goal1072_post_scale_up_rtx_pod_batch/robot_prepared_pose_flags_validation.json` |
| `robot_collision_screening` | `prepared_pose_flags` | `large_timing_repeat` | `Goal1071` | `True` | `0.100` | `docs/reports/goal1072_post_scale_up_rtx_pod_batch/robot_prepared_pose_flags_36m_timing.json` | `python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py --mode optix --pose-count 36000000 --obstacle-count 4096 --iterations 5 --input-mode packed_arrays --result-mode pose_count --skip-validation --output-json docs/reports/goal1072_post_scale_up_rtx_pod_batch/robot_prepared_pose_flags_36m_timing.json` |

## Excluded Rows

| App | Path | Status | Reason | Next move |
| --- | --- | --- | --- | --- |
| `barnes_hut_force_app` | `node_coverage_prepared` | `blocked_contract_reframe_required` | The current Barnes-Hut node-coverage contract builds only four one-level quadtree nodes. The 1M-body pod run produced a 0.004204 s median RT query, so blind body-count scaling mostly measures input construction/packing rather than meaningful RTX traversal. | Design a richer node/tree traversal contract before the next paid pod attempt; do not spend cloud time by simply increasing body_count under the current four-node build. |

## Boundary

Goal1072 is a local superseding pod-batch plan based on Goal1071 evidence. It does not run cloud, does not create resources, does not authorize release, does not change public wording, and does not authorize public RTX speedup claims.
