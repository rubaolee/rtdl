$ErrorActionPreference = "Stop"

param(
    [switch]$ContinueOnError
)

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Helpers = @(
    "scripts\run_claude_phoenix_v3_m43_grouped_reduction_review_2026_06_23.ps1",
    "scripts\run_claude_phoenix_v3_m44_scorecard_sync_review_2026_06_23.ps1",
    "scripts\run_claude_phoenix_v3_m45_barnes_hut_reaudit_review_2026_06_23.ps1",
    "scripts\run_claude_phoenix_v3_m46_librts_watch_rows_review_2026_06_23.ps1",
    "scripts\run_claude_phoenix_v3_m47_librts_stability_protocol_review_2026_06_23.ps1",
    "scripts\run_claude_phoenix_v3_m44_goal_completion_audit_review_2026_06_23.ps1",
    "scripts\run_claude_phoenix_v3_m48_librts_harness_execution_safety_review_2026_06_23.ps1",
    "scripts\run_claude_phoenix_v3_m49_current_blocker_queue_review_2026_06_23.ps1",
    "scripts\run_claude_phoenix_v3_m50_spatial_topology_runner_fail_closed_review_2026_06_23.ps1",
    "scripts\run_claude_phoenix_v3_m51_librts_authorized_runbook_review_2026_06_23.ps1",
    "scripts\run_claude_phoenix_v3_m52_pod_surface_audit_review_2026_06_23.ps1"
)

$Failures = @()

foreach ($Helper in $Helpers) {
    $Path = Join-Path $Root $Helper
    if (-not (Test-Path -LiteralPath $Path)) {
        $Message = "missing helper: $Helper"
        if ($ContinueOnError) {
            $Failures += $Message
            Write-Warning $Message
            continue
        }
        throw $Message
    }

    Write-Host "[phoenix-v3-claude-debt] running $Helper"
    try {
        & $Path
        if ($LASTEXITCODE -ne 0) {
            throw "exit_code=$LASTEXITCODE"
        }
    } catch {
        $Message = "$Helper failed: $($_.Exception.Message)"
        if ($ContinueOnError) {
            $Failures += $Message
            Write-Warning $Message
            continue
        }
        throw $Message
    }
}

$Summary = [ordered]@{
    status = if ($Failures.Count -eq 0) { "completed" } else { "completed_with_failures" }
    helper_count = $Helpers.Count
    failure_count = $Failures.Count
    failures = $Failures
    note = "This script only backfills Claude review debt. It does not authorize release, all-app, paid POD, public speedup wording, V4, embedding, C ABI, or true-zero-copy."
}

$Summary | ConvertTo-Json -Depth 4

if ($Failures.Count -gt 0) {
    exit 2
}
