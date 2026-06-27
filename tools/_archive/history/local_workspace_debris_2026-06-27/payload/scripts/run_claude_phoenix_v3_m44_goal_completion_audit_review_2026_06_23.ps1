$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Claude = "C:\Users\Lestat\.local\bin\claude.exe"
$Out = Join-Path $Root "docs\reviews\claude_phoenix_v3_m44_goal_completion_audit_review_2026-06-23.raw.md"

if (-not (Test-Path -LiteralPath $Claude)) {
    throw "Claude binary not found at verified path: $Claude"
}

$Prompt = @"
You are the external reviewer for Phoenix V3 M44 goal completion. Review whether the active M44 objective is satisfied. This is a completion audit, not a release review.

Required output: one of these verdict labels:
- accept_m44_goal_complete_pending_claude_debt_backfill
- accept_m44_substantively_done_but_do_not_mark_complete_until_3ai
- revise_m44_missing_evidence_or_next_work
- reject_m44_goal_not_satisfied

Include findings by severity, answer all fifteen review questions, and include an explicit non-authorization block.

Do not authorize V3 release, all-app, paid POD, public speedup wording, broad V3-over-V2 claims, V4, embedding, C ABI, or true-zero-copy.

Read:
- docs/reviews/call_for_review_phoenix_v3_m44_goal_completion_audit_2026-06-23.md
- docs/reports/phoenix_v3_m44_goal_completion_audit_pending_3ai_2026-06-23.md
- docs/reviews/codex_antigravity_phoenix_v3_m43_grouped_reduction_cupy_warp_2ai_consensus_2026-06-23.md
- docs/reviews/phoenix_v3_claude_review_debt_register_2026-06-23.md
- docs/reports/phoenix_v3_m44_step2_scorecard_sync_after_m43_2026-06-23.md
- docs/reports/phoenix_v3_m45_barnes_hut_blocker_reaudit_2026-06-23.md
- docs/reports/phoenix_v3_m46_librts_set_b_watch_rows_status_and_next_protocol_2026-06-23.md
- docs/rebuild/v3/phoenix_v3_m47_librts_stability_protocol_2026-06-23.md
- scripts/v3_phoenix_m47_librts_stability_protocol.py
- tests/v3_phoenix_m47_librts_stability_protocol_test.py
- docs/reports/phoenix_v3_m48_librts_stability_harness_execution_safety_2026-06-23.md
- docs/reports/phoenix_v3_m49_current_blocker_queue_after_m48_2026-06-23.md
- docs/reports/phoenix_v3_m50_spatial_topology_stream_runner_fail_closed_2026-06-23.md
- docs/reviews/call_for_review_phoenix_v3_m50_spatial_topology_runner_fail_closed_2026-06-23.md
- docs/rebuild/v3/phoenix_v3_m51_librts_authorized_runbook_2026-06-23.md
- docs/reviews/call_for_review_phoenix_v3_m51_librts_authorized_runbook_2026-06-23.md
- docs/reports/phoenix_v3_m52_pod_runner_authorization_surface_audit_2026-06-23.md
- docs/reviews/call_for_review_phoenix_v3_m52_pod_runner_authorization_surface_audit_2026-06-23.md
- tests/v3_phoenix_review_debt_and_completion_gate_test.py
- tests/v3_phoenix_m50_spatial_runner_fail_closed_gate_test.py
- tests/v3_phoenix_m51_librts_authorized_runbook_gate_test.py
- tests/v3_phoenix_m52_pod_surface_audit_gate_test.py
- docs/reports/phoenix_v3_m44_review_debt_gate_and_rebuild_validation_2026-06-23.md
- docs/reviews/antigravity_phoenix_v3_m44_goal_completion_audit_review_2026-06-23.md
- docs/reviews/codex_antigravity_phoenix_v3_m44_goal_completion_audit_interim_2ai_consensus_2026-06-23.md
- docs/rebuild/v3/evidence/phoenix_v3_m47_librts_stability_protocol_dry_run_20260623/summary.json
- docs/handoff/PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md
- docs/handoff/REFRESH_LOCAL_2026-04-13.md
"@

Push-Location $Root
try {
    $Prompt | & $Claude --print --dangerously-skip-permissions --add-dir $Root | Set-Content -LiteralPath $Out -Encoding UTF8
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
    Get-Content -LiteralPath $Out -TotalCount 180
} finally {
    Pop-Location
}
