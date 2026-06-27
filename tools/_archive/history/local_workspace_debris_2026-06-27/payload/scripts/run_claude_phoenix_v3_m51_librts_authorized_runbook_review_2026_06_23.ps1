$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Claude = "C:\Users\Lestat\.local\bin\claude.exe"
$Out = Join-Path $Root "docs\reviews\claude_phoenix_v3_m51_librts_authorized_runbook_review_2026-06-23.raw.md"

if (-not (Test-Path -LiteralPath $Claude)) {
    throw "Claude binary not found at verified path: $Claude"
}

$Prompt = @"
You are the external reviewer for Phoenix V3 M51. Review whether the LibRTS authorized-run runbook is safe and bounded.

Required output: one of these verdict labels:
- accept_m51_runbook_no_run
- revise_m51_before_any_execution
- reject_m51_accidentally_authorizes_pod

Include findings by severity, answer all eight review questions, and include an explicit non-authorization block.

Do not authorize V3 release, all-app, paid POD, focused POD, public speedup wording, broad V3-over-V2 claims, V4, embedding, C ABI, or true-zero-copy.

Read:
- docs/reviews/call_for_review_phoenix_v3_m51_librts_authorized_runbook_2026-06-23.md
- docs/rebuild/v3/phoenix_v3_m51_librts_authorized_runbook_2026-06-23.md
- docs/rebuild/v3/phoenix_v3_m47_librts_stability_protocol_2026-06-23.md
- docs/reports/phoenix_v3_m48_librts_stability_harness_execution_safety_2026-06-23.md
- scripts/v3_phoenix_m47_librts_stability_protocol.py
- tests/v3_phoenix_m47_librts_stability_protocol_test.py
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
