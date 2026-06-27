$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Claude = "C:\Users\Lestat\.local\bin\claude.exe"
$Out = Join-Path $Root "docs\reviews\claude_phoenix_v3_m49_current_blocker_queue_review_2026-06-23.raw.md"

if (-not (Test-Path -LiteralPath $Claude)) {
    throw "Claude binary not found at verified path: $Claude"
}

$Prompt = @"
You are the external reviewer for Phoenix V3 M49. Review whether the current blocker queue after M48 is correct.

Required output: one of these verdict labels:
- accept_m49_queue_refresh_no_run
- revise_m49_queue_before_next_work
- reject_m49_wrong_next_target

Include findings by severity, answer all eight review questions, and include an explicit non-authorization block.

Do not authorize V3 release, all-app, paid POD, public speedup wording, broad V3-over-V2 claims, V4, embedding, C ABI, or true-zero-copy.

Read:
- docs/reviews/call_for_review_phoenix_v3_m49_current_blocker_queue_after_m48_2026-06-23.md
- docs/reports/phoenix_v3_m49_current_blocker_queue_after_m48_2026-06-23.md
- docs/reports/phoenix_v3_m8_remaining_blocker_queue_2026-06-22.md
- docs/reports/phoenix_v3_m35_focused_evidence_gap_ledger_2026-06-23.md
- docs/reports/phoenix_v3_m44_step2_scorecard_sync_after_m43_2026-06-23.md
- docs/reports/phoenix_v3_m45_barnes_hut_blocker_reaudit_2026-06-23.md
- docs/reports/phoenix_v3_m46_librts_set_b_watch_rows_status_and_next_protocol_2026-06-23.md
- docs/rebuild/v3/phoenix_v3_m47_librts_stability_protocol_2026-06-23.md
- docs/reports/phoenix_v3_m48_librts_stability_harness_execution_safety_2026-06-23.md
- docs/rebuild/v3/phoenix_v3_spatial_rayjoin_m3_gap_analysis_2026-06-21.md
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
