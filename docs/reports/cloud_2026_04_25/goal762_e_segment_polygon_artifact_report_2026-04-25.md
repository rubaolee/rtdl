# Goal762 RTX Cloud Artifact Report

## Verdict

Status: `ok`.

This report checks cloud artifacts and summarizes phase metrics. It does not authorize RTX speedup claims; claims require human/AI review of correctness, phase separation, hardware metadata, and comparison baselines.

## Run Metadata

- summary_path: `/workspace/rtdl_python_only/docs/reports/goal761_group_e_segment_polygon_summary_2026-04-25.json`
- runner_status: `ok`
- dry_run: `False`
- git_head: `fatal: not a git repository (or any parent up to mount point /)
Stopping at filesystem boundary (GIT_DISCOVERY_ACROSS_FILESYSTEM not set).`
- failure_count: `0`

## Artifact Table

| App | Path | Runner | Artifact | Input/prep pack (s) | Warm query median (s) | Postprocess median (s) | Validation / oracle (s) | Non-claim |
|---|---|---:|---:|---:|---:|---:|---:|---|
| road_hazard_screening | road_hazard_native_summary_gate | ok | ok |  | 7.212323 |  |  | not default public road-hazard behavior and not a full GIS/routing speedup claim |
| segment_polygon_hitcount | segment_polygon_hitcount_native_experimental | ok | ok |  |  |  |  | not default public app behavior and not a row-returning any-hit claim |
| segment_polygon_anyhit_rows | segment_polygon_anyhit_rows_native_bounded_gate | ok | ok |  | 0.000000 |  |  | not default public app behavior and not an unbounded pair-row performance claim |

## Baseline Review Contracts

| App | Path | Status | Comparable metric scope | Claim limit |
|---|---|---:|---|---|
| road_hazard_screening | road_hazard_native_summary_gate | ok | strict road-hazard native OptiX summary result on the same copies/output-mode semantics | experimental native road-hazard summary gate only; not default public app behavior or full GIS/routing speedup |
| segment_polygon_hitcount | segment_polygon_hitcount_native_experimental | ok | strict segment/polygon hit-count result on the same dataset and output count semantics | experimental native hit-count gate only; not pair-row any-hit or road-hazard whole-app speedup |
| segment_polygon_anyhit_rows | segment_polygon_anyhit_rows_native_bounded_gate | ok | strict bounded segment/polygon pair-row result on the same dataset and output capacity | experimental native bounded pair-row gate only; not default public app behavior and not unbounded row-volume performance |

## Required Review

- Confirm the machine is RTX-class and `nvidia-smi` metadata matches the intended cloud resource.
- Confirm all `artifact_status` cells are `ok` before interpreting timings.
- Compare against explicit baselines separately; this report intentionally does not compute public speedup claims.
- Keep DB, fixed-radius summary, and robot pose-flag claim scopes separate.
