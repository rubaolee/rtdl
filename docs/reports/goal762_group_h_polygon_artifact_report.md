# Goal762 RTX Cloud Artifact Report

## Verdict

Status: `ok`.

This report checks cloud artifacts and summarizes phase metrics. It does not authorize RTX speedup claims; claims require human/AI review of correctness, phase separation, hardware metadata, and comparison baselines.

## Run Metadata

- summary_path: `/Users/rl2025/rtdl_python_only/docs/reports/goal761_group_h_polygon_summary.json`
- runner_status: `ok`
- dry_run: `False`
- git_head: `fatal: not a git repository (or any parent up to mount point /)
Stopping at filesystem boundary (GIT_DISCOVERY_ACROSS_FILESYSTEM not set).`
- failure_count: `0`

## Artifact Table

| App | Path | Runner | Artifact | Input/prep pack (s) | Warm query median (s) | Postprocess median (s) | Validation / oracle (s) | Non-claim |
|---|---|---:|---:|---:|---:|---:|---:|---|
| polygon_pair_overlap_area_rows | polygon_pair_overlap_optix_native_assisted_phase_gate | ok | ok | 0.000000 | 4.250674 | 3.324128 |  | not a monolithic GPU polygon-area kernel and not a full app RTX speedup claim |
| polygon_set_jaccard | polygon_set_jaccard_optix_native_assisted_phase_gate | ok | ok | 0.000000 | 3.512444 | 5.403336 |  | not a monolithic GPU Jaccard kernel and not a full app RTX speedup claim |

## Baseline Review Contracts

| App | Path | Status | Comparable metric scope | Claim limit |
|---|---|---:|---|---|
| polygon_pair_overlap_area_rows | polygon_pair_overlap_optix_native_assisted_phase_gate | ok | native-assisted OptiX LSI/PIP candidate-discovery phase plus native C++ exact area continuation | native-assisted candidate-discovery plus native exact continuation path only; no full app RTX speedup claim without same-semantics review |
| polygon_set_jaccard | polygon_set_jaccard_optix_native_assisted_phase_gate | ok | native-assisted OptiX LSI/PIP candidate-discovery phase plus native C++ exact Jaccard continuation | native-assisted candidate-discovery plus native exact continuation path only; no full app RTX speedup claim without same-semantics review |

## Required Review

- Confirm the machine is RTX-class and `nvidia-smi` metadata matches the intended cloud resource.
- Confirm all `artifact_status` cells are `ok` before interpreting timings.
- Compare against explicit baselines separately; this report intentionally does not compute public speedup claims.
- Keep DB, fixed-radius summary, and robot pose-flag claim scopes separate.

