# Goal762 RTX Cloud Artifact Report

## Verdict

Status: `needs_attention`.

This report checks cloud artifacts and summarizes phase metrics. It does not authorize RTX speedup claims; claims require human/AI review of correctness, phase separation, hardware metadata, and comparison baselines.

## Run Metadata

- summary_path: `/workspace/rtdl_python_only/docs/reports/goal761_group_f_graph_summary.json`
- runner_status: `ok`
- dry_run: `False`
- git_head: `7f569829fbad00f9bfa58e758b0fc4ee0324b410`
- failure_count: `1`

## Artifact Table

| App | Path | Runner | Artifact | Input/prep pack (s) | Warm query median (s) | Postprocess median (s) | Validation / oracle (s) | Non-claim |
|---|---|---:|---:|---:|---:|---:|---:|---|
| graph_analytics | graph_visibility_edges_gate | ok | ok |  | 1.490231 |  |  | not shortest-path, graph database, distributed graph analytics, or whole-app graph-system acceleration; BFS visited/frontier bookkeeping and triangle set-intersection remain outside RT traversal |

## Baseline Review Contracts

| App | Path | Status | Comparable metric scope | Claim limit |
|---|---|---:|---|---|
| graph_analytics | graph_visibility_edges_gate | ok | strict graph visibility-edge, native BFS graph-ray, and native triangle-count graph-ray row-digest results for the same copies semantics | bounded graph RT sub-paths only: visibility any-hit plus BFS/triangle candidate generation; not shortest-path, graph database, distributed graph analytics, or whole-app graph-system acceleration |

## Required Review

- Confirm the machine is RTX-class and `nvidia-smi` metadata matches the intended cloud resource.
- Confirm all `artifact_status` cells are `ok` before interpreting timings.
- Compare against explicit baselines separately; this report intentionally does not compute public speedup claims.
- Keep DB, fixed-radius summary, and robot pose-flag claim scopes separate.
