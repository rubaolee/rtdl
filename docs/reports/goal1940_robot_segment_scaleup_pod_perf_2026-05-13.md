# Goal1940 Robot and Segment Scale-Up Pod Performance

Status: robot-segment-scaleup-evidence-collected-release-still-blocked

Date: 2026-05-13

## Scope

Goal1940 extends the Goal1933/1934 large-scale pod work for the two rows that
were still too small to read well: `segment_polygon_anyhit_rows` and
`robot_collision_screening`.

The run used the RTX A5000 pod artifacts labeled with source commit
`35666fb829a88f77ebdc6d18b9a66a45861d0e67`. It does not authorize v2.0
release readiness, package-install claims, broad RT-core acceleration claims,
whole-app acceleration claims, or arbitrary PyTorch/CuPy program acceleration.

## Segment Any-Hit Rows

This row is now useful seconds-scale evidence. The same-contract v1.8 prepared
OptiX baseline emits generic any-hit rows; the v2 path keeps the same prepared
OptiX ray/primitive work and hands the result columns to CuPy or Torch for the
partner-side query contract.

| Count | Partner | v1.8 median s | v2 median s | v2/v1.8 | Parity |
| ---: | --- | ---: | ---: | ---: | --- |
| 65,536 | CuPy | 0.369504 | 0.076481 | 0.206983x | pass |
| 65,536 | Torch | 0.369504 | 0.074531 | 0.201706x | pass |
| 262,144 | CuPy | 2.422186 | 0.354920 | 0.146529x | pass |
| 262,144 | Torch | 2.422186 | 0.353734 | 0.146039x | pass |
| 1,048,576 | CuPy | 7.121871 | 1.631535 | 0.229088x | pass |
| 1,048,576 | Torch | 7.121871 | 1.582755 | 0.222239x | pass |

Interpretation: this is a positive v2 partner-composition result at real
seconds scale. It supports a narrow claim that the current segment any-hit row
can preserve the v1.8 contract while moving the post-native column work into
partner tensors. It still does not prove broad RT-core speedup or whole-app
acceleration because both sides use the same prepared OptiX ray/primitive work;
the measured difference is the surrounding contract and column-processing path.

## Robot Collision Screening

This row remains a strong positive-ratio result, but the prepared OptiX baseline
is still subsecond at the largest completed fetched scale. The v2 row writes
generic native any-hit ray flags and lets CuPy/Torch reduce those flags into app
pose-collision flags on GPU. The artifacts record true zero-copy device-column
handoff metadata for the selected OptiX path, but keep `rt_core_speedup` and
whole-app claims unauthorized.

| Poses | Obstacles | Partner | v1.8 median s | v2 median s | v2/v1.8 | Pose flags |
| ---: | ---: | --- | ---: | ---: | ---: | --- |
| 262,144 | 4,096 | CuPy | 0.018790 | 0.000799 | 0.042545x | exact |
| 262,144 | 4,096 | Torch | 0.015061 | 0.000816 | 0.054200x | exact |
| 1,048,576 | 16,384 | CuPy | 0.062005 | 0.001923 | 0.031008x | exact |
| 1,048,576 | 16,384 | Torch | 0.057051 | 0.001828 | 0.032033x | exact |
| 4,194,304 | 16,384 | CuPy | 0.250863 | 0.005143 | 0.020502x | exact |
| 4,194,304 | 16,384 | Torch | 0.259467 | 0.005685 | 0.021910x | exact |
| 8,388,608 | 16,384 | CuPy | 0.524696 | 0.009835 | 0.018745x | exact |
| 8,388,608 | 16,384 | Torch | 0.529537 | 0.011019 | 0.020808x | exact |

Interpretation: the adapter is doing the right v2-style thing, and the partner
post-processing is much cheaper than the v1.8 pose-flag materialization path.
However, because the baseline remains below one second even at 4,194,304 poses,
this is not yet the seconds-scale robot claim we wanted. Treat it as a strong
implementation and scaling signal, not as final broad performance evidence.
The 8,388,608-pose row was run with visible progress and a 45-minute timeout;
it completed cleanly, but still kept the v1.8 median near half a second.

## Boundary

- Segment any-hit has a seconds-scale positive same-contract pod row.
- Robot collision has exact parity and strong positive ratios through
  8,388,608 poses, but the completed fetched rows are still subsecond baseline
  rows.
- Both rows are source-labeled and GPU-labeled RTX A5000 pod artifacts.
- The evidence does not authorize v2.0 release readiness, whole-app speedup
  wording, broad RT-core wording, package-install wording, or arbitrary partner
  program acceleration.

## Artifacts

- `docs/reports/goal1940_robot_segment_scaleup_pod/segment_segment_anyhit_rows_65536.json`
- `docs/reports/goal1940_robot_segment_scaleup_pod/segment_262144_segment_anyhit_rows_262144.json`
- `docs/reports/goal1940_robot_segment_scaleup_pod/segment_1048576_segment_anyhit_rows_1048576.json`
- `docs/reports/goal1940_robot_segment_scaleup_pod/robot_robot_collision_262144x4096.json`
- `docs/reports/goal1940_robot_segment_scaleup_pod/robot_1048576x16384_robot_collision_1048576x16384.json`
- `docs/reports/goal1940_robot_segment_scaleup_pod/robot_4194304x16384_robot_collision_4194304x16384.json`
- `docs/reports/goal1940_robot_segment_scaleup_pod/robot_8388608x16384_robot_collision_8388608x16384.json`
