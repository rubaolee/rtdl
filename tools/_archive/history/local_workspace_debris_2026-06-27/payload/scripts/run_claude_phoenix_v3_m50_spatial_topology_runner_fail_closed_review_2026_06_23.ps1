$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Claude = "C:\Users\Lestat\.local\bin\claude.exe"
$Out = Join-Path $Root "docs\reviews\claude_phoenix_v3_m50_spatial_topology_runner_fail_closed_review_2026-06-23.raw.md"

if (-not (Test-Path -LiteralPath $Claude)) {
    throw "Claude binary not found at verified path: $Claude"
}

$Prompt = @"
You are the external reviewer for Phoenix V3 M50. Review whether the Spatial/RayJoin topology-stream runner is now fail-closed after M49.

Required output: one of these verdict labels:
- accept_m50_runner_fail_closed_no_run
- revise_m50_before_next_work
- reject_m50_runner_still_runs_too_easily

Include findings by severity, answer all eight review questions, and include an explicit non-authorization block.

Do not authorize V3 release, all-app, paid POD, focused POD, public speedup wording, broad V3-over-V2 claims, V4, embedding, C ABI, or true-zero-copy.

Read:
- docs/reviews/call_for_review_phoenix_v3_m50_spatial_topology_runner_fail_closed_2026-06-23.md
- docs/reports/phoenix_v3_m50_spatial_topology_stream_runner_fail_closed_2026-06-23.md
- scripts/v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner.py
- tests/v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner_test.py
- docs/reports/phoenix_v3_m49_current_blocker_queue_after_m48_2026-06-23.md
- docs/rebuild/v3/phoenix_v3_spatial_rayjoin_m3_gap_analysis_2026-06-21.md
- docs/reviews/phoenix_v3_claude_review_debt_register_2026-06-23.md
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
