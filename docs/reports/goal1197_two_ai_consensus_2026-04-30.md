# Goal1197 Two-AI Consensus

Date: 2026-04-30

## Goal

Create a reviewed investigation manifest for the four app paths where accepted
Goal1195 evidence showed OptiX slower than Embree.

## Evidence

- Manifest:
  `docs/reports/goal1197_optix_slower_app_investigation_manifest_2026-04-30.md`
- Manifest JSON:
  `docs/reports/goal1197_optix_slower_app_investigation_manifest_2026-04-30.json`
- Claude review:
  `docs/reports/goal1197_claude_optix_slower_app_investigation_review_2026-04-30.md`
- Source evidence:
  `docs/reports/goal1195_two_ai_consensus_2026-04-30.md`
- Wording decision:
  `docs/reports/goal1196_two_ai_consensus_2026-04-30.md`

## Consensus

Codex verdict: `ACCEPT`

Claude verdict: `ACCEPT`

Goal1197 status: `closed_for_future_pod_execution`.

## Accepted Plan

The next pod run should investigate exactly these four slower OptiX rows:

- `database_analytics`
- `graph_analytics`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

The next pod run should also include this positive control:

- `road_hazard_screening`

After Goal1198, `hausdorff_distance` is no longer a positive ratio control from
the current bundle. It is a same-scale repair target: collect same-scale or
explicitly normalized Hausdorff Embree/OptiX evidence before any positive public
ratio wording.

The polygon-pair advisory from Claude was fixed before closure: the scale sweep
now holds `chunk_copies=100` constant so copy-count scaling is not confounded
with chunk-size changes.

## Boundary

Goal1197 does not authorize public wording changes, release, or speedup claims.
It only defines the reviewed investigation plan for a future batched pod session.
