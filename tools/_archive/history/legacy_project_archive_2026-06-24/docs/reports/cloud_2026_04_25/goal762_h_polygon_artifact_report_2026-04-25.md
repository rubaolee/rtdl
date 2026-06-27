# Goal762 RTX Cloud Artifact Report

## Verdict

Status: `needs_attention`.

This report checks cloud artifacts and summarizes phase metrics. It does not authorize RTX speedup claims; claims require human/AI review of correctness, phase separation, hardware metadata, and comparison baselines.

## Run Metadata

- summary_path: `/workspace/rtdl_python_only/docs/reports/goal761_group_h_polygon_summary_2026-04-25.json`
- runner_status: `failed`
- dry_run: `False`
- git_head: `fatal: not a git repository (or any parent up to mount point /)
Stopping at filesystem boundary (GIT_DISCOVERY_ACROSS_FILESYSTEM not set).`
- failure_count: `1`

## Artifact Table

| App | Path | Runner | Artifact | Input/prep pack (s) | Warm query median (s) | Postprocess median (s) | Validation / oracle (s) | Non-claim |
|---|---|---:|---:|---:|---:|---:|---:|---|
| polygon_pair_overlap_area_rows | polygon_pair_overlap_optix_native_assisted_phase_gate | ok | ok | 0.000000 | 36.357255 | 9.061918 |  | not a fully native polygon-area kernel and not a full app RTX speedup claim |
| polygon_set_jaccard | polygon_set_jaccard_optix_native_assisted_phase_gate | failed | ok | 0.000000 | 33.542748 | 12.897674 |  | not a fully native Jaccard kernel and not a full app RTX speedup claim |

## Baseline Review Contracts

| App | Path | Status | Comparable metric scope | Claim limit |
|---|---|---:|---|---|
| polygon_pair_overlap_area_rows | polygon_pair_overlap_optix_native_assisted_phase_gate | ok | native-assisted OptiX LSI/PIP candidate-discovery phase plus CPU exact area refinement | native-assisted candidate-discovery path only; exact area/Jaccard refinement remains CPU/Python |
| polygon_set_jaccard | polygon_set_jaccard_optix_native_assisted_phase_gate | ok | native-assisted OptiX LSI/PIP candidate-discovery phase plus CPU exact Jaccard refinement | native-assisted candidate-discovery path only; exact area/Jaccard refinement remains CPU/Python |

## Required Review

- Confirm the machine is RTX-class and `nvidia-smi` metadata matches the intended cloud resource.
- Confirm all `artifact_status` cells are `ok` before interpreting timings.
- Compare against explicit baselines separately; this report intentionally does not compute public speedup claims.
- Keep DB, fixed-radius summary, and robot pose-flag claim scopes separate.
