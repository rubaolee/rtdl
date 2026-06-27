$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Claude = "C:\Users\Lestat\.local\bin\claude.exe"
$Out = Join-Path $Root "docs\reviews\claude_phoenix_v3_m53_open_debt_backfill_review_2026-06-23.raw.md"

if (-not (Test-Path -LiteralPath $Claude)) {
    throw "Claude binary not found at verified path: $Claude"
}

$Prompt = @"
You are the external reviewer for Phoenix V3 M53 open Claude debt backfill.

This is a bounded debt-backfill review. It is not a release review and must not
authorize any execution.

Read:
- docs/reviews/call_for_review_phoenix_v3_m53_open_claude_debt_backfill_2026-06-23.md
- docs/reviews/phoenix_v3_claude_review_debt_register_2026-06-23.md
- docs/handoff/REFRESH_LOCAL_2026-04-13.md
- docs/handoff/PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md

Then inspect the supporting files named by the M53 review packet as needed.

Required output:
- One overall verdict label from the M53 packet.
- Per-debt verdict lines for M43, M44-scorecard, M45, M46, M47, M48, M49, M50,
  M51, and M52.
- Findings by severity.
- Answers to all eleven review questions.
- One recommended next bounded runtime-trunk work item for M54.
- An explicit non-authorization block.

Do not authorize V3 release, all-app, paid POD, focused POD, public speedup
wording, broad V3-over-V2 claims, V4, embedding, C ABI, or true-zero-copy.
If you think a focused POD run should be considered later, record it only as a
recommendation for a separate review packet, not as an authorization.
"@

Push-Location $Root
try {
    $Prompt | & $Claude --print --dangerously-skip-permissions --add-dir $Root | Set-Content -LiteralPath $Out -Encoding UTF8
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
    Get-Content -LiteralPath $Out -TotalCount 220
} finally {
    Pop-Location
}
