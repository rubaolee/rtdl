# Goal2748 Triton Group-ID Device Error Flag

Date: 2026-05-30

Status: implemented and pod-smoked

## Purpose

Goal2743 intentionally froze a debt item in the v2.5 Triton continuation
preview: grouped operations rejected invalid `group_ids` through a Torch CUDA
predicate followed by a host scalar read. That is correct and fail-closed, but
it is not a device-resident error-flag path and it must not be described as
zero-copy validation.

Goal2748 adds the first generic device-resident validation helper while keeping
the public claim boundary conservative.

## Code Changes

- Added `TRITON_GROUP_ID_BOUNDS_DEVICE_FLAG_I64_OPERATION`.
- Added `describe_triton_group_id_bounds_device_flag_i64()`.
- Added `run_triton_group_id_bounds_device_flag_i64(group_ids, group_count=...)`.
- Added `assert_triton_group_ids_in_bounds_device_flag_i64(...)`.
- Added an opt-in grouped-operation mode:
  `TRITON_GROUP_ID_BOUNDS_DEVICE_FLAG_HOST_RAISE_MODE`.
- Exposed the new descriptor, constants, and helpers from `rtdsl.__init__`.
- Updated the Goal2743 boundary test so default grouped operations now disclose:
  a device-error-flag helper is available, but the default strict Python
  exception path still uses the original host scalar sync.

## Contract

The new helper writes one CUDA/Triton `invalid_count:int64[1]` device tensor.

Two modes are now explicit:

| Mode | Host scalar sync | Purpose | Claim boundary |
| --- | ---: | --- | --- |
| `triton_device_error_flag_no_host_read` | no | Produce a device-side invalid-count flag for future device-resident continuation planning. | Not a Python exception path by itself; not a zero-copy public claim. |
| `triton_device_error_flag_host_scalar_raise` | yes | Read the device flag to preserve fail-closed Python `ValueError` behavior. | Correctness enforcement only; not zero-copy validation. |

The existing default remains:
`torch_cuda_precheck_host_scalar_sync`.

## Pod Evidence

Pod command:

```bash
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so
timeout 240 python3 -m unittest \
  tests.goal2748_triton_group_id_device_error_flag_test \
  tests.goal2743_triton_group_id_validation_boundary_test \
  tests.goal2662_v2_5_partner_continuation_contract_test
```

Result:

```text
Ran 18 tests in 1.093s
OK
```

Additional explicit pod smoke:

```json
{
  "counts": [1, 2, 1],
  "invalid_count": 2,
  "flag_validation": {
    "mode": "triton_device_error_flag_no_host_read",
    "uses_host_scalar_sync": false,
    "device_error_flag_available": true,
    "true_zero_copy_claim_authorized": false
  },
  "host_raise_validation": {
    "mode": "triton_device_error_flag_host_scalar_raise",
    "uses_host_scalar_sync": true,
    "device_error_flag_available": true,
    "device_error_flag_used": true,
    "true_zero_copy_claim_authorized": false
  },
  "promoted_performance_path": false,
  "rt_core_speedup_claim_authorized": false
}
```

## Local Evidence

Windows local command:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest `
  tests.goal2748_triton_group_id_device_error_flag_test `
  tests.goal2743_triton_group_id_validation_boundary_test `
  tests.goal2662_v2_5_partner_continuation_contract_test
```

Result:

```text
Ran 18 tests in 0.007s
OK (skipped=2)
```

The two skipped tests are the CUDA/Triton runtime checks, expected on this
Windows shell.

## Remaining Boundary

This goal does not promote the Triton preview to a release performance path.
It does not authorize true zero-copy wording. Python exceptions still require a
host scalar read when strict fail-closed behavior is requested.

The next hardening steps remain:

- event/stream ordering between native OptiX producers and Triton consumers
  without device-wide synchronization;
- using device error flags inside a larger device-resident continuation plan
  instead of reading them immediately for Python exceptions;
- broader multi-driver and multi-GPU validation before any release claim.
