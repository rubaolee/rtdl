# Phoenix V3 Claude Review Debt Register

Date: 2026-06-23

Status: `m53_claude_bundle_backfill_obtained_goal_completion_pending_3ai`

This register records review debt that must be sent to Claude when Claude is
available again. It exists because Phoenix V3 engineering may continue with
bounded external review from another AI, but Claude must still review the
important debt items before any goal-completion audit, all-app authorization,
paid-POD authorization, or release-level decision.

Batch helper for backfilling current debt:

`scripts/run_claude_phoenix_v3_review_debt_backfill_2026_06_23.ps1`

## M53 Bundle Backfill Status

M53 obtained a bundled Claude backfill review for the open debt items M43,
M44-scorecard, and M45-M52:

- `docs/reviews/call_for_review_phoenix_v3_m53_open_claude_debt_backfill_2026-06-23.md`
- `docs/reviews/claude_phoenix_v3_m53_open_debt_backfill_recorded_review_2026-06-23.md`
- `docs/reviews/codex_claude_phoenix_v3_m53_open_debt_backfill_2ai_consensus_2026-06-23.md`

Overall verdict:

```text
accept_m53_open_debt_backfill_no_authorization_continue_m54
```

Per-debt result:

| Debt | Claude Verdict | Status |
| --- | --- | --- |
| M43 | accept | Backfilled by M53 |
| M44-scorecard | accept | Backfilled by M53 |
| M45 | accept | Backfilled by M53 |
| M46 | accept | Backfilled by M53 |
| M47 | accept | Backfilled by M53; P1 pre-execution items remain |
| M48 | accept | Backfilled by M53; P1 pre-execution items remain |
| M49 | accept | Backfilled by M53 |
| M50 | accept | Backfilled by M53 |
| M51 | accept | Backfilled by M53; run remains unauthorized |
| M52 | accept | Backfilled by M53 |
| M44 goal completion | accept | Paid separately by 3-AI M44 completion consensus |

M53 does not complete the active goal by itself because the user requires 3-AI
goal-completion audit. Gemini remains locally unavailable, and Antigravity is
only a user-forwarded GUI fallback. M53 also does not authorize POD, all-app,
release, public speedup wording, or broad V3-over-V2 claims.

## Post-M53 Debt: M70/M71 RTNN Focused Protocol And Dry-Run Gate

Status: `m70_m71_claude_backfill_obtained_goal_complete_no_execution_no_pod`

Reason:

- Claude was unavailable because of session limit when M70 and M71 needed
  review.
- Codex and Antigravity produced provisional 2AI acceptances.
- Claude has now backfilled the required reviews, and final 3AI consensus
  exists for the bounded no-execution M70/M71 scope.
- The work is still no-execution: it does not authorize benchmark execution,
  runbook execution, POD spend, all-app runs, release, or public performance
  wording.

Claude reviewed:

- `docs/reviews/call_for_review_phoenix_v3_m70_m71_claude_backfill_2026-06-24.md`
- `docs/reviews/call_for_review_phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.md`
- `docs/rebuild/v3/phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.json`
- `docs/reports/phoenix_v3_m70_rtnn_focused_protocol_2026-06-23.md`
- `docs/reviews/antigravity_phoenix_v3_m70_rtnn_focused_protocol_review_2026-06-23.md`
- `docs/reviews/call_for_review_phoenix_v3_m71_rtnn_local_harness_dry_run_gate_2026-06-23.md`
- `docs/rebuild/v3/phoenix_v3_m71_rtnn_local_harness_dry_run_gate_2026-06-23.json`
- `docs/reports/phoenix_v3_m71_rtnn_local_harness_dry_run_gate_2026-06-23.md`
- `docs/reviews/antigravity_phoenix_v3_m71_rtnn_local_harness_dry_run_gate_review_2026-06-23.md`

Recorded Claude output:

- `docs/reviews/claude_phoenix_v3_m70_rtnn_focused_protocol_recorded_review_2026-06-23.md`
- `docs/reviews/claude_phoenix_v3_m71_rtnn_local_harness_dry_run_gate_recorded_review_2026-06-23.md`
- `docs/reviews/claude_phoenix_v3_m70_m71_backfill_recorded_review_2026-06-24.md`

Final 3AI record:

- `docs/reviews/codex_claude_antigravity_phoenix_v3_m70_m71_final_3ai_consensus_2026-06-24.md`
- `docs/reports/phoenix_v3_m70_m71_goal_completion_3ai_audit_2026-06-24.md`

Helper script:

`scripts/run_claude_phoenix_v3_m70_m71_backfill_2026_06_24.ps1`

Preserved boundaries:

- no V3 release
- no all-app benchmark run
- no POD spend
- no runbook execution
- no benchmark execution
- no public speedup wording
- no broad V3-over-V2 wording
- no V4 work
- no embedding
- no C ABI
- no true-zero-copy claim
- no route-specific RTNN app tuning

## Current Debt Items

### Debt 1: M43 Grouped Reduction CuPy Warp Prepared Runner

Reason:

- Claude was unavailable because of session limit when M43 needed review.
- Gemini was unavailable with `IneligibleTierError`.
- The user supplied a substantive Antigravity GUI external review, saved at:
  `docs/reviews/antigravity_phoenix_v3_m43_grouped_reduction_cupy_warp_review_2026-06-23.md`.
- Codex+Antigravity consensus is saved at:
  `docs/reviews/codex_antigravity_phoenix_v3_m43_grouped_reduction_cupy_warp_2ai_consensus_2026-06-23.md`.

Claude must later review:

- `docs/reviews/call_for_review_phoenix_v3_m43_grouped_reduction_cupy_warp_prepared_runner_2026-06-23.md`
- `docs/reports/phoenix_v3_m43_grouped_reduction_cupy_warp_prepared_runner_2026-06-23.md`
- `docs/reviews/antigravity_phoenix_v3_m43_grouped_reduction_cupy_warp_review_2026-06-23.md`
- `docs/reviews/codex_antigravity_phoenix_v3_m43_grouped_reduction_cupy_warp_2ai_consensus_2026-06-23.md`

Required Claude output:

- Confirm, amend, or reject the Antigravity M43 verdict.
- State whether M43 remains accepted as bounded Step-2 grouped-reduction
  technical closure.
- Preserve non-authorization boundaries unless explicitly and separately
  reviewed:
  - no V3 release
  - no all-app benchmark run
  - no paid POD spend
  - no public speedup wording
  - no broad V3-over-V2 claim
  - no V4 work
  - no embedding
  - no C ABI
  - no true zero-copy claim

Helper script:

`scripts/run_claude_phoenix_v3_m43_grouped_reduction_review_2026_06_23.ps1`

### Debt 2: M44 Step-2 Scorecard Sync After M43

Reason:

- M44 was created while Claude was unavailable, to avoid blocking bounded local
  Phoenix V3 planning.
- M44 does not authorize release, all-app, paid POD, or public performance
  claims; it only synchronizes the Step-2 scorecard and next-work plan after
  M43.

Claude must later review:

- `docs/reviews/call_for_review_phoenix_v3_m44_step2_scorecard_sync_after_m43_2026-06-23.md`
- `docs/reports/phoenix_v3_m44_step2_scorecard_sync_after_m43_2026-06-23.md`

Required Claude output:

- Confirm, amend, or reject the M44 scorecard synchronization.
- State whether the next-work trail should continue away from all-app/POD and
  toward focused runtime-trunk blockers.
- Preserve all non-authorization boundaries.

Helper script:

`scripts/run_claude_phoenix_v3_m44_scorecard_sync_review_2026_06_23.ps1`

### Debt 3: M45 Barnes-Hut Blocker Reaudit

Reason:

- M45 corrected the initial M44 next-target recommendation by reading the
  existing Barnes-Hut evidence trail and classifying Barnes-Hut as
  focused-fix-covered for planning, pending reviewed full-suite validation.

Claude must later review:

- `docs/reviews/call_for_review_phoenix_v3_m45_barnes_hut_blocker_reaudit_2026-06-23.md`
- `docs/reports/phoenix_v3_m45_barnes_hut_blocker_reaudit_2026-06-23.md`

Required Claude output:

- Confirm, amend, or reject the Barnes-Hut `focused-fix-covered` planning
  classification.
- State whether more Barnes-Hut route tuning should remain blocked before
  external review.
- Preserve all non-authorization boundaries.

Helper script:

`scripts/run_claude_phoenix_v3_m45_barnes_hut_reaudit_review_2026_06_23.ps1`

### Debt 4: M46 LibRTS Watch-Row Status

Reason:

- M46 kept the accepted M27 retain-output fix but left the LibRTS OptiX cold
  and Embree stress watch rows open.
- It redirected next work toward a focused stability/cold-start protocol rather
  than all-app/POD or code rewrites.

Claude must later review:

- `docs/reviews/call_for_review_phoenix_v3_m46_librts_set_b_watch_rows_status_2026-06-23.md`
- `docs/reports/phoenix_v3_m46_librts_set_b_watch_rows_status_and_next_protocol_2026-06-23.md`

Required Claude output:

- Confirm, amend, or reject the M46 watch-row classification.
- State whether M47 protocol preparation is the correct next bounded work.
- Preserve all non-authorization boundaries.

Helper script:

`scripts/run_claude_phoenix_v3_m46_librts_watch_rows_review_2026_06_23.ps1`

### Debt 5: M47 LibRTS Stability / Cold-Start Protocol And Dry-Run Harness

Reason:

- M47 prepared a focused protocol and dry-run/intake harness for the open
  LibRTS watch rows.
- The harness is dry-run by default and requires both `--execute` and the token
  `M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED` for real execution.

Claude must later review:

- `docs/reviews/call_for_review_phoenix_v3_m47_librts_stability_protocol_2026-06-23.md`
- `docs/rebuild/v3/phoenix_v3_m47_librts_stability_protocol_2026-06-23.md`
- `scripts/v3_phoenix_m47_librts_stability_protocol.py`
- `tests/v3_phoenix_m47_librts_stability_protocol_test.py`
- `docs/rebuild/v3/evidence/phoenix_v3_m47_librts_stability_protocol_dry_run_20260623/summary.json`

Required Claude output:

- Confirm, amend, or reject the M47 protocol and harness.
- If authorizing POD, authorize exactly one focused LibRTS stability run and no
  broader spend.
- Preserve all non-authorization boundaries.

Helper script:

`scripts/run_claude_phoenix_v3_m47_librts_stability_protocol_review_2026_06_23.ps1`

### Debt 6: M44 Goal Completion Audit

Status: `paid_by_claude_recorded_review_goal_complete_pending_debt_backfill`

Reason:

- The active M44 goal was substantively satisfied by Codex evidence, but the
  user required `3-AI` completion audit before it could be called complete.
- Antigravity GUI review supplied the temporary second seat with
  verdict `accept_m44_substantively_done_but_do_not_mark_complete_until_3ai`;
- Claude then supplied the direct-call third seat with verdict
  `accept_m44_goal_complete_pending_claude_debt_backfill`.

Claude reviewed:

- `docs/reviews/call_for_review_phoenix_v3_m44_goal_completion_audit_2026-06-23.md`
- `docs/reports/phoenix_v3_m44_goal_completion_audit_pending_3ai_2026-06-23.md`
- `docs/reviews/antigravity_phoenix_v3_m44_goal_completion_audit_review_2026-06-23.md`
- `docs/reviews/codex_antigravity_phoenix_v3_m44_goal_completion_audit_interim_2ai_consensus_2026-06-23.md`
- `docs/reports/phoenix_v3_m44_review_debt_gate_and_rebuild_validation_2026-06-23.md`

Recorded Claude output:

- `docs/reviews/claude_phoenix_v3_m44_goal_completion_audit_recorded_review_2026-06-23.md`
- `docs/reviews/codex_claude_antigravity_phoenix_v3_m44_goal_completion_3ai_consensus_2026-06-23.md`

Remaining obligation:

- Backfill the discrete milestone Claude reviews for M43-M52. The completion
  review says that those discrete reviews remain debt but are not a precondition
  for M44 process-goal completion.

Helper script:

`scripts/run_claude_phoenix_v3_m44_goal_completion_audit_review_2026_06_23.ps1`

### Debt 7: M48 LibRTS Stability Harness Execution Safety

Reason:

- M48 was added while Claude was unavailable.
- It hardens the M47 focused LibRTS stability harness but does not run or
  authorize POD.

Claude must later review:

- `docs/reviews/call_for_review_phoenix_v3_m48_librts_stability_harness_execution_safety_2026-06-23.md`
- `docs/reports/phoenix_v3_m48_librts_stability_harness_execution_safety_2026-06-23.md`
- `scripts/v3_phoenix_m47_librts_stability_protocol.py`
- `tests/v3_phoenix_m47_librts_stability_protocol_test.py`
- `docs/rebuild/v3/evidence/phoenix_v3_m48_librts_stability_harness_execution_safety_dry_run_20260623/summary.json`

Required Claude output:

- Confirm, amend, or reject the M48 harness hardening.
- If authorizing POD, authorize exactly one focused LibRTS stability run and no
  broader spend.
- Preserve all non-authorization boundaries.

Helper script:

`scripts/run_claude_phoenix_v3_m48_librts_harness_execution_safety_review_2026_06_23.ps1`

### Debt 8: M49 Current Blocker Queue After M48

Reason:

- M49 was created while Claude was unavailable.
- It prevents the stale M8 Spatial/RayJoin next-target recommendation from
  being read as authorization for RayJoin route tuning after M35.

Claude must later review:

- `docs/reviews/call_for_review_phoenix_v3_m49_current_blocker_queue_after_m48_2026-06-23.md`
- `docs/reports/phoenix_v3_m49_current_blocker_queue_after_m48_2026-06-23.md`
- `docs/reports/phoenix_v3_m35_focused_evidence_gap_ledger_2026-06-23.md`
- `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_m3_gap_analysis_2026-06-21.md`

Required Claude output:

- Confirm, amend, or reject the M49 queue refresh.
- State whether Spatial/RayJoin should remain blocked except as generic
  topology-stream residency/full-M3 accounting work.
- Preserve all non-authorization boundaries.

Helper script:

`scripts/run_claude_phoenix_v3_m49_current_blocker_queue_review_2026_06_23.ps1`

### Debt 9: M50 Spatial Topology-Stream Runner Fail-Closed Gate

Reason:

- M50 was added while Claude was unavailable.
- M49 blocked Spatial/RayJoin route tuning and POD except as future generic
  topology-stream residency / full-M3 accounting work.
- The existing M3 runner still had a real-run CLI default, so M50 made it
  dry-run by default and required both `--execute` and the explicit token
  `M50_SPATIAL_TOPOLOGY_STREAM_M3_POD_AUTHORIZED` for any real execution.

Claude must later review:

- `docs/reviews/call_for_review_phoenix_v3_m50_spatial_topology_runner_fail_closed_2026-06-23.md`
- `docs/reports/phoenix_v3_m50_spatial_topology_stream_runner_fail_closed_2026-06-23.md`
- `scripts/v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner.py`
- `tests/v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner_test.py`

Required Claude output:

- Confirm, amend, or reject the M50 fail-closed runner gate.
- State whether old runner commands are now safe by default because they emit
  dry-run packets instead of running the workload.
- Preserve all non-authorization boundaries.

Helper script:

`scripts/run_claude_phoenix_v3_m50_spatial_topology_runner_fail_closed_review_2026_06_23.ps1`

### Debt 10: M51 LibRTS Authorized-Run Runbook

Reason:

- M51 was added while Claude was unavailable.
- It prepares an operational runbook for a future externally authorized focused
  LibRTS stability run.
- It does not run anything and does not authorize POD; it exists to prevent
  improvisation and summary-only evidence if a later review authorizes the run.

Claude must later review:

- `docs/reviews/call_for_review_phoenix_v3_m51_librts_authorized_runbook_2026-06-23.md`
- `docs/rebuild/v3/phoenix_v3_m51_librts_authorized_runbook_2026-06-23.md`
- `docs/rebuild/v3/phoenix_v3_m47_librts_stability_protocol_2026-06-23.md`
- `docs/reports/phoenix_v3_m48_librts_stability_harness_execution_safety_2026-06-23.md`
- `scripts/v3_phoenix_m47_librts_stability_protocol.py`

Required Claude output:

- Confirm, amend, or reject the M51 runbook.
- State whether the runbook remains non-authorizing and fail-closed.
- Preserve all non-authorization boundaries.

Helper script:

`scripts/run_claude_phoenix_v3_m51_librts_authorized_runbook_review_2026_06_23.ps1`

### Debt 11: M52 POD Runner Authorization Surface Audit

Reason:

- M52 was added while Claude was unavailable.
- It audits current Phoenix V3 executable/POD surfaces so historical evidence
  scripts are not mistaken for current authorization.
- It records that only M47 and M50 are active fail-closed token-gated surfaces,
  and neither is currently authorized to execute.

Claude must later review:

- `docs/reviews/call_for_review_phoenix_v3_m52_pod_runner_authorization_surface_audit_2026-06-23.md`
- `docs/reports/phoenix_v3_m52_pod_runner_authorization_surface_audit_2026-06-23.md`
- `scripts/v3_phoenix_m47_librts_stability_protocol.py`
- `scripts/v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner.py`

Required Claude output:

- Confirm, amend, or reject the M52 authorization-surface audit.
- State whether old `v3_phoenix_*pod*` scripts must remain historical unless
  re-gated and re-reviewed.
- Preserve all non-authorization boundaries.

Helper script:

`scripts/run_claude_phoenix_v3_m52_pod_surface_audit_review_2026_06_23.ps1`

## Standing Review Rule From User

- For major decisions, or at least once every six hours during sustained work,
  obtain `2+` AI consensus.
- Any goal-completion audit must have `3-AI` review/consensus before the goal is
  called complete.
- Default external-review priority is still: Codex calls Claude first, then
  Gemini. Antigravity is only an occasional user-forwarded GUI fallback when
  Claude/Gemini are not usable; it is not the normal path.
- Engineering may continue before the debt is paid only when the action is
  bounded, non-release, non-paid-POD, and preserves the claim boundary.

## Goal-Level Decision Audit

Decision: continue M44 using Antigravity as bounded external review while
recording mandatory Claude review debt and requiring 3-AI goal-completion audit.

1. Was I foolish? No.
2. If yes, what actions made the decision foolish? The foolish alternative
   would be either to stop all V3 work waiting for Claude, or to pretend the
   Claude review debt no longer exists.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Record the debt, continue bounded engineering, and force Claude back
   into the loop before completion or larger decisions.
4. Can I now try a different path that actually solves the problem? Yes. M44
   can proceed with scorecard synchronization and next-family planning while
   release/all-app/POD remain blocked.
