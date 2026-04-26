# Goal762 RTX Cloud Artifact Report

## Verdict

Status: `ok`.

This report checks cloud artifacts and summarizes phase metrics. It does not authorize RTX speedup claims; claims require human/AI review of correctness, phase separation, hardware metadata, and comparison baselines.

## Run Metadata

- summary_path: `/Users/rl2025/rtdl_python_only/docs/reports/goal761_group_c_database_summary.json`
- runner_status: `ok`
- dry_run: `False`
- git_head: `fatal: not a git repository (or any parent up to mount point /)
Stopping at filesystem boundary (GIT_DISCOVERY_ACROSS_FILESYSTEM not set).`
- failure_count: `0`

## Artifact Table

| App | Path | Runner | Artifact | Input/prep pack (s) | Warm query median (s) | Postprocess median (s) | Validation / oracle (s) | Non-claim |
|---|---|---:|---:|---:|---:|---:|---:|---|
| database_analytics | prepared_db_session_sales_risk | ok | ok | 0.531194 | 0.100171 | 0.000011 |  | not a SQL engine claim and not a broad RTX RT-core app speedup claim |
| database_analytics | prepared_db_session_regional_dashboard | ok | ok | 0.675507 | 0.135571 | 0.000003 |  | not a SQL engine claim and not a broad RTX RT-core app speedup claim |

## Baseline Review Contracts

| App | Path | Status | Comparable metric scope | Claim limit |
|---|---|---:|---|---|
| database_analytics | prepared_db_session_sales_risk | ok | compact_summary prepared DB query result for the same scenario/copies/iterations | prepared DB sub-path only; not a DBMS or SQL-engine speedup claim |
| database_analytics | prepared_db_session_regional_dashboard | ok | compact_summary prepared DB query result for the same scenario/copies/iterations | prepared DB sub-path only; not a DBMS or SQL-engine speedup claim |

## Required Review

- Confirm the machine is RTX-class and `nvidia-smi` metadata matches the intended cloud resource.
- Confirm all `artifact_status` cells are `ok` before interpreting timings.
- Compare against explicit baselines separately; this report intentionally does not compute public speedup claims.
- Keep DB, fixed-radius summary, and robot pose-flag claim scopes separate.
