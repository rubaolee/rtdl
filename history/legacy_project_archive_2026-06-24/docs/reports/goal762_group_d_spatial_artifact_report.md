# Goal762 RTX Cloud Artifact Report

## Verdict

Status: `ok`.

This report checks cloud artifacts and summarizes phase metrics. It does not authorize RTX speedup claims; claims require human/AI review of correctness, phase separation, hardware metadata, and comparison baselines.

## Run Metadata

- summary_path: `/Users/rl2025/rtdl_python_only/docs/reports/goal761_group_d_spatial_summary.json`
- runner_status: `ok`
- dry_run: `False`
- git_head: `fatal: not a git repository (or any parent up to mount point /)
Stopping at filesystem boundary (GIT_DISCOVERY_ACROSS_FILESYSTEM not set).`
- failure_count: `0`

## Artifact Table

| App | Path | Runner | Artifact | Input/prep pack (s) | Warm query median (s) | Postprocess median (s) | Validation / oracle (s) | Non-claim |
|---|---|---:|---:|---:|---:|---:|---:|---|
| service_coverage_gaps | prepared_gap_summary | ok | ok | 0.242204 | 0.147815 | 0.000007 |  | not a whole-app service coverage speedup claim and not a nearest-clinic row-output claim |
| event_hotspot_screening | prepared_count_summary | ok | ok | 0.159699 | 0.226937 | 0.000007 |  | not a whole-app hotspot-screening speedup claim and not a neighbor-row output claim |
| facility_knn_assignment | coverage_threshold_prepared | ok | ok | 0.260395 | 0.000599 | 0.000001 | 0.000000 | not a ranked nearest-depot, KNN fallback-assignment, or facility-location optimizer claim |

## Baseline Review Contracts

| App | Path | Status | Comparable metric scope | Claim limit |
|---|---|---:|---|---|
| service_coverage_gaps | prepared_gap_summary | ok | prepared compact fixed-radius summary for the same generated households/events/facilities and radius | prepared compact summary only; not nearest-row or whole-app speedup |
| event_hotspot_screening | prepared_count_summary | ok | prepared compact fixed-radius summary for the same generated households/events/facilities and radius | prepared compact summary only; not nearest-row or whole-app speedup |
| facility_knn_assignment | coverage_threshold_prepared | ok | same app/path semantics for facility_knn_assignment:coverage_threshold_prepared | bounded sub-path only |

## Required Review

- Confirm the machine is RTX-class and `nvidia-smi` metadata matches the intended cloud resource.
- Confirm all `artifact_status` cells are `ok` before interpreting timings.
- Compare against explicit baselines separately; this report intentionally does not compute public speedup claims.
- Keep DB, fixed-radius summary, and robot pose-flag claim scopes separate.

