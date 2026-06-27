# Goal1071 RTX Pod Scale-Up Result

Date: 2026-04-28

## Environment

- Host: RunPod RTX A5000 pod
- GPU: NVIDIA RTX A5000, 24 GB VRAM
- Driver: 580.126.09
- CUDA used for build: 12.4
- OptiX headers: NVIDIA `optix-dev` tag `v9.0.0`
- Source commit: `9d4ce689b9e6bd9c943fa4e0cbb4be9dcc96572f`

## Bootstrap

Bootstrap passed on the pod:

- `make build-optix` succeeded with `OPTIX_PREFIX=/workspace/vendor/optix-dev`.
- Focused OptiX tests passed: 34 tests OK.
- Bootstrap artifact copied in the pod workspace: `docs/reports/goal763_rtx_cloud_bootstrap_check.json`.

## Goal1068 Batch Intake

The six-row Goal1068 batch completed and was copied back to:

- `docs/reports/goal1068_next_rtx_pod_efficiency_batch/`

Local intake result:

- Artifact: `docs/reports/goal1070_goal1068_artifact_intake_after_pod_2026-04-28.json`
- Overall status: `timing_floor_not_met`
- Validation rows passed: `3/3`
- Timing rows above 100 ms floor: `0/3`
- Timing rows below 100 ms floor: `3/3`
- Public RTX speedup claims authorized: `0`

## Goal1068 Timing Results

| App | Path | Scale | Validation | Median RT phase | 100 ms floor |
| --- | --- | ---: | --- | ---: | --- |
| `facility_knn_assignment` | `coverage_threshold_prepared` | 800,000 copies / 3.2M queries | passed separately | 0.034053 s | failed |
| `robot_collision_screening` | `prepared_pose_flags` | 8M poses / 32M rays | passed separately | 0.015967 s | failed |
| `barnes_hut_force_app` | `node_coverage_prepared` | 1M bodies / 4 nodes | passed separately | 0.004204 s | failed |

## Scale-Up Probes

Additional timing-only probes were run while the pod was still available and copied back to:

- `docs/reports/goal1071_scale_up_probes/`

| App | Probe artifact | Scale | Median RT phase | 100 ms floor |
| --- | --- | ---: | ---: | --- |
| `facility_knn_assignment` | `facility_coverage_threshold_2_5m_timing.json` | 2.5M copies / 10M queries | 0.111742 s | passed |
| `robot_collision_screening` | `robot_prepared_pose_flags_32m_timing.json` | 32M poses / 128M rays | 0.098737 s | failed, near miss |
| `robot_collision_screening` | `robot_prepared_pose_flags_36m_timing.json` | 36M poses / 144M rays | 0.102610 s | passed |

## Conclusions

Facility and robot have working larger-scale timing contracts for the next reviewed batch:

- Facility should move from 800,000 copies to 2,500,000 copies for timing-only claim-review repeats.
- Robot should move from 8,000,000 poses to 36,000,000 poses for timing-only claim-review repeats.

Barnes-Hut should not be scaled blindly under the current contract. The RT build side has only four one-level quadtree nodes, so increasing body count mostly increases input construction and packing while the RT query remains too short. This row needs a benchmark-contract redesign before another paid pod attempt.

## Boundary

This report documents cloud evidence and scale-up probes. It does not change public wording, authorize release, or authorize public RTX speedup claims. Facility and robot still require a superseding manifest/intake update and 2+ AI review before public wording can be promoted.

