# Goal1346 Follow-Up Prioritization Public Matrix Sync

Date: 2026-05-06

## Scope

Synchronized active live-matrix planning audits with current public wording
state:

- Goal1051 now expects `13` reviewed rows and only `graph_analytics` blocked.
- Goal1125 now treats unresolved NVIDIA public wording rows as
  `database_analytics`, `graph_analytics`, and `polygon_set_jaccard`.
- `polygon_pair_overlap_area_rows` is no longer unresolved in these active
  audits because Goal1263 promoted bounded polygon-pair wording.

## Boundary

This does not rewrite historical decision packets. Goal1196 and Goal1224 remain
historical evidence from earlier states. This change does not authorize new
public wording, release actions, cloud work, or backend implementation.

## Local Validation

- `PYTHONPATH=src:. python3 -m unittest tests.goal1051_post_goal1048_followup_plan_test tests.goal1125_unresolved_rtx_public_wording_prioritization_test tests.goal1196_public_wording_decision_packet_test tests.goal1224_resolve_remaining_public_wording_rows_test tests.goal938_public_rtx_wording_sync_test`
- Result: `OK`, 21 tests.
- `git diff --check`
- Result: `OK`.

## Pod Validation

Pod SSH command:

`ssh root@213.173.108.215 -p 14800 -i ~/.ssh/id_ed25519_rtdl_codex`

Validated from Git with `git fetch origin main` and `git reset --hard
origin/main`.

- Pod commit: `19f256178f81b0187d42f3c3daf72fd5e520295c`.
- Pod command: `PYTHONPATH=src:. python3 -m unittest tests.goal1051_post_goal1048_followup_plan_test tests.goal1125_unresolved_rtx_public_wording_prioritization_test tests.goal1196_public_wording_decision_packet_test tests.goal1224_resolve_remaining_public_wording_rows_test tests.goal938_public_rtx_wording_sync_test`
- Pod result: `OK`, 21 tests.
