# Goal5055 - v2.14.4 POD Smoke Remote Launcher

Date: 2026-07-06

Status:

```text
completed_remote_pod_smoke_launcher_ready__pod_auth_still_blocked
```

## Purpose

Goal5055 makes the remaining strict POD smoke debt easier to retire when a
login-capable POD is available.

Goal5052 already created the in-POD strict smoke runner.  Goal5055 adds a
Windows-side PowerShell launcher that:

1. SSHes into an already-provisioned POD checkout;
2. runs the strict Goal5052 smoke runner there;
3. downloads the resulting JSON to the local evidence path expected by the
   Goal5053 release preflight gate.

It does not upload a new checkout, reset remote files, delete remote files, or
claim that the POD smoke has passed.

## Added Files

```text
scripts/goal5055_run_v2144_pod_smoke_remote.ps1
tests/goal5055_v2144_pod_smoke_remote_launcher_test.py
```

## Usage

Example:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/goal5055_run_v2144_pod_smoke_remote.ps1 `
  -HostName 157.157.221.29 `
  -Port 22051 `
  -IdentityFile "$env:USERPROFILE\.ssh\id_ed25519" `
  -RemoteRepo "/workspace/rtdl_v0_4_release_prep_review"
```

The default local output path is:

```text
history/internal_docs/goal5052_v2144_public_api_pod_smoke_result.json
```

That is the same path required by:

```text
scripts/goal5053_v2144_release_preflight.py
```

## Remote Preconditions

The remote POD must already contain:

```text
an RTDL checkout
scripts/goal5052_v2144_public_api_pod_smoke_runner.sh
build/librtdl_optix.so or a valid RTDL_OPTIX_LIBRARY setup
CUDA/Numba runtime capable of running the strict smoke
```

The launcher intentionally does not provision or mutate those assets.

## Current POD Attempt

The most recent user-provided POD endpoint was:

```text
root@157.157.221.29 -p 22051
```

Both default SSH and explicit `~/.ssh/id_ed25519` attempts failed with:

```text
Permission denied (publickey,password).
```

Therefore the strict POD smoke debt remains open.

## Verification

Command:

```powershell
$env:PYTHONPATH='src'; py -3 -m unittest tests.goal5055_v2144_pod_smoke_remote_launcher_test tests.goal5054_v2144_external_review_packet_test tests.goal5053_v2144_release_preflight_test tests.goal5052_v2144_public_api_pod_smoke_runner_test
```

Result:

```text
Could not find platform independent libraries <prefix>
............
----------------------------------------------------------------------
Ran 12 tests in 2.891s

OK
```

The local tests are static/structural.  They verify that the launcher uses the
strict Goal5052 runner, downloads the expected JSON path, preserves claim
boundaries, and avoids destructive remote commands.  They do not prove POD
runtime success.

## Claim Boundary

Authorized:

```text
remote_pod_smoke_launcher_ready
strict_pod_smoke_command_fixed
pod_auth_still_blocked_for_latest_endpoint
```

Not authorized:

```text
strict_pod_smoke_passed
POD_CUDA_runtime_success
public_release_ready
v2_14_4_speedup_claim
true_zero_copy_claim
author_parity_claim
device_group_by_public_ready
```

## Exit Label

```text
completed_remote_pod_smoke_launcher_ready__pod_auth_still_blocked
```
