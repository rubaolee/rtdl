# Goal762 RTX Cloud Artifact Report

## Verdict

Status: `ok`.

This report checks cloud artifacts and summarizes phase metrics. It does not authorize RTX speedup claims; claims require human/AI review of correctness, phase separation, hardware metadata, and comparison baselines.

## Run Metadata

- summary_path: `/workspace/rtdl_python_only/docs/reports/goal761_rtx_cloud_run_all_summary_runpod_2026-04-23.json`
- runner_status: `ok`
- dry_run: `False`
- git_head: `e74c54e89e3548627b69b24a73d36870b7b6d08e`
- failure_count: `0`

## Artifact Table

| App | Path | Runner | Artifact | Warm query median (s) | Postprocess median (s) | Validation / oracle (s) | Non-claim |
|---|---|---:|---:|---:|---:|---:|---|
| database_analytics | prepared_db_session_sales_risk | ok | ok | 0.137131 |  |  | not a SQL engine claim and not a broad RTX RT-core app speedup claim |
| database_analytics | prepared_db_session_regional_dashboard | ok | ok | 0.204094 |  |  | not a SQL engine claim and not a broad RTX RT-core app speedup claim |
| outlier_detection | prepared_fixed_radius_density_summary | ok | ok | 0.490954 | 0.137718 | 0.000000 | not a KNN, Hausdorff, ANN, Barnes-Hut, anomaly-detection-system, or whole-app RTX speedup claim |
| dbscan_clustering | prepared_fixed_radius_core_flags | ok | ok | 0.482424 | 0.137738 | 0.000000 | not a full DBSCAN clustering, KNN, Hausdorff, ANN, Barnes-Hut, or whole-app RTX speedup claim |
| robot_collision_screening | prepared_pose_flags | ok | ok | 0.240423 |  | 0.000000 | not continuous collision detection, full robot kinematics, or mesh-engine replacement |

## Required Review

- Confirm the machine is RTX-class and `nvidia-smi` metadata matches the intended cloud resource.
- Confirm all `artifact_status` cells are `ok` before interpreting timings.
- Compare against explicit baselines separately; this report intentionally does not compute public speedup claims.
- Keep DB, fixed-radius summary, and robot pose-flag claim scopes separate.
