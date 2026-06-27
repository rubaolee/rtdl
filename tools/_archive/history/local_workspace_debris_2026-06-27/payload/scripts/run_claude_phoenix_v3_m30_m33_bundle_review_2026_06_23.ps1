param(
    [string]$Repo = "C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review"
)

$ErrorActionPreference = "Stop"

$Claude = "C:\Users\Lestat\.local\bin\claude.exe"
$Prompt = Join-Path $Repo "docs\reviews\call_for_review_phoenix_v3_m30_m33_external_review_bundle_2026-06-23.md"
$Out = Join-Path $Repo "docs\reviews\claude_phoenix_v3_m30_m33_bundle_review_2026-06-23.raw.md"
$Err = Join-Path $Repo "scratch\claude_phoenix_v3_m30_m33_bundle_review_2026-06-23.err.txt"

if (-not (Test-Path -LiteralPath $Claude)) {
    throw "Claude binary not found at $Claude"
}
if (-not (Test-Path -LiteralPath $Prompt)) {
    throw "Review prompt not found at $Prompt"
}

Set-Location -LiteralPath $Repo
Remove-Item -LiteralPath $Out, $Err -ErrorAction SilentlyContinue

Get-Content -Raw -LiteralPath $Prompt |
    & $Claude --print --dangerously-skip-permissions --add-dir $Repo `
        1> $Out 2> $Err

$stdoutBytes = if (Test-Path -LiteralPath $Out) { (Get-Item -LiteralPath $Out).Length } else { 0 }
$stderrBytes = if (Test-Path -LiteralPath $Err) { (Get-Item -LiteralPath $Err).Length } else { 0 }

[pscustomobject]@{
    prompt = $Prompt
    stdout = $Out
    stderr = $Err
    stdout_bytes = $stdoutBytes
    stderr_bytes = $stderrBytes
    exit_code = $LASTEXITCODE
}
