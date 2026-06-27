# Call For Review: Phoenix V3 M60 Step-2 Set-A Selection

Date: 2026-06-23

Status:

```text
review_requested_no_release_no_pod_no_public_claims
```

## Request

Review the M60 decision to select Spatial/RayJoin point-location topology stream
as the next Step-2 Set-A runtime-family target, bounded strictly to generic
topology-stream prepared-handle / internal residency / full-M3 phase-accounting
work.

This review must decide whether the selection is technically sound and whether
M61 may proceed as local no-POD topology-stream runtime work. It must not
authorize POD, all-app benchmarking, release, public performance wording, or
RayJoin app-specific route tuning.

## Required Inputs

- `docs/reports/phoenix_v3_m60_step2_set_a_selection_spatial_topology_stream_2026-06-23.md`
- `docs/reports/phoenix_v3_m59_librts_yellow_open_decision_2026-06-23.md`
- `docs/reviews/codex_claude_antigravity_phoenix_v3_m59_librts_yellow_open_decision_3ai_consensus_2026-06-23.md`
- `docs/reports/phoenix_v3_m35_focused_evidence_gap_ledger_2026-06-23.md`
- `docs/reports/phoenix_v3_m49_current_blocker_queue_after_m48_2026-06-23.md`
- `docs/reports/phoenix_v3_m50_spatial_topology_stream_runner_fail_closed_2026-06-23.md`
- `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_m3_gap_analysis_2026-06-21.md`
- `docs/reports/phoenix_v3_m45_barnes_hut_blocker_reaudit_2026-06-23.md`
- `docs/reports/phoenix_v3_m44_step2_scorecard_sync_after_m43_2026-06-23.md`
- `docs/reviews/codex_claude_antigravity_phoenix_v3_m53_goal_completion_3ai_consensus_2026-06-23.md`
- `docs/reviews/claude_phoenix_v3_m53_open_debt_backfill_recorded_review_2026-06-23.md`
- `src/rtdsl/prepared_execution.py`

## Facts To Audit

- M59 classifies LibRTS/AABB as Set-B yellow/open and not the active Step-2
  runtime gap.
- M45 classifies Barnes-Hut as focused-fix-covered for planning, pending
  full-suite validation.
- M43/M44 classify grouped reduction as bounded Step-2 technical closure, not
  an all-app/release gate clear.
- M53 later backfilled the M43-M52 Claude review debt and records M43 as
  accepted for bounded Step-2 technical closure only.
- M35 classifies RayJoin point-location as structural-ready but not material.
- M49 says Spatial/RayJoin may be revisited only as generic topology-stream
  residency/full-M3 accounting work, not route tuning.
- M50 makes the Spatial/RayJoin topology-stream POD runner fail closed.
- The M3 gap analysis records a device-resident internal route delta of
  `2.282x`, but also says the public-row-ready full M3 phase table is missing.
- `src/rtdsl/prepared_execution.py` already has
  `run_point_location_topology_stream_prepared_session`, so M61 can start from
  an existing productized runner surface rather than inventing an app path.

## Requested Verdict Labels

Choose exactly one:

- `accept_m60_select_spatial_topology_stream_for_local_set_a_step2`
- `request_m60_changes_before_selection`
- `reject_m60_selection_choose_different_set_a_family`

## Review Questions

1. Is Spatial/RayJoin point-location topology stream a valid Set-A-shaped next
   target under Claude's Step-2 design?
2. Does M60 correctly avoid RayJoin app-specific route tuning?
3. Is it correct to prioritize topology-stream prepared-handle/residency/full-M3
   accounting over another LibRTS or Barnes-Hut cycle?
4. Does the M3 device-resident internal delta support this as a V3 residency
   lever without becoming a V4/true-zero-copy claim?
5. Is M61 correctly limited to local no-POD gap-ledger/design/gate work?
6. Does M60 preserve all non-authorization boundaries?
7. If rejecting, which Set-A family should be selected instead and why?

## Non-Authorization

This review must not authorize:

- no V3 release
- no all-app benchmark run
- no paid POD spend
- no focused POD spend
- no public speedup wording
- no broad V3-over-V2 claim
- no whole-app speedup claim
- no paper reproduction claim
- no V4 work
- no embedding
- no C ABI
- no true-zero-copy claim
- no watch-row closure
