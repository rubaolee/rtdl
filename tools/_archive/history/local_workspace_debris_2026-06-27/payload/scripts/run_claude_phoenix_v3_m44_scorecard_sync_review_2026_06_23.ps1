$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Claude = "C:\Users\Lestat\.local\bin\claude.exe"
$Out = Join-Path $Root "docs\reviews\claude_phoenix_v3_m44_step2_scorecard_sync_review_2026-06-23.raw.md"

if (-not (Test-Path -LiteralPath $Claude)) {
    throw "Claude binary not found at verified path: $Claude"
}

$Prompt = @"
You are the external reviewer for Phoenix V3 M44. Review the Step-2 scorecard sync after M43.

Required output: one of these verdict labels:
- accept_m44_sync_continue_m45_barnes_hut_audit
- revise_m44_counts_or_classification
- revise_m44_next_work_selection
- reject_m44_all_app_should_be_authorized_now
- reject_m44_m43_should_not_count_as_step2_closure

Include findings by severity, answer all seven review questions in the call-for-review file, and include an explicit non-authorization block.

Do not authorize release, all-app, paid POD, public speedup wording, broad V3-over-V2 claims, V4, embedding, C ABI, or true-zero-copy.

Read:
- docs/reviews/call_for_review_phoenix_v3_m44_step2_scorecard_sync_after_m43_2026-06-23.md
- docs/reports/phoenix_v3_m44_step2_scorecard_sync_after_m43_2026-06-23.md
- docs/reports/phoenix_v3_m40_component_union_focused_pod_intake_2026-06-23.md
- docs/reviews/codex_claude_phoenix_v3_m40_component_union_focused_pod_intake_2ai_consensus_2026-06-23.md
- docs/reports/phoenix_v3_m42_grouped_reduction_grid_occupancy_root_cause_2026-06-23.md
- docs/reviews/codex_claude_phoenix_v3_m42_grouped_reduction_grid_occupancy_2ai_consensus_2026-06-23.md
- docs/reports/phoenix_v3_m43_grouped_reduction_cupy_warp_prepared_runner_2026-06-23.md
- docs/reviews/antigravity_phoenix_v3_m43_grouped_reduction_cupy_warp_review_2026-06-23.md
- docs/reviews/codex_antigravity_phoenix_v3_m43_grouped_reduction_cupy_warp_2ai_consensus_2026-06-23.md
- docs/reviews/phoenix_v3_claude_review_debt_register_2026-06-23.md
- docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md
- docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.json
- docs/rebuild/v3/phoenix_v3_m26_scorecard_classification_and_pod_resource_plan_2026-06-23.md
- docs/reviews/codex_claude_phoenix_v3_m26_scorecard_classification_and_pod_resource_plan_2ai_consensus_2026-06-23.md
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
