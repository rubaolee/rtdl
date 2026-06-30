# Goal1166 Post-Goal1165 Next RTX Pod Packet

Date: 2026-04-30

Valid: `true`

Goal1166 prepares one focused post-Goal1165 RTX pod batch. It does not create cloud resources, does not authorize public wording, and does not turn timing-only skip-validation artifacts into correctness evidence.

## Preconditions

- Run only from an already-running RTX-class NVIDIA pod checkout.
- Build OptiX with driver-compatible headers before running the packet.
- For driver 550/CUDA 13, use OptiX headers v8.0.0 and RTDL_OPTIX_PTX_COMPILER=nvcc.
- Export RTDL_SOURCE_COMMIT or keep .rtdl_source_commit populated.
- Copy the whole report directory back before stopping or terminating the pod.

## Rows

| Label | App | Phase | Skip validation | Timing floor | Output | Command |
| --- | --- | --- | --- | ---: | --- | --- |
| `ann_candidate_validation` | `ann_candidate_search` | `correctness_validation` | `False` | `` | `docs/reports/goal1166_post_goal1165_next_rtx_pod_packet/ann_candidate_8192_validation.json` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario ann_candidate_coverage --mode optix --copies 8192 --iterations 3 --radius 0.2 --output-json docs/reports/goal1166_post_goal1165_next_rtx_pod_packet/ann_candidate_8192_validation.json` |
| `ann_candidate_large_timing` | `ann_candidate_search` | `large_timing_repeat` | `True` | `0.100` | `docs/reports/goal1166_post_goal1165_next_rtx_pod_packet/ann_candidate_65536_timing.json` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario ann_candidate_coverage --mode optix --copies 65536 --iterations 7 --radius 0.2 --skip-validation --output-json docs/reports/goal1166_post_goal1165_next_rtx_pod_packet/ann_candidate_65536_timing.json` |
| `robot_pose_flags_validation` | `robot_collision_screening` | `correctness_validation` | `False` | `` | `docs/reports/goal1166_post_goal1165_next_rtx_pod_packet/robot_pose_flags_32768_validation.json` | `python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py --mode optix --pose-count 32768 --obstacle-count 64 --iterations 3 --input-mode python_objects --result-mode pose_flags --output-json docs/reports/goal1166_post_goal1165_next_rtx_pod_packet/robot_pose_flags_32768_validation.json` |
| `robot_pose_flags_large_timing` | `robot_collision_screening` | `large_timing_repeat` | `True` | `0.100` | `docs/reports/goal1166_post_goal1165_next_rtx_pod_packet/robot_pose_flags_262144_timing.json` | `python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py --mode optix --pose-count 262144 --obstacle-count 64 --iterations 7 --input-mode packed_arrays --result-mode pose_count --skip-validation --output-json docs/reports/goal1166_post_goal1165_next_rtx_pod_packet/robot_pose_flags_262144_timing.json` |
| `jaccard_safe_chunk_validation` | `polygon_set_jaccard` | `safe_chunk_validation` | `False` | `` | `docs/reports/goal1166_post_goal1165_next_rtx_pod_packet/polygon_jaccard_8192_chunk512_validation.json` | `python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode optix --copies 8192 --output-mode summary --validation-mode analytic_summary --chunk-copies 512 --output-json docs/reports/goal1166_post_goal1165_next_rtx_pod_packet/polygon_jaccard_8192_chunk512_validation.json` |
| `jaccard_boundary_diagnostic_small_chunk` | `polygon_set_jaccard` | `boundary_diagnostic` | `False` | `` | `docs/reports/goal1166_post_goal1165_next_rtx_pod_packet/polygon_jaccard_8192_chunk256_diagnostic.json` | `python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode optix --copies 8192 --output-mode summary --validation-mode analytic_summary --chunk-copies 256 --output-json docs/reports/goal1166_post_goal1165_next_rtx_pod_packet/polygon_jaccard_8192_chunk256_diagnostic.json` |

## Boundary

Goal1166 prepares one focused post-Goal1165 RTX pod batch. It does not create cloud resources, does not authorize public wording, and does not turn timing-only skip-validation artifacts into correctness evidence.
