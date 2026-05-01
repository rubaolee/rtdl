# Goal1081 Same-Scale Baseline Execution Packet

Date: 2026-04-29

Valid: `true`

Goal1081 prepares same-scale baseline commands only. It does not run them, does not change public wording, does not authorize release, and does not authorize public RTX speedup claims.

## Rows

| App | Path | Baseline | Host | Output | Command |
| --- | --- | --- | --- | --- | --- |
| `facility_knn_assignment` | `coverage_threshold_prepared` | `cpu_oracle_same_scale` | `local_or_linux` | `docs/reports/goal1081_same_scale_baselines/facility_coverage_threshold_2_5m_cpu_oracle.json` | `PYTHONPATH=src:. python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario facility_service_coverage --mode dry-run --copies 2500000 --iterations 1 --radius 1.0 --output-json docs/reports/goal1081_same_scale_baselines/facility_coverage_threshold_2_5m_cpu_oracle.json` |
| `robot_collision_screening` | `prepared_pose_flags` | `embree_same_scale` | `linux_or_windows_high_memory` | `docs/reports/goal1081_same_scale_baselines/robot_prepared_pose_flags_36m_embree_baseline.json` | `PYTHONPATH=src:. python3 scripts/goal839_robot_pose_count_baseline.py --backend embree --pose-count 36000000 --obstacle-count 4096 --iterations 3 --worker-count 8 --output-json docs/reports/goal1081_same_scale_baselines/robot_prepared_pose_flags_36m_embree_baseline.json` |
| `barnes_hut_force_app` | `node_coverage_prepared_rich` | `future_contract` | `not_ready` | `None` | `not ready: contract redesign required` |

## Boundary

Goal1081 prepares same-scale baseline commands only. It does not run them, does not change public wording, does not authorize release, and does not authorize public RTX speedup claims.

