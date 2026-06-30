# Goal762 RTX Cloud Artifact Report

## Verdict

Status: `ok`.

This report checks cloud artifacts and summarizes phase metrics. It does not authorize RTX speedup claims; claims require human/AI review of correctness, phase separation, hardware metadata, and comparison baselines.

## Run Metadata

- summary_path: `/Users/rl2025/rtdl_python_only/docs/reports/goal761_group_g_prepared_decision_summary.json`
- runner_status: `ok`
- dry_run: `False`
- git_head: `fatal: not a git repository (or any parent up to mount point /)
Stopping at filesystem boundary (GIT_DISCOVERY_ACROSS_FILESYSTEM not set).`
- failure_count: `0`

## Artifact Table

| App | Path | Runner | Artifact | Input/prep pack (s) | Warm query median (s) | Postprocess median (s) | Validation / oracle (s) | Non-claim |
|---|---|---:|---:|---:|---:|---:|---:|---|
| hausdorff_distance | directed_threshold_prepared | ok | ok | 0.221144 | 0.001217 | 0.000002 | 0.000071 | not an exact Hausdorff distance, KNN-row, or nearest-neighbor ranking speedup claim |
| ann_candidate_search | candidate_threshold_prepared | ok | ok | 0.184749 | 0.000632 | 0.000001 | 0.007268 | not a full ANN index, nearest-neighbor ranking, FAISS/HNSW/IVF/PQ, or recall-optimizer claim |
| barnes_hut_force_app | node_coverage_prepared | ok | ok | 0.310841 | 0.001540 | 0.000001 | 0.100459 | not a Barnes-Hut opening-rule, force-vector reduction, or N-body solver speedup claim |

## Baseline Review Contracts

| App | Path | Status | Comparable metric scope | Claim limit |
|---|---|---:|---|---|
| hausdorff_distance | directed_threshold_prepared | ok | same app/path semantics for hausdorff_distance:directed_threshold_prepared | bounded sub-path only |
| ann_candidate_search | candidate_threshold_prepared | ok | same app/path semantics for ann_candidate_search:candidate_threshold_prepared | bounded sub-path only |
| barnes_hut_force_app | node_coverage_prepared | ok | same app/path semantics for barnes_hut_force_app:node_coverage_prepared | bounded sub-path only |

## Required Review

- Confirm the machine is RTX-class and `nvidia-smi` metadata matches the intended cloud resource.
- Confirm all `artifact_status` cells are `ok` before interpreting timings.
- Compare against explicit baselines separately; this report intentionally does not compute public speedup claims.
- Keep DB, fixed-radius summary, and robot pose-flag claim scopes separate.
