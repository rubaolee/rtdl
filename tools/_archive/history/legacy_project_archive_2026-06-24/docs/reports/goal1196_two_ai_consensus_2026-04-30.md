# Goal1196 Two-AI Consensus

Date: 2026-04-30

## Goal

Decide which of the six Goal1195 evidence-ready app pairs may proceed to
bounded public wording sync.

## Evidence

- Decision packet:
  `docs/reports/goal1196_public_wording_decision_packet_2026-04-30.md`
- Decision packet JSON:
  `docs/reports/goal1196_public_wording_decision_packet_2026-04-30.json`
- Goal1195 consensus:
  `docs/reports/goal1195_two_ai_consensus_2026-04-30.md`
- Claude review:
  `docs/reports/goal1196_claude_public_wording_decision_review_2026-04-30.md`

## Consensus

Codex verdict: `ACCEPT`

Claude verdict: `ACCEPT`

Goal1196 status: `closed_for_public_wording_sync`.

## Accepted Decisions

- Promote `road_hazard_screening` to bounded public wording reviewed status.
- Promote `hausdorff_distance` to bounded public wording reviewed status.
- Keep `database_analytics` blocked from positive public speedup wording because
  OptiX was slower than Embree in the accepted evidence.
- Keep `graph_analytics` blocked from positive public speedup wording because
  OptiX was slower than Embree in the accepted evidence.
- Keep `polygon_pair_overlap_area_rows` blocked from positive public speedup
  wording because OptiX was slower than Embree in the accepted evidence.
- Keep `polygon_set_jaccard` blocked from positive public speedup wording
  because OptiX was slower than Embree and because the recovery trail observed
  chunk-sensitive or nondeterministic behavior after an initial parity failure.

## Boundary

This consensus authorizes a follow-up public matrix/docs sync for the two
accepted bounded wording rows only. It does not authorize release and does not
authorize whole-app, default-mode, Python postprocess, DBMS, GIS, graph-system,
exact-distance, or broad RT-core claims.
