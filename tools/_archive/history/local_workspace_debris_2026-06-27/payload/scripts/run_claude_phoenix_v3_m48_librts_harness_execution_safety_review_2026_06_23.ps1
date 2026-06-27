$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Claude = "C:\Users\Lestat\.local\bin\claude.exe"
$Out = Join-Path $Root "docs\reviews\claude_phoenix_v3_m48_librts_harness_execution_safety_review_2026-06-23.raw.md"

if (-not (Test-Path -LiteralPath $Claude)) {
    throw "Claude binary not found at verified path: $Claude"
}

$Prompt = @"
You are the external reviewer for Phoenix V3 M48. Review the LibRTS stability harness execution-safety hardening.

Required output: one of these verdict labels:
- accept_m48_harness_safety_hardening_no_run
- accept_m48_and_authorize_one_focused_librts_stability_pod
- revise_m48_before_any_run
- reject_m48_wrong_direction

Include findings by severity, answer all nine review questions, and include an explicit non-authorization block.

Do not authorize V3 release, all-app, public speedup wording, broad V3-over-V2 claims, V4, embedding, C ABI, or true-zero-copy. Only authorize paid POD if you explicitly choose accept_m48_and_authorize_one_focused_librts_stability_pod, and then only for one focused LibRTS stability run.

Read:
- docs/reviews/call_for_review_phoenix_v3_m48_librts_stability_harness_execution_safety_2026-06-23.md
- docs/reports/phoenix_v3_m48_librts_stability_harness_execution_safety_2026-06-23.md
- scripts/v3_phoenix_m47_librts_stability_protocol.py
- tests/v3_phoenix_m47_librts_stability_protocol_test.py
- docs/rebuild/v3/phoenix_v3_m47_librts_stability_protocol_2026-06-23.md
- docs/rebuild/v3/evidence/phoenix_v3_m48_librts_stability_harness_execution_safety_dry_run_20260623/summary.json
- docs/reports/phoenix_v3_m46_librts_set_b_watch_rows_status_and_next_protocol_2026-06-23.md
- docs/reviews/codex_claude_phoenix_v3_m27_librts_aabb_set_b_triage_and_cold_optix_retain_fix_2ai_consensus_2026-06-23.md
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
