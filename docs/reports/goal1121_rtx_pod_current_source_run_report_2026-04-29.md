# Goal1121 RTX Pod Current-Source Run Report

Date: 2026-04-29

## Scope

Goal1121 records the RTX A5000 pod execution of the current-source Goal1116 packet and the follow-up robot scale correction needed to make the robot timing row reviewable under the existing 100 ms median-query floor.

This report is evidence intake only. It does not authorize release, public wording changes, or public RTX speedup claims.

## Environment

| Item | Value |
| --- | --- |
| Pod SSH | `root@69.30.85.225 -p 22197` |
| GPU | `NVIDIA RTX A5000` |
| GPU memory | `24564 MiB` |
| Driver | `570.211.01` |
| CUDA compiler | `/usr/local/cuda/bin/nvcc`, CUDA 12.4 compiler build |
| OptiX headers | Official NVIDIA `optix-dev` tag `v9.0.0`, cloned to `/workspace/vendor/optix-dev-9.0.0` |
| Native library | `/root/rtdl_python_only/build/librtdl_optix.so` |
| Source marker | `2ba7ae0` |

## Commands

The prepared runner was executed on the pod:

```text
scripts/goal1116_current_source_rtx_rerun_runner.sh
```

Because the runner's planned 8M robot timing row completed below the review floor, one bounded follow-up robot timing row was executed:

```text
python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py \
  --mode optix \
  --pose-count 64000000 \
  --obstacle-count 4096 \
  --iterations 5 \
  --input-mode packed_arrays \
  --result-mode pose_count \
  --skip-validation \
  --output-json docs/reports/goal1116_current_source_rtx_rerun_packet/robot_prepared_pose_flags_64m_timing_goal1121.json
```

## Intake Results

The original Goal1116 packet artifacts were copied back and intaken by Goal1118. That intake is intentionally still `valid: false` because the planned robot 8M timing row is below the 100 ms timing floor:

| App | Phase | Median query sec | Valid | Finding |
| --- | --- | ---: | --- | --- |
| `facility_knn_assignment` | `same_scale_validation_and_timing` | `0.103119` | `true` | none |
| `robot_collision_screening` | `correctness_validation` | `0.006214` | `true` | none |
| `robot_collision_screening` | `large_timing_repeat` at 8M poses | `0.013837` | `false` | `median_query_below_timing_floor` |
| `barnes_hut_force_app` | `correctness_validation` | `0.008320` | `true` | none |
| `barnes_hut_force_app` | `large_timing_repeat` at 20M bodies | `0.240634` | `true` | none |

The Goal1121 packet variant swaps only the robot large timing row from 8M poses to the 64M follow-up artifact. Goal1118 intake against that packet is `valid: true`:

| App | Phase | Median query sec | Valid | Finding |
| --- | --- | ---: | --- | --- |
| `facility_knn_assignment` | `same_scale_validation_and_timing` | `0.103119` | `true` | none |
| `robot_collision_screening` | `correctness_validation` | `0.006214` | `true` | none |
| `robot_collision_screening` | `large_timing_repeat` at 64M poses | `0.178698` | `true` | none |
| `barnes_hut_force_app` | `correctness_validation` | `0.008320` | `true` | none |
| `barnes_hut_force_app` | `large_timing_repeat` at 20M bodies | `0.240634` | `true` | none |

## Artifacts

| Artifact | Purpose |
| --- | --- |
| `docs/reports/goal1116_current_source_rtx_rerun_packet/goal1116_runner.log` | Runner transcript, GPU environment, start/end timestamps |
| `docs/reports/goal1116_current_source_rtx_rerun_packet/facility_recentered_coverage_threshold_2_5m_optix_validation.json` | Facility recentered OptiX validation/timing |
| `docs/reports/goal1116_current_source_rtx_rerun_packet/robot_prepared_pose_flags_validation.json` | Robot OptiX correctness validation |
| `docs/reports/goal1116_current_source_rtx_rerun_packet/robot_prepared_pose_flags_8m_timing.json` | Original robot 8M timing row, below timing floor |
| `docs/reports/goal1116_current_source_rtx_rerun_packet/robot_prepared_pose_flags_64m_timing_goal1121.json` | Follow-up robot 64M timing row, above timing floor |
| `docs/reports/goal1116_current_source_rtx_rerun_packet/barnes_hut_depth8_4096_validation.json` | Barnes-Hut OptiX correctness validation |
| `docs/reports/goal1116_current_source_rtx_rerun_packet/barnes_hut_depth8_20m_timing.json` | Barnes-Hut 20M timing row |
| `docs/reports/goal1118_current_source_rtx_rerun_intake_2026-04-29.md` | Original packet intake, `4/5` valid due to 8M robot timing floor |
| `docs/reports/goal1121_current_source_rtx_rerun_packet_with_robot_64m_2026-04-29.json` | Packet variant replacing only the robot timing row with 64M |
| `docs/reports/goal1121_current_source_rtx_rerun_intake_with_robot_64m_2026-04-29.md` | Follow-up packet intake, `5/5` valid |

## Interpretation

- Facility, robot, and Barnes-Hut all produced current-source OptiX artifacts on real RTX-class NVIDIA hardware.
- Robot correctness validation passed at 4096 poses and 256 obstacles.
- Robot 8M timing was too fast for the existing timing floor; this is a measurement-review issue, not a correctness failure.
- Robot 64M timing crossed the timing floor with median warm query `0.178698` seconds.
- Barnes-Hut 20M timing crossed the timing floor with median warm query `0.240634` seconds.
- Facility recentered timing crossed the timing floor with median warm query `0.103119` seconds and matched oracle.

## Boundary

No public speedup claim is authorized here. The artifacts support engineering review of real OptiX execution and timing-floor adequacy. Public claims still require the project wording matrix and release-level documentation review.
