# Call For Review: Phoenix V3 M53 Open Claude Debt Backfill

Date: 2026-06-23

This is a bounded Claude debt-backfill review. It is not a release review and
must not authorize any execution.

## Objective

Review the open Claude debt items after M44 process-goal completion:

- M43 grouped-reduction CuPy warp prepared runner
- M44 Step-2 scorecard sync
- M45 Barnes-Hut blocker reaudit
- M46 LibRTS watch-row status
- M47 LibRTS stability protocol and dry-run harness
- M48 LibRTS harness execution safety
- M49 current blocker queue
- M50 Spatial/RayJoin topology-stream runner fail-closed gate
- M51 LibRTS authorized-run runbook
- M52 POD runner authorization surface audit

Debt 6, the M44 goal-completion audit, is already paid by:

- `docs/reviews/claude_phoenix_v3_m44_goal_completion_audit_recorded_review_2026-06-23.md`
- `docs/reviews/codex_claude_antigravity_phoenix_v3_m44_goal_completion_3ai_consensus_2026-06-23.md`

## Required Files

Primary debt register:

- `docs/reviews/phoenix_v3_claude_review_debt_register_2026-06-23.md`

Open-debt review packets and reports:

- `docs/reviews/call_for_review_phoenix_v3_m43_grouped_reduction_cupy_warp_prepared_runner_2026-06-23.md`
- `docs/reports/phoenix_v3_m43_grouped_reduction_cupy_warp_prepared_runner_2026-06-23.md`
- `docs/reviews/antigravity_phoenix_v3_m43_grouped_reduction_cupy_warp_review_2026-06-23.md`
- `docs/reviews/codex_antigravity_phoenix_v3_m43_grouped_reduction_cupy_warp_2ai_consensus_2026-06-23.md`
- `docs/reviews/call_for_review_phoenix_v3_m44_step2_scorecard_sync_after_m43_2026-06-23.md`
- `docs/reports/phoenix_v3_m44_step2_scorecard_sync_after_m43_2026-06-23.md`
- `docs/reviews/call_for_review_phoenix_v3_m45_barnes_hut_blocker_reaudit_2026-06-23.md`
- `docs/reports/phoenix_v3_m45_barnes_hut_blocker_reaudit_2026-06-23.md`
- `docs/reviews/call_for_review_phoenix_v3_m46_librts_set_b_watch_rows_status_2026-06-23.md`
- `docs/reports/phoenix_v3_m46_librts_set_b_watch_rows_status_and_next_protocol_2026-06-23.md`
- `docs/reviews/call_for_review_phoenix_v3_m47_librts_stability_protocol_2026-06-23.md`
- `docs/rebuild/v3/phoenix_v3_m47_librts_stability_protocol_2026-06-23.md`
- `scripts/v3_phoenix_m47_librts_stability_protocol.py`
- `tests/v3_phoenix_m47_librts_stability_protocol_test.py`
- `docs/rebuild/v3/evidence/phoenix_v3_m47_librts_stability_protocol_dry_run_20260623/summary.json`
- `docs/reviews/call_for_review_phoenix_v3_m48_librts_stability_harness_execution_safety_2026-06-23.md`
- `docs/reports/phoenix_v3_m48_librts_stability_harness_execution_safety_2026-06-23.md`
- `docs/rebuild/v3/evidence/phoenix_v3_m48_librts_stability_harness_execution_safety_dry_run_20260623/summary.json`
- `docs/reviews/call_for_review_phoenix_v3_m49_current_blocker_queue_after_m48_2026-06-23.md`
- `docs/reports/phoenix_v3_m49_current_blocker_queue_after_m48_2026-06-23.md`
- `docs/reports/phoenix_v3_m35_focused_evidence_gap_ledger_2026-06-23.md`
- `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_m3_gap_analysis_2026-06-21.md`
- `docs/reviews/call_for_review_phoenix_v3_m50_spatial_topology_runner_fail_closed_2026-06-23.md`
- `docs/reports/phoenix_v3_m50_spatial_topology_stream_runner_fail_closed_2026-06-23.md`
- `scripts/v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner.py`
- `tests/v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner_test.py`
- `docs/reviews/call_for_review_phoenix_v3_m51_librts_authorized_runbook_2026-06-23.md`
- `docs/rebuild/v3/phoenix_v3_m51_librts_authorized_runbook_2026-06-23.md`
- `docs/reviews/call_for_review_phoenix_v3_m52_pod_runner_authorization_surface_audit_2026-06-23.md`
- `docs/reports/phoenix_v3_m52_pod_runner_authorization_surface_audit_2026-06-23.md`

Current guardrails:

- `docs/handoff/REFRESH_LOCAL_2026-04-13.md`
- `docs/handoff/PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md`
- `tests/v3_phoenix_review_debt_and_completion_gate_test.py`

## Required Verdict Labels

Choose one overall verdict:

- `accept_m53_open_debt_backfill_no_authorization_continue_m54`
- `accept_m53_with_p1_fixes_no_authorization`
- `revise_m53_missing_per_debt_evidence`
- `reject_m53_backfill_inadequate`

For each open debt item M43, M44-scorecard, M45, M46, M47, M48, M49, M50, M51,
and M52, provide one line:

```text
<debt>: accept | accept_with_p1 | revise | reject
```

## Review Questions

1. Does M43 remain accepted as bounded grouped-reduction Step-2 technical
   closure without broad release/performance claims?
2. Does M44 Step-2 scorecard sync remain accurate after M43 and M44 completion?
3. Is M45 correct that Barnes-Hut is focused-fix-covered for planning, pending
   validation, and should not be a new route-tuning target?
4. Is M46 correct that LibRTS watch rows remain open and need stability
   protocol evidence before interpretation?
5. Is M47 protocol/harness safe as dry-run-only by default?
6. Is M48 harness-safety hardening sufficient and still non-authorizing?
7. Is M49 correct that stale Spatial/RayJoin route tuning remains blocked except
   as generic topology-stream residency/full-M3 accounting work?
8. Is M50's runner fail-closed gate sufficient to prevent accidental execution?
9. Is M51's runbook non-authorizing and operationally precise enough for a
   future separately authorized focused run?
10. Is M52's authorization-surface audit correct about current vs historical
    runner authorization?
11. Which single next bounded runtime-trunk work item should M54 take?

## Non-Authorization

This review must not authorize:

- no V3 release
- no all-app benchmark run
- no paid POD spend
- no focused POD spend
- no public speedup wording
- no broad V3-over-V2 claim
- no V4 work
- no embedding
- no C ABI
- no true zero-copy claim

If you believe a focused POD run should be considered later, record it only as
a recommendation for a separate review packet. Do not authorize it here.
