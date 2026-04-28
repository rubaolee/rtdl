# Goal1062 Blocked RTX Wording Rerun Manifest

Date: 2026-04-28

Valid: `True`

Goal1062 prepares one batched rerun plan for the remaining blocked NVIDIA RTX wording rows. It does not run cloud, create resources, authorize release, or authorize public speedup wording.

## Global Preconditions

- Run only from an already-running RTX-class NVIDIA pod checkout.
- Build the OptiX backend from the checked-out commit before commands.
- Export RTDL_SOURCE_COMMIT or keep .rtdl_source_commit populated.
- Copy the whole report directory back before stopping or terminating the pod.
- Do not use this manifest to authorize public wording without a later artifact-intake and 2+ AI review.

## Rows

| App | Path | Phase | Skip validation | Timing floor | Output | Command |
| --- | --- | --- | --- | ---: | --- | --- |
| `facility_knn_assignment` | `coverage_threshold_prepared` | `correctness_validation` | `False` | `` | `docs/reports/goal1062_blocked_rtx_wording_rerun/facility_coverage_threshold_validation.json` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario facility_service_coverage --mode optix --copies 20000 --iterations 10 --radius 1.0 --output-json docs/reports/goal1062_blocked_rtx_wording_rerun/facility_coverage_threshold_validation.json` |
| `facility_knn_assignment` | `coverage_threshold_prepared` | `large_timing_repeat` | `True` | `0.100` | `docs/reports/goal1062_blocked_rtx_wording_rerun/facility_coverage_threshold_large_timing.json` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario facility_service_coverage --mode optix --copies 800000 --iterations 7 --radius 1.0 --skip-validation --output-json docs/reports/goal1062_blocked_rtx_wording_rerun/facility_coverage_threshold_large_timing.json` |
| `robot_collision_screening` | `prepared_pose_flags` | `correctness_validation` | `False` | `` | `docs/reports/goal1062_blocked_rtx_wording_rerun/robot_prepared_pose_flags_validation.json` | `python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py --mode optix --pose-count 4096 --obstacle-count 256 --iterations 3 --input-mode python_objects --result-mode pose_flags --output-json docs/reports/goal1062_blocked_rtx_wording_rerun/robot_prepared_pose_flags_validation.json` |
| `robot_collision_screening` | `prepared_pose_flags` | `large_timing_repeat` | `True` | `0.100` | `docs/reports/goal1062_blocked_rtx_wording_rerun/robot_prepared_pose_flags_large_timing.json` | `python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py --mode optix --pose-count 8000000 --obstacle-count 4096 --iterations 7 --input-mode packed_arrays --result-mode pose_count --skip-validation --output-json docs/reports/goal1062_blocked_rtx_wording_rerun/robot_prepared_pose_flags_large_timing.json` |

## Boundary

Goal1062 prepares one batched rerun plan for the remaining blocked NVIDIA RTX wording rows. It does not run cloud, create resources, authorize release, or authorize public speedup wording.

