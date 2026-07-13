# Goal5056 - v2.14.4 Strict POD Smoke Result

Date: 2026-07-06

Status:

```text
completed_strict_pod_smoke_passed__release_still_blocked_by_review_debt
```

## Purpose

Goal5056 retires the strict POD smoke debt created by Goal5052.

This is a runtime/API smoke only.  It is not a performance benchmark and does
not authorize any v2.14.4 speedup, true zero-copy, author-parity, or public
`device_group_by` claim.

## POD Access

The user-provided POD endpoint was:

```text
ssh root@157.157.221.29 -p 22051
```

The default key and normal `id_ed25519` failed.  The working key was:

```text
~/.ssh/id_ed25519_rtdl_codex_current_pod
```

The remote host was:

```text
8feb86803ac4
```

GPU:

```text
NVIDIA RTX 4000 Ada Generation
Driver Version: 550.127.05
CUDA Version: 12.4
```

## Remote Checkout

The existing remote checkout `/root/rtdl_goal5036` was old and dirty, so it was
not modified or reset.

Instead, the local current HEAD was bundled and cloned into a fresh remote
checkout:

```text
/root/rtdl_goal5055_b5ef0e67f
git_head = b5ef0e67f90a6e4e3e3fea358c4bc5916500179b
```

The existing native library was reused read-only:

```text
/root/rtdl_goal5036/build/librtdl_optix.so
```

## Environment Issue Found And Fixed

The first strict run failed because the old remote venv used:

```text
numba 0.66.0
```

That stack emitted PTX 8.7 while the POD driver/toolchain accepted PTX 8.4:

```text
CUDA_ERROR_UNSUPPORTED_PTX_VERSION
Unsupported .version 8.7; current version is '8.4'
```

A fresh isolated venv was created inside the new checkout:

```text
/root/rtdl_goal5055_b5ef0e67f/.venv_goal5055
```

Installed stack:

```text
numpy==2.2.6
numba==0.61.2
nvidia-cuda-nvcc-cu12==12.4.131
nvidia-cuda-nvrtc-cu12==12.4.127
nvidia-nvjitlink-cu12==12.4.127
```

Numba still initially found `/usr/local/cuda` CUDA 12.8 NVVM.  The successful
run explicitly pointed Numba at the venv CUDA 12.4 NVVM:

```bash
export VENV=/root/rtdl_goal5055_b5ef0e67f/.venv_goal5055
export CUDA_HOME=$VENV/lib/python3.12/site-packages/nvidia/cuda_nvcc
export CUDA_PATH=$CUDA_HOME
export LD_LIBRARY_PATH=$CUDA_HOME/nvvm/lib64:${LD_LIBRARY_PATH:-}
export PATH=$CUDA_HOME/bin:$VENV/bin:$PATH
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=/root/rtdl_goal5036/build/librtdl_optix.so
```

The Goal5055 remote launcher was updated to accept these remote environment
paths as parameters for future POD runs.

## Strict Smoke Result

Command:

```bash
/bin/bash scripts/goal5052_v2144_public_api_pod_smoke_runner.sh \
  history/internal_docs/goal5052_v2144_public_api_pod_smoke_result.json
```

Result:

```text
overall_status = pass
strict = true
```

Step 1:

```text
public_numba_partner_continuation_cuda = pass
operation = uint32_equal_mask
mask = [false, true, true, false]
host_fallback_used = false
public_speedup_claim_authorized = false
true_zero_copy_claim_authorized = false
elapsed_sec = 0.7986969891935587
```

Step 2:

```text
rayjoin_public_device_order_by_native_cuda_path = pass
backend = native_thrust_lexsort_i64_f64_i64_i64
contract_version = rtdl.device_order_by.v2_14_4.public.v1
observed_order = [2, 1, 3, 0]
public_device_order_by_used = true
elapsed_sec = 0.024714553728699684
```

Local evidence file:

```text
history/internal_docs/goal5052_v2144_public_api_pod_smoke_result.json
```

## Updated Preflight State

After copying the strict POD JSON back locally and rerunning Goal5053 preflight:

```text
strict_pod_smoke = pass
overall_status = blocked_by_release_gates
remaining blocker = external_review_debt
```

The release is still blocked because external review debt remains open.

## Verification

Command:

```powershell
$env:PYTHONPATH='src'; py -3 -m unittest tests.goal5055_v2144_pod_smoke_remote_launcher_test tests.goal5054_v2144_external_review_packet_test tests.goal5053_v2144_release_preflight_test tests.goal5052_v2144_public_api_pod_smoke_runner_test
```

Result:

```text
Could not find platform independent libraries <prefix>
.............................s...........................
----------------------------------------------------------------------
Ran 57 tests in 3.116s

OK (skipped=1)
```

## Claim Boundary

Authorized:

```text
strict_pod_smoke_passed
public_numba_partner_cuda_smoke_passed
rayjoin_public_device_order_by_native_cuda_path_smoke_passed
preflight_pod_gate_passed
release_still_blocked_by_review_debt
```

Not authorized:

```text
public_release_ready
v2_14_4_speedup_claim
true_zero_copy_claim
author_parity_claim
device_group_by_public_ready
review_debt_retired
```

## Exit Label

```text
completed_strict_pod_smoke_passed__release_still_blocked_by_review_debt
```
