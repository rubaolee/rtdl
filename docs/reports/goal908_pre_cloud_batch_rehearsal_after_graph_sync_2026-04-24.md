# Goal908: Pre-Cloud Batch Rehearsal After Graph Sync

Date: 2026-04-24

## Purpose

After Goal907 synchronized graph readiness wording, Goal908 re-ran the local dry-run shape for the single-session RTX cloud packet. The goal is to verify that the next paid pod session can still run the complete active+deferred app batch in one pass, instead of restarting cloud per app.

## Commands

One-shot runner dry-run:

```bash
PYTHONPATH=src:. python3 scripts/goal769_rtx_pod_one_shot.py \
  --dry-run \
  --skip-git-update \
  --skip-optix-install \
  --include-deferred \
  --output-json build/goal907_one_shot_dry_run.json \
  --artifact-json build/goal907_artifact.json \
  --artifact-md build/goal907_artifact.md \
  --bundle-tgz build/goal907_bundle.tgz
```

Result:

```text
status: ok
include_deferred: true
steps: goal763_bootstrap, goal761_run_manifest, goal762_analyze_artifacts
bundle status: dry_run
```

Manifest dry-run:

```bash
PYTHONPATH=src:. python3 scripts/goal761_rtx_cloud_run_all.py \
  --dry-run \
  --include-deferred \
  --output-json build/goal907_goal761_dry_run.json
```

Result:

```text
status: ok
entry_count: 17
failed: []
```

## Batched App Paths

The dry-run schedules these 17 cloud artifact entries:

| # | Manifest path |
| --- | --- |
| 1 | `prepared_db_session_sales_risk` |
| 2 | `prepared_db_session_regional_dashboard` |
| 3 | `prepared_fixed_radius_density_summary` |
| 4 | `prepared_fixed_radius_core_flags` |
| 5 | `prepared_pose_flags` |
| 6 | `graph_visibility_edges_gate` |
| 7 | `prepared_gap_summary` |
| 8 | `prepared_count_summary` |
| 9 | `road_hazard_native_summary_gate` |
| 10 | `segment_polygon_hitcount_native_experimental` |
| 11 | `directed_threshold_prepared` |
| 12 | `candidate_threshold_prepared` |
| 13 | `coverage_threshold_prepared` |
| 14 | `node_coverage_prepared` |
| 15 | `segment_polygon_anyhit_rows_native_bounded_gate` |
| 16 | `polygon_pair_overlap_optix_native_assisted_phase_gate` |
| 17 | `polygon_set_jaccard_optix_native_assisted_phase_gate` |

## Interpretation

Local pre-cloud orchestration is ready in shape:

- The runbook still points to one full active+deferred pod command.
- The runner still builds a single bootstrap, benchmark, analyzer, and artifact-bundle sequence.
- The manifest includes the combined graph gate after Goal907.
- No paid cloud action is needed until an RTX pod is actually available.

## Boundary

Goal908 is a dry-run orchestration check only. It does not execute OptiX workloads, does not use NVIDIA RT cores, and does not authorize any speedup claim.
