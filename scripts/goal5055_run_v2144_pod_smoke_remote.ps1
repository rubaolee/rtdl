param(
    [Parameter(Mandatory = $true)]
    [string]$HostName,

    [Parameter(Mandatory = $true)]
    [int]$Port,

    [string]$User = "root",

    [string]$IdentityFile = "",

    [string]$RemoteRepo = "/workspace/rtdl_v0_4_release_prep_review",

    [string]$RemoteOutput = "history/internal_docs/goal5052_v2144_public_api_pod_smoke_result.json",

    [string]$LocalOutput = "history/internal_docs/goal5052_v2144_public_api_pod_smoke_result.json",

    [string]$RemotePythonVenv = "",

    [string]$RemoteCudaHome = "",

    [string]$RemoteRtdlOptixLibrary = "",

    [switch]$BootstrapPodEnv
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Goal5055 remote launcher for an already-provisioned POD checkout.
# Boundary: runs the strict Goal5052 smoke and downloads evidence only.
# It does not claim public release readiness, speedup, true zero-copy, or author parity.
# It also does not create, delete, or reset the remote checkout.

$sshArgs = @(
    "-o", "BatchMode=yes",
    "-o", "StrictHostKeyChecking=no",
    "-o", "ConnectTimeout=12",
    "-p", $Port.ToString()
)

if ($IdentityFile -ne "") {
    $sshArgs += @("-i", $IdentityFile)
}

$target = "${User}@${HostName}"
$quotedRemoteRepo = "'" + ($RemoteRepo -replace "'", "'\''") + "'"
$quotedRemoteOutput = "'" + ($RemoteOutput -replace "'", "'\''") + "'"
$remoteEnv = ""
$bootstrapPodEnvValue = if ($BootstrapPodEnv.IsPresent) { "1" } else { "0" }

if ($RemotePythonVenv -ne "") {
    $quotedRemotePythonVenv = "'" + ($RemotePythonVenv -replace "'", "'\''") + "'"
    $remoteEnv += "export PATH=${quotedRemotePythonVenv}/bin:`$PATH; "
}

if ($RemoteCudaHome -ne "") {
    $quotedRemoteCudaHome = "'" + ($RemoteCudaHome -replace "'", "'\''") + "'"
    $remoteEnv += "export CUDA_HOME=${quotedRemoteCudaHome}; "
    $remoteEnv += "export CUDA_PATH=${quotedRemoteCudaHome}; "
    $remoteEnv += "export PATH=${quotedRemoteCudaHome}/bin:`$PATH; "
    $remoteEnv += "export LD_LIBRARY_PATH=${quotedRemoteCudaHome}/nvvm/lib64:`${LD_LIBRARY_PATH:-}; "
}

if ($RemoteRtdlOptixLibrary -ne "") {
    $quotedRemoteRtdlOptixLibrary = "'" + ($RemoteRtdlOptixLibrary -replace "'", "'\''") + "'"
    $remoteEnv += "export RTDL_OPTIX_LIBRARY=${quotedRemoteRtdlOptixLibrary}; "
}

$remoteCommand = @"
set -euo pipefail
cd ${quotedRemoteRepo}
${remoteEnv}
echo "goal5055_remote_host=`$(hostname)"
echo "goal5055_remote_pwd=`$(pwd)"
echo "goal5055_git_head=`$(git rev-parse HEAD 2>/dev/null || true)"
test -f scripts/goal5052_v2144_public_api_pod_smoke_runner.sh
if [ "${bootstrapPodEnvValue}" = "1" ]; then
  test -f scripts/goal5057_v2144_strict_pod_smoke_with_env.sh
  bash scripts/goal5057_v2144_strict_pod_smoke_with_env.sh ${quotedRemoteOutput}
else
  bash scripts/goal5052_v2144_public_api_pod_smoke_runner.sh ${quotedRemoteOutput}
fi
"@

Write-Host "Goal5055 remote strict POD smoke"
Write-Host "target=${target}"
Write-Host "remote_repo=${RemoteRepo}"
Write-Host "remote_output=${RemoteOutput}"
Write-Host "local_output=${LocalOutput}"

& ssh @sshArgs $target $remoteCommand
if ($LASTEXITCODE -ne 0) {
    throw "remote strict POD smoke failed"
}

$localPath = Resolve-Path -Path "." | ForEach-Object { Join-Path $_.Path $LocalOutput }
$localDir = Split-Path -Parent $localPath
if ($localDir -ne "" -and -not (Test-Path -LiteralPath $localDir)) {
    New-Item -ItemType Directory -Path $localDir | Out-Null
}

$scpArgs = @()
if ($IdentityFile -ne "") {
    $scpArgs += @("-i", $IdentityFile)
}
$scpArgs += @(
    "-P", $Port.ToString(),
    "-o", "BatchMode=yes",
    "-o", "StrictHostKeyChecking=no",
    "-o", "ConnectTimeout=12",
    "${target}:${RemoteRepo}/${RemoteOutput}",
    $localPath
)

& scp @scpArgs
if ($LASTEXITCODE -ne 0) {
    throw "failed to download strict POD smoke JSON"
}

Write-Host "Goal5055 complete: ${LocalOutput}"
