# Goal5057 - v2.14.4 POD Environment Bootstrap

Date: 2026-07-06

Status:

```text
completed_pod_env_bootstrap_verified__strict_smoke_passed
```

## Purpose

Goal5057 turns the POD environment fix discovered during Goal5056 into
repeatable scripts.

The problem was not the user's POD.  The POD was reachable with the correct key.
The failure was a runtime-toolchain mismatch:

```text
system /usr/local/cuda -> CUDA 12.8 NVVM emitted PTX 8.7
POD driver/toolchain -> CUDA 12.4 / PTX 8.4 support
Numba CUDA smoke -> CUDA_ERROR_UNSUPPORTED_PTX_VERSION
```

The successful manual fix was:

```text
use an isolated venv with Numba + CUDA 12.4 Python packages
force CUDA_HOME/CUDA_PATH/LD_LIBRARY_PATH/PATH to that venv CUDA NVVM
then run the strict Goal5052 smoke
```

Goal5057 makes that a scripted path and verifies it on the POD.

## Added / Updated Files

```text
scripts/goal5057_v2144_pod_env_bootstrap.sh
scripts/goal5057_v2144_strict_pod_smoke_with_env.sh
scripts/goal5055_run_v2144_pod_smoke_remote.ps1
tests/goal5057_v2144_pod_env_bootstrap_test.py
tests/goal5055_v2144_pod_smoke_remote_launcher_test.py
```

## Bootstrap Contract

`scripts/goal5057_v2144_pod_env_bootstrap.sh`:

1. creates or reuses a POD-local venv;
2. installs pinned CUDA-compatible packages:

```text
numpy==2.2.6
numba==0.61.2
nvidia-cuda-nvcc-cu12==12.4.131
nvidia-cuda-nvrtc-cu12==12.4.127
nvidia-nvjitlink-cu12==12.4.127
```

3. locates the venv `nvidia/cuda_nvcc` root;
4. writes `history/internal_docs/goal5057_v2144_pod_env_exports.sh`;
5. runs a minimal Numba CUDA kernel and writes
   `history/internal_docs/goal5057_v2144_pod_env_bootstrap_result.json`.

The exported environment includes:

```bash
export CUDA_HOME=...
export CUDA_PATH=...
export LD_LIBRARY_PATH=.../nvvm/lib64:${LD_LIBRARY_PATH:-}
export PATH=.../bin:.../cuda_nvcc/bin:${PATH}
```

This is the key fix: Numba must load the CUDA 12.4 NVVM from the venv, not the
system CUDA 12.8 NVVM.

## One-Command Strict Smoke

`scripts/goal5057_v2144_strict_pod_smoke_with_env.sh`:

1. runs the environment bootstrap;
2. sources the generated exports;
3. runs `scripts/goal5052_v2144_public_api_pod_smoke_runner.sh` in strict mode.

## Remote Launcher Update

`scripts/goal5055_run_v2144_pod_smoke_remote.ps1` now supports:

```powershell
-BootstrapPodEnv
```

When this switch is present, the remote launcher uses the Goal5057 bootstrap
path instead of requiring the caller to remember the CUDA/Numba environment
variables manually.

## Claim Boundary

Authorized:

```text
pod_env_bootstrap_script_ready
cuda_12_4_numba_env_contract_scripted
remote_launcher_can_use_bootstrap_path
pod_env_bootstrap_verified_on_pod
strict_pod_smoke_passed_through_bootstrap_path
```

Not authorized:

```text
public_release_ready
v2_14_4_speedup_claim
true_zero_copy_claim
author_parity_claim
device_group_by_public_ready
```

## Verification

Command:

```powershell
$env:PYTHONPATH='src'; py -3 -m unittest tests.goal5057_v2144_pod_env_bootstrap_test tests.goal5056_v2144_strict_pod_smoke_result_test tests.goal5055_v2144_pod_smoke_remote_launcher_test tests.goal5054_v2144_external_review_packet_test tests.goal5053_v2144_release_preflight_test tests.goal5052_v2144_public_api_pod_smoke_runner_test tests.goal5051_v2144_api_consolidation_closeout_packet_test tests.goal5050_v2144_public_private_boundary_audit_test tests.goal5049_rayjoin_public_v2144_surface_migration_test tests.goal5048_non_rayjoin_numba_partner_public_api_genericity_test tests.goal5047_numba_partner_continuation_public_api_test tests.goal5046_device_group_by_public_readiness_decision_test tests.goal5045_public_device_order_by_contract_test tests.goal5044_public_prepared_geometry_session_contract_test tests.goal5043_public_device_column_buffer_contract_test
```

Result:

```text
Could not find platform independent libraries <prefix>
..................................s...........................
----------------------------------------------------------------------
Ran 62 tests in 3.214s

OK (skipped=1)
```

## POD Runtime Verification

The scripted Goal5057 path was run on the POD:

```bash
cd /root/rtdl_goal5055_b5ef0e67f
export RTDL_OPTIX_LIBRARY=/root/rtdl_goal5036/build/librtdl_optix.so
bash scripts/goal5057_v2144_strict_pod_smoke_with_env.sh \
  history/internal_docs/goal5052_v2144_public_api_pod_smoke_result.json
```

Result:

```text
goal5057_v2144_pod_env_bootstrap_result.json:
  overall_status = pass
  numba_version = 0.61.2
  numpy_version = 2.2.6
  ptxas = CUDA 12.4, V12.4.131
  minimal_cuda_kernel_result = [2]

goal5052_v2144_public_api_pod_smoke_result.json:
  strict = true
  overall_status = pass
  public_numba_partner_continuation_cuda = pass
  rayjoin_public_device_order_by_native_cuda_path = pass
```

## Next

Run the new bootstrap path on the POD:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/goal5055_run_v2144_pod_smoke_remote.ps1 `
  -HostName 157.157.221.29 `
  -Port 22051 `
  -IdentityFile "$env:USERPROFILE\.ssh\id_ed25519_rtdl_codex_current_pod" `
  -RemoteRepo "/root/rtdl_goal5055_b5ef0e67f" `
  -RemoteRtdlOptixLibrary "/root/rtdl_goal5036/build/librtdl_optix.so" `
  -BootstrapPodEnv
```

## Exit Label

```text
completed_pod_env_bootstrap_verified__strict_smoke_passed
```
