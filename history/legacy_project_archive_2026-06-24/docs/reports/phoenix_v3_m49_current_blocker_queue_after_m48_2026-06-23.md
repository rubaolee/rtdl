# Phoenix V3 M49 Current Blocker Queue After M48

Date: 2026-06-23

Status: `current_queue_refreshed_not_release_not_pod`

M49 reconciles the old M8 remaining-blocker queue with later Phoenix evidence
through M48. This is a planning/control document, not a release scorecard and
not a run authorization.

## Bottom Line

The old M8 queue still usefully identifies visible remaining rows, but its
`spatial_rayjoin_lsi_optix_topology_stream` next-target wording is stale if read
as "go tune the RayJoin route." M35 reframed RayJoin as structural-ready but not
material. It may be revisited only as a generic topology-stream residency and
full phase-accounting engine task, not as Spatial/RayJoin app tuning.

The immediate queue is:

1. Backfill Claude review debt for M43-M48 and the M44 completion audit.
2. Keep M44 goal open until the required `3-AI` completion audit is saved.
3. Review M47/M48 before any focused LibRTS stability POD run.
4. If continuing local-only engineering before review, use RayJoin only for a
   read-only topology-stream gap audit or generic prepared-handle design; do
   not code a RayJoin-specific route or spend POD.

## Current Queue

| Item | Current status | Allowed next action | Forbidden action |
| --- | --- | --- | --- |
| M44 goal completion | Codex + Antigravity say substantively done, not complete | Claude completion-audit backfill | Mark complete before Claude/3-AI |
| M43 grouped reduction | Bounded Step-2 technical closure accepted by Antigravity; Claude debt open | Claude backfill review | Use as release/all-app claim |
| M47/M48 LibRTS stability | Protocol and execution-safety harness ready locally | External review; if accepted, exactly one focused LibRTS stability run | Run POD now; all-app; rewrite LibRTS before stability evidence |
| Barnes-Hut | Focused-fix-covered for planning | Carry into next reviewed full-suite validation | More Barnes-Hut route tuning now |
| Spatial/RayJoin | Largest old row loss but structural-only under M35 | Revisit only through generic topology-stream residency/full-M3 accounting | Treat M8 as authorization to tune RayJoin or claim public Spatial speed |
| RTDBSCAN/component union | Component signature structural; component-union core node has focused positive evidence | Revisit only if generic component-union bottleneck work reduces the dominant union pass | RTDBSCAN wrapper micro-tuning |
| Grouped reduction | M43 cleared original blocked shape through generic CuPy route | Keep as Step-2 family evidence; await review debt | More shape chasing without review |

## Why M8 Is Superseded But Not Useless

M8 reported the largest active row loss as:

```text
goal2636_stress|spatial_rayjoin|rayjoin_lsi_authored_tiled_x2048|optix|rayjoin_optix_promoted_lsi_tiled_x2048
speedup: 0.8881209503239741x
```

That was correct as a row-loss ordering. It is not enough as an engineering
decision after M35, because M35 records:

```text
RayJoin point-location topology stream = structural ready, not material
Current runner wraps the same scalar-count executor; no new physical work is removed
Revisit only if RayJoin becomes a multi-phase topology pipeline where the runner removes materialization or repeated planning
```

Therefore the current meaning is:

```text
Spatial/RayJoin can remain a benchmark stress test for V3, but only for a
generic topology-stream prepared-handle/residency/full-M3-accounting task.
```

It is not a license to tune one app route.

## Supporting Evidence

- Old queue:
  `docs/reports/phoenix_v3_m8_remaining_blocker_queue_2026-06-22.md`
- M35 focused gap ledger:
  `docs/reports/phoenix_v3_m35_focused_evidence_gap_ledger_2026-06-23.md`
- M44 scorecard sync:
  `docs/reports/phoenix_v3_m44_step2_scorecard_sync_after_m43_2026-06-23.md`
- M45 Barnes-Hut reaudit:
  `docs/reports/phoenix_v3_m45_barnes_hut_blocker_reaudit_2026-06-23.md`
- M46 LibRTS watch-row status:
  `docs/reports/phoenix_v3_m46_librts_set_b_watch_rows_status_and_next_protocol_2026-06-23.md`
- M47 protocol:
  `docs/rebuild/v3/phoenix_v3_m47_librts_stability_protocol_2026-06-23.md`
- M48 harness safety:
  `docs/reports/phoenix_v3_m48_librts_stability_harness_execution_safety_2026-06-23.md`
- Existing RayJoin M3 gap analysis:
  `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_m3_gap_analysis_2026-06-21.md`

## Current Local Validation

```text
PYTHONPATH=src;. py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 122
Ran 632 tests in 75.022s
OK
```

## Non-Authorization

This report does not authorize:

- no V3 release
- no all-app benchmark run
- no paid POD spend
- no public speedup wording
- no broad V3-over-V2 claim
- no V4 work
- no embedding
- no C ABI
- no true zero-copy claim

## Goal-Level Decision Audit

Decision: treat M8's Spatial/RayJoin next-target recommendation as superseded
unless it is reframed as a generic topology-stream residency/full-M3 accounting
task.

1. Was I foolish? No.
2. If yes, what actions made the decision foolish? The foolish action would be
   blindly following the old M8 target after M35 already showed that the
   existing RayJoin runner is structural but not material.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Keep the old row-loss ordering, but add the M35 condition: only generic
   multi-phase topology-stream work counts.
4. Can I now try a different path that actually solves the problem? Yes. First
   backfill review debt and finish the LibRTS protocol review gate; if local
   RayJoin work resumes, start with a read-only topology-stream gap audit, not
   app route tuning.
