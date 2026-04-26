# Goal762 RTX Cloud Artifact Report

## Verdict

Status: `ok`.

This report checks cloud artifacts and summarizes phase metrics. It does not authorize RTX speedup claims; claims require human/AI review of correctness, phase separation, hardware metadata, and comparison baselines.

## Run Metadata

- summary_path: `/Users/rl2025/rtdl_python_only/docs/reports/goal761_group_b_fixed_radius_summary.json`
- runner_status: `ok`
- dry_run: `False`
- git_head: `fatal: not a git repository (or any parent up to mount point /)
Stopping at filesystem boundary (GIT_DISCOVERY_ACROSS_FILESYSTEM not set).`
- failure_count: `0`

## Artifact Table

| App | Path | Runner | Artifact | Input/prep pack (s) | Warm query median (s) | Postprocess median (s) | Validation / oracle (s) | Non-claim |
|---|---|---:|---:|---:|---:|---:|---:|---|
| outlier_detection | prepared_fixed_radius_density_summary | ok | ok | 0.278969 | 0.000854 | 0.000000 | 0.000000 | not per-point outlier labels, row-output neighbors, KNN, Hausdorff, ANN, Barnes-Hut, anomaly-detection-system, or whole-app RTX speedup claim |
| dbscan_clustering | prepared_fixed_radius_core_flags | ok | ok | 0.259356 | 0.000854 | 0.000000 | 0.000000 | not per-point core flags, not a full DBSCAN clustering, KNN, Hausdorff, ANN, Barnes-Hut, or whole-app RTX speedup claim |

## Baseline Review Contracts

| App | Path | Status | Comparable metric scope | Claim limit |
|---|---|---:|---|---|
| outlier_detection | prepared_fixed_radius_density_summary | ok | prepared fixed-radius scalar threshold-count/core-count result with identical radius, threshold, fixture, and copies | outlier threshold-count or DBSCAN core-count summary only; not row-returning neighbors or full DBSCAN cluster expansion |
| dbscan_clustering | prepared_fixed_radius_core_flags | ok | prepared fixed-radius scalar threshold-count/core-count result with identical radius, threshold, fixture, and copies | outlier threshold-count or DBSCAN core-count summary only; not row-returning neighbors or full DBSCAN cluster expansion |

## Required Review

- Confirm the machine is RTX-class and `nvidia-smi` metadata matches the intended cloud resource.
- Confirm all `artifact_status` cells are `ok` before interpreting timings.
- Compare against explicit baselines separately; this report intentionally does not compute public speedup claims.
- Keep DB, fixed-radius summary, and robot pose-flag claim scopes separate.

