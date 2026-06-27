$ErrorActionPreference = "Stop"

$Repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PromptPath = Join-Path $Repo "scratch\claude_prompt_phoenix_v3_m70_m71_backfill_2026-06-24.txt"
$Claude = Join-Path $env:USERPROFILE ".local\bin\claude.exe"

if (!(Test-Path $PromptPath)) {
    throw "Missing prompt: $PromptPath"
}
if (!(Test-Path $Claude)) {
    throw "Missing Claude executable: $Claude"
}

Get-Content $PromptPath -Raw |
    & $Claude --print --permission-mode bypassPermissions --add-dir $Repo
