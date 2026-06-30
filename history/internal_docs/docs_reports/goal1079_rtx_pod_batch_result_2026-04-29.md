# Goal1079 RTX Pod Batch Result

Date: 2026-04-29

## Environment

- Host: RunPod RTX A5000 pod
- GPU: NVIDIA RTX A5000, 24 GB VRAM
- Driver: 580.126.09
- CUDA toolkit used for build: 12.4
- OptiX headers: NVIDIA `optix-dev` tag `v9.0.0`
- Source commit staged on pod: `1dc7d0b843bb50769cf2bdd707957fb448661ca2`

## Bootstrap

Bootstrap passed on the pod:

- `make build-optix` succeeded with `OPTIX_PREFIX=/workspace/vendor/optix-dev`.
- `scripts/goal763_rtx_cloud_bootstrap_check.py` reported `status: ok`.
- Focused OptiX tests passed: 34 tests OK.
- Goal1072/Goal1076 manifest tests passed on the pod: 6 tests OK.

Copied bootstrap artifact:

- `docs/reports/goal763_rtx_cloud_bootstrap_check.json`

## Goal1072 Facility/Robot Batch

Copied artifacts:

- `docs/reports/goal1072_post_scale_up_rtx_pod_batch/facility_coverage_threshold_validation.json`
- `docs/reports/goal1072_post_scale_up_rtx_pod_batch/facility_coverage_threshold_2_5m_timing.json`
- `docs/reports/goal1072_post_scale_up_rtx_pod_batch/robot_prepared_pose_flags_validation.json`
- `docs/reports/goal1072_post_scale_up_rtx_pod_batch/robot_prepared_pose_flags_36m_timing.json`

Local intake:

- `docs/reports/goal1073_goal1072_artifact_intake_after_pod_2026-04-29.json`
- `docs/reports/goal1073_goal1072_artifact_intake_after_pod_2026-04-29.md`
- Overall status: `ready_for_public_wording_review`
- Validation rows passed: 2/2
- Timing rows passed 100 ms floor: 2/2
- Public speedup claims authorized: 0

| App | Path | Scale | Median RTX phase | Intake status |
| --- | --- | ---: | ---: | --- |
| `facility_knn_assignment` | `coverage_threshold_prepared` | 2.5M copies / 10M queries | 0.111038 s | `timing_floor_passed` |
| `robot_collision_screening` | `prepared_pose_flags` | 36M poses / 144M rays | 0.100071 s | `timing_floor_passed` |

Robot passed by a very narrow margin. Treat it as claim-review evidence, not as
a robust public speedup claim without follow-up review.

## Goal1076 Barnes-Hut Rich Candidate

Copied artifacts:

- `docs/reports/goal1076_barnes_hut_rich_rtx_pod_candidate/barnes_hut_rich_node_coverage_validation.json`
- `docs/reports/goal1076_barnes_hut_rich_rtx_pod_candidate/barnes_hut_rich_node_coverage_large_timing.json`

Local intake:

- `docs/reports/goal1078_goal1076_artifact_intake_after_pod_2026-04-29.json`
- `docs/reports/goal1078_goal1076_artifact_intake_after_pod_2026-04-29.md`
- Overall status: `timing_floor_not_met`
- Validation rows passed: 1/1
- Timing rows passed 100 ms floor: 0/1
- Public speedup claims authorized: 0

| App | Path | Scale | Median RTX phase | Intake status |
| --- | --- | ---: | ---: | --- |
| `barnes_hut_force_app` | `node_coverage_prepared_rich` | 1M bodies / 65,536 nodes | 0.005456 s | `timing_below_floor` |

## Goal1079 Barnes-Hut Scale-Up Probe

Because the 1M Barnes-Hut rich timing row was still too short, one larger
timing-only probe was run before stopping the pod.

Copied artifact:

- `docs/reports/goal1079_barnes_hut_rich_scale_up_probe/barnes_hut_rich_node_coverage_20m_timing.json`

| App | Path | Scale | Median RTX phase | Floor |
| --- | --- | ---: | ---: | --- |
| `barnes_hut_force_app` | `node_coverage_prepared_rich` | 20M bodies / 65,536 nodes | 0.221393 s | passed |

Other phase timings:

- input build: 86.603642 s
- point pack: 32.149716 s
- OptiX prepare: 1.391462 s

This shows the rich Barnes-Hut contract can reach a meaningful RTX phase scale,
but the current app has high Python-side input/packing overhead.

## Pod Shutdown

After copyback, the pod was idle:

- GPU utilization: 0%
- GPU memory used: 1 MiB
- No RTDL benchmark or build process running

The pod can be stopped or terminated.

## Boundary

This report records cloud evidence and local intake results. It does not change
public wording, authorize release, or authorize public RTX speedup claims.
