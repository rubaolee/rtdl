$ErrorActionPreference = "Stop"

$RepoRoot = "C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review"
$ClaudeExe = "C:\Users\Lestat\.local\bin\claude.exe"
$PromptPath = Join-Path $RepoRoot "docs\reviews\call_for_review_phoenix_v3_aggregate_release_readiness_13_row_2026-06-22.md"
$StdoutPath = Join-Path $RepoRoot "docs\reviews\claude_phoenix_v3_aggregate_release_readiness_13_row_after_surface_integrity_2026-06-22.stdout.md"
$StderrPath = Join-Path $RepoRoot "docs\reviews\claude_phoenix_v3_aggregate_release_readiness_13_row_after_surface_integrity_2026-06-22.stderr.txt"
$StatusPath = Join-Path $RepoRoot "docs\reviews\claude_phoenix_v3_aggregate_release_readiness_13_row_after_surface_integrity_2026-06-22.status.json"

Set-Location -LiteralPath $RepoRoot

$header = @"
You are Claude acting as the external reviewer for Phoenix V3 aggregate release readiness.
Do not modify files. Inspect the repository evidence as needed and answer in Markdown.
Use the requested verdict labels exactly. Be critical: release authorization is allowed only if the evidence supports a responsible user-facing V3 release.
"@

$status = [ordered]@{
  tool = "claude"
  review = "phoenix_v3_aggregate_release_readiness_13_row_after_surface_integrity"
  prompt_path = $PromptPath
  stdout_path = $StdoutPath
  stderr_path = $StderrPath
  started_utc = (Get-Date).ToUniversalTime().ToString("o")
  completed_utc = $null
  exit_code = $null
  result = "running"
}

$status | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $StatusPath -Encoding UTF8

try {
  $prompt = Get-Content -LiteralPath $PromptPath -Raw
  ($header + "`n`n" + $prompt) |
    & $ClaudeExe --print --dangerously-skip-permissions `
      1> $StdoutPath `
      2> $StderrPath
  $exitCode = $LASTEXITCODE
  $status.exit_code = $exitCode
  if ($exitCode -eq 0) {
    $status.result = "completed"
  } else {
    $status.result = "failed_nonzero_exit"
  }
} catch {
  $status.exit_code = 1
  $status.result = "failed_exception"
  $_ | Out-String | Add-Content -LiteralPath $StderrPath -Encoding UTF8
} finally {
  $status.completed_utc = (Get-Date).ToUniversalTime().ToString("o")
  $status | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $StatusPath -Encoding UTF8
}

exit $status.exit_code
