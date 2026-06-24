$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Claude = "C:\Users\Lestat\.local\bin\claude.exe"
$Out = Join-Path $Root "future\v4\reviews\claude_v4_0_release_candidate_review_2026-06-24.raw.md"

if (-not (Test-Path -LiteralPath $Claude)) {
    throw "Claude binary not found at verified path: $Claude"
}

$Prompt = @"
You are an external reviewer for RTDL V4.0 release-candidate readiness.

Required output:
- one verdict label from: approve_release_candidate_not_authorized, approve_with_required_amendments, reject_release_candidate_overclaims, reject_release_candidate_insufficient_evidence
- findings by severity
- answers to the five review questions in the call-for-review file
- explicit non-authorization block

Do not authorize release, public speedup wording, Tier-3 callback support, raw OptiX callbacks, CuPy performance claims, embedding/C-ABI, non-Python host binding claims, or app-specific native kernels.

Read these files in this repository:
- future/v4/reviews/call_for_review_v4_0_release_candidate_2026-06-24.md
- future/v4/v4_0_release_candidate_packet_2026-06-24.md
- future/v4/README.md
- src/rtdsl/v4.py
- src/rtdsl/v4_scope.py
- future/v4/evidence/v4_scope_gate_2026-06-24.json
- future/v4/evidence/v4_final_release_scope_catalog_gate_gpu_32768_2026-06-24.json
- future/v4/evidence/v4_final_release_scope_catalog_gate_gpu_2026-06-24.json
- future/v4/evidence/v4_local_full_test_sweep_2026-06-24.md
- scripts/v4_catalog_regression_gate.py
- src/rtdsl/v4_operator_catalog.py
- future/v4/tier3_numba_ptx_spike.md
- future/v4/tier3_optix_module_link_spike.md
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
