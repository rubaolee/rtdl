# Call For Review - Goal5052 v2.14.4 Public API POD Smoke Runner

Date: 2026-07-06

Review target:

```text
history/internal_docs/goal5052_v2_14_4_public_api_pod_smoke_runner_2026-07-06.md
scripts/goal5052_v2144_public_api_pod_smoke.py
scripts/goal5052_v2144_public_api_pod_smoke_runner.sh
tests/goal5052_v2144_public_api_pod_smoke_runner_test.py
```

## Requested Verdict Labels

```text
approve_goal5052_pod_smoke_runner_ready_local_partial_skip_only
revise_goal5052_before_pod_run
fail_goal5052_if_local_skip_is_presented_as_pod_success
```

## Context

Goal5052 does not retire the POD debt.  It creates the executable strict POD
smoke runner needed to retire that debt later.

The two smoke steps are:

1. public `NumbaPartnerContinuation` CUDA execution over `DeviceColumnBuffer`;
2. RayJoin app migrated public `device_order_by` native CUDA path.

## Review Questions

1. Does the Python smoke script actually exercise public
   `numba_partner_continuation(...)` and `run_numba_partner_continuation(...)`?
2. Does the RayJoin smoke exercise the migrated
   `_run_public_device_order_by_native_lexsort(...)` path rather than directly
   calling the native lexsort helper?
3. Does the strict shell runner set `RTDL_OPTIX_LIBRARY`, run on an already
   running POD, and treat skipped CUDA/OptiX checks as failure?
4. Does the local test correctly allow non-strict `partial_skip` without
   presenting it as POD success?
5. Does the JSON schema include non-authorization boundaries for speedup,
   true-zero-copy, author parity, and public `device_group_by`?
6. Should this goal close as runner-ready while keeping `POD_CUDA_runtime_success`
   unauthorized until the strict runner is actually executed on POD?

## Non-Authorization

This review must not authorize:

```text
POD_CUDA_runtime_success
public_speedup_claim
true_zero_copy_claim
author_parity_claim
device_group_by_public_ready
```
