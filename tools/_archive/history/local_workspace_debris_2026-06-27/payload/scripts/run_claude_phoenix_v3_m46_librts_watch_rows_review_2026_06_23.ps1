$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Claude = "C:\Users\Lestat\.local\bin\claude.exe"
$Out = Join-Path $Root "docs\reviews\claude_phoenix_v3_m46_librts_watch_rows_review_2026-06-23.raw.md"

if (-not (Test-Path -LiteralPath $Claude)) {
    throw "Claude binary not found at verified path: $Claude"
}

$Prompt = @"
You are the external reviewer for Phoenix V3 M46. Review the LibRTS Set-B watch-row status and next-protocol recommendation.

Required output: one of these verdict labels:
- accept_m46_prepare_m47_librts_stability_protocol
- revise_m46_watch_row_classification
- revise_m46_next_action_code_fix_needed_first
- reject_m46_librts_should_be_closed

Include findings by severity, answer all seven review questions, and include an explicit non-authorization block.

Do not authorize release, all-app, paid POD, public speedup wording, broad V3-over-V2 claims, V4, embedding, C ABI, or true-zero-copy.

Read:
- docs/reviews/call_for_review_phoenix_v3_m46_librts_set_b_watch_rows_status_2026-06-23.md
- docs/reports/phoenix_v3_m46_librts_set_b_watch_rows_status_and_next_protocol_2026-06-23.md
- docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md
- docs/reports/phoenix_v3_m25_librts_aabb_optix_runner_watch_row_2026-06-23.md
- docs/reports/phoenix_v3_m27_librts_aabb_set_b_triage_and_cold_optix_retain_fix_2026-06-23.md
- docs/reviews/codex_claude_phoenix_v3_m27_librts_aabb_set_b_triage_and_cold_optix_retain_fix_2ai_consensus_2026-06-23.md
- docs/reports/phoenix_v3_m31_librts_watch_rows_existing_evidence_analysis_2026-06-23.md
- examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py
- tests/v3_phoenix_librts_aabb_count_runner_test.py
"@

Push-Location $Root
try {
    $Prompt | & $Claude --print --dangerously-skip-permissions --add-dir $Root | Set-Content -LiteralPath $Out -Encoding UTF8
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
    Get-Content -LiteralPath $Out -TotalCount 160
} finally {
    Pop-Location
}
