$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Claude = "C:\Users\Lestat\.local\bin\claude.exe"
$Out = Join-Path $Root "docs\reviews\claude_phoenix_v3_m47_librts_stability_protocol_review_2026-06-23.raw.md"

if (-not (Test-Path -LiteralPath $Claude)) {
    throw "Claude binary not found at verified path: $Claude"
}

$Prompt = @"
You are the external reviewer for Phoenix V3 M47. Review the LibRTS stability/cold-start protocol draft.

Required output: one of these verdict labels:
- accept_m47_protocol_no_run_yet
- accept_m47_authorize_one_focused_librts_stability_pod
- revise_m47_protocol_before_review
- reject_m47_wrong_target

Include findings by severity, answer all nine review questions, and include an explicit non-authorization block.

Do not authorize V3 release, all-app, public speedup wording, broad V3-over-V2 claims, V4, embedding, C ABI, or true-zero-copy. Only authorize paid POD if you explicitly choose accept_m47_authorize_one_focused_librts_stability_pod, and then only for one focused LibRTS stability run.

Read:
- docs/reviews/call_for_review_phoenix_v3_m47_librts_stability_protocol_2026-06-23.md
- docs/rebuild/v3/phoenix_v3_m47_librts_stability_protocol_2026-06-23.md
- docs/reports/phoenix_v3_m46_librts_set_b_watch_rows_status_and_next_protocol_2026-06-23.md
- docs/reports/phoenix_v3_m31_librts_watch_rows_existing_evidence_analysis_2026-06-23.md
- docs/reviews/codex_claude_phoenix_v3_m27_librts_aabb_set_b_triage_and_cold_optix_retain_fix_2ai_consensus_2026-06-23.md
- scripts/v3_phoenix_m47_librts_stability_protocol.py
- tests/v3_phoenix_m47_librts_stability_protocol_test.py
- docs/rebuild/v3/evidence/phoenix_v3_m47_librts_stability_protocol_dry_run_20260623/summary.json
- examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py
- tests/v3_phoenix_librts_aabb_count_runner_test.py
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
