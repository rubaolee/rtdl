$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Claude = "C:\Users\Lestat\.local\bin\claude.exe"
$Out = Join-Path $Root "docs\reviews\claude_phoenix_v3_m45_barnes_hut_reaudit_review_2026-06-23.raw.md"

if (-not (Test-Path -LiteralPath $Claude)) {
    throw "Claude binary not found at verified path: $Claude"
}

$Prompt = @"
You are the external reviewer for Phoenix V3 M45. Review the Barnes-Hut blocker re-audit.

Required output: one of these verdict labels:
- accept_m45_barnes_hut_focused_fix_covered_move_to_remaining_blockers
- revise_m45_barnes_hut_still_active_coding_target
- revise_m45_missing_evidence_or_boundary
- reject_m45_barnes_hut_release_blocker_unresolved

Include findings by severity, answer all seven review questions, and include an explicit non-authorization block.

Do not authorize release, all-app, paid POD, public speedup wording, broad V3-over-V2 claims, V4, embedding, C ABI, or true-zero-copy.

Read:
- docs/reviews/call_for_review_phoenix_v3_m45_barnes_hut_blocker_reaudit_2026-06-23.md
- docs/reports/phoenix_v3_m45_barnes_hut_blocker_reaudit_2026-06-23.md
- docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md
- docs/reports/phoenix_v3_m24_barnes_hut_prepared_query_residency_fix_2026-06-23.md
- docs/reviews/claude_phoenix_v3_m24_barnes_hut_prepared_query_residency_fix_review_2026-06-23.raw.md
- docs/reviews/claude_phoenix_v3_m24_barnes_hut_prepared_query_residency_fix_followup_2026-06-23.raw.md
- docs/reports/phoenix_v3_barnes_hut_blocker_intake_m7_2026-06-22.md
- docs/rebuild/v3/phoenix_v3_m28_set_a_trunk_family_freeze_aggregate_tree_fused_vector_sum_2026-06-23.md
- docs/reports/phoenix_v3_m29_barnes_hut_v2_14_current_surface_classification_2026-06-23.md
- docs/reviews/claude_phoenix_v3_m29_barnes_hut_surface_classification_review_2026-06-23.raw.md
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
