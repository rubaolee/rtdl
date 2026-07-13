# Goal5052 - v2.14.4 Public API POD Smoke Runner

Date: 2026-07-06

Status:

```text
completed_pod_smoke_runner_ready__local_non_strict_smoke_partial_skip
```

## Purpose

Goal5052 turns the open v2.14.4 POD debts into an executable smoke runner.

The runner checks:

1. public `NumbaPartnerContinuation` can execute a CUDA continuation over a
   `DeviceColumnBuffer`;
2. the RayJoin Section 5.7 app path migrated in Goal5049 can execute its public
   `device_order_by` native CUDA route.

This goal does not run a POD.  It prepares the exact POD command and validates
that the local non-strict path writes machine-readable evidence.

## Added Files

```text
scripts/goal5052_v2144_public_api_pod_smoke.py
scripts/goal5052_v2144_public_api_pod_smoke_runner.sh
tests/goal5052_v2144_public_api_pod_smoke_runner_test.py
```

## Smoke Steps

### Step 1 - Public Numba partner continuation CUDA smoke

The script creates a CUDA `uint32` device column:

```text
values = [1, 7, 7, 3]
```

Then runs:

```text
DeviceColumnBuffer -> numba_partner_continuation(uint32_equal_mask) -> run
```

Expected output:

```text
[False, True, True, False]
```

### Step 2 - RayJoin migrated public device_order_by path

The script imports the RayJoin Section 5.7 binary app and calls the migrated
helper:

```text
_run_public_device_order_by_native_lexsort(...)
```

That helper uses:

```text
DeviceColumnBuffer -> device_order_by(..., backend="native_cuda")
```

Expected sorted order:

```text
[2, 1, 3, 0]
```

## POD Command

On an already-running RTX-class Linux POD:

```bash
export PYTHONPATH="${PYTHONPATH:-src:.}"
export RTDL_OPTIX_LIBRARY="${RTDL_OPTIX_LIBRARY:-$(pwd)/build/librtdl_optix.so}"
bash scripts/goal5052_v2144_public_api_pod_smoke_runner.sh
```

The runner uses `--strict`.  In strict mode, skipped CUDA/OptiX smoke steps fail
the run.

## Local Verification

Command:

```powershell
$env:PYTHONPATH="src"; py -3 -m unittest tests.goal5052_v2144_public_api_pod_smoke_runner_test
```

Result:

```text
Could not find platform independent libraries <prefix>
...
----------------------------------------------------------------------
Ran 3 tests in 0.593s

OK
```

The local test invokes the Python smoke script without `--strict`.  Local
machines without CUDA/OptiX may return:

```text
overall_status = partial_skip
```

This is expected locally and does not satisfy POD debt.

## Claim Boundary

Authorized:

```text
pod_smoke_runner_ready
local_non_strict_json_smoke_writes_machine_readable_evidence
strict_pod_runner_available
```

Not authorized:

```text
POD_CUDA_runtime_success
public_speedup_claim
true_zero_copy_claim
author_parity_claim
device_group_by_public_ready
```

## Next

Run the strict runner on a POD and attach the resulting JSON before using
Goal5047/5049 as runtime-backed evidence in any user-facing v2.14.4 release
note.
