# Goal762 RTX Cloud Artifact Report

## Verdict

Status: `ok`.

This report checks cloud artifacts and summarizes phase metrics. It does not authorize RTX speedup claims; claims require human/AI review of correctness, phase separation, hardware metadata, and comparison baselines.

## Run Metadata

- summary_path: `/workspace/rtdl_python_only/docs/reports/goal761_rtx_cloud_run_all_summary.json`
- runner_status: `ok`
- dry_run: `False`
- git_head: `259c0c2dcdda373c8003cf3409a387ab61c5f407`
- failure_count: `0`

## Artifact Table

| App | Path | Runner | Artifact | Input/prep pack (s) | Warm query median (s) | Postprocess median (s) | Validation / oracle (s) | Non-claim |
|---|---|---:|---:|---:|---:|---:|---:|---|
| database_analytics | prepared_db_session_sales_risk | ok | ok |  | 0.090205 |  |  | not a SQL engine claim and not a broad RTX RT-core app speedup claim |
| database_analytics | prepared_db_session_regional_dashboard | ok | ok |  | 0.145297 |  |  | not a SQL engine claim and not a broad RTX RT-core app speedup claim |
| outlier_detection | prepared_fixed_radius_density_summary | ok | ok | 0.138852 | 0.000409 | 0.000000 | 0.000000 | not a KNN, Hausdorff, ANN, Barnes-Hut, anomaly-detection-system, or whole-app RTX speedup claim |
| dbscan_clustering | prepared_fixed_radius_core_flags | ok | ok | 0.121584 | 0.000405 | 0.000000 | 0.000000 | not a full DBSCAN clustering, KNN, Hausdorff, ANN, Barnes-Hut, or whole-app RTX speedup claim |
| robot_collision_screening | prepared_pose_flags | ok | ok | 0.000523 | 0.000179 |  | 0.000000 | not continuous collision detection, full robot kinematics, or mesh-engine replacement |

## Required Review

- Confirm the machine is RTX-class and `nvidia-smi` metadata matches the intended cloud resource.
- Confirm all `artifact_status` cells are `ok` before interpreting timings.
- Compare against explicit baselines separately; this report intentionally does not compute public speedup claims.
- Keep DB, fixed-radius summary, and robot pose-flag claim scopes separate.
