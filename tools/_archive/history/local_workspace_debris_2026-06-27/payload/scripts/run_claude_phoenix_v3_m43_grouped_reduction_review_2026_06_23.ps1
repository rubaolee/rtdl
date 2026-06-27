$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Claude = "C:\Users\Lestat\.local\bin\claude.exe"
$Out = Join-Path $Root "docs\reviews\claude_phoenix_v3_m43_grouped_reduction_cupy_warp_review_2026-06-23.raw.md"

if (-not (Test-Path -LiteralPath $Claude)) {
    throw "Claude binary not found at verified path: $Claude"
}

$Prompt = @"
You are the external reviewer for Phoenix V3 M43. Review the call-for-review packet and evidence in this repository.

Required output: one of these verdict labels:
- accept_m43_original_shape_hot_gate_cleared_continue_step2
- accept_m43_hot_gate_cleared_but_require_wall_followup
- revise_m43_contract_or_metadata
- reject_m43_not_generic_runtime_work

Include findings by severity, answer all seven review questions, and include an explicit non-authorization block.

Do not authorize release, all-app, paid POD, public speedup wording, broad V3-over-V2 claims, V4, embedding, C ABI, or true-zero-copy.

Read:
- docs/reviews/call_for_review_phoenix_v3_m43_grouped_reduction_cupy_warp_prepared_runner_2026-06-23.md
- docs/reports/phoenix_v3_m43_grouped_reduction_cupy_warp_prepared_runner_2026-06-23.md
- docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m43_lx1_cupy_warp_original_262144x1024_20260623_153707/summary.json
- docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m43_lx1_cupy_warp_trust_offsets_262144x1024_20260623_154342/summary.json
- docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m43_trust_offsets_followup_20260623_154700.json
- src/rtdsl/partner_adapters.py
- src/rtdsl/prepared_execution.py
- src/rtdsl/numba_partner_continuation.py
- scripts/v3_phoenix_grouped_reduction_m41_local_harness.py
"@

Push-Location $Root
try {
    $Prompt | & $Claude --print --dangerously-skip-permissions --add-dir $Root | Set-Content -LiteralPath $Out -Encoding UTF8
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
    Get-Content -LiteralPath $Out -TotalCount 120
} finally {
    Pop-Location
}
