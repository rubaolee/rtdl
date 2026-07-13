# Goal4946 - Native Device Columns To Numba Execution

## Status

`completed_native_pip_device_columns_to_generic_numba_execution__no_speedup_claim`

Goal4946 is the first actual producer-to-Layer-2 execution gate after the Layer 1/2 split:

```text
RTDL native primitive producer
  -> generic device-column row-buffer
  -> v2.6 neutral Numba handoff
  -> generic Numba numeric continuation execution
```

This goal deliberately does not optimize RayJoin and does not claim any app speedup. It proves that hardware-produced native device columns can be consumed by a generic Numba continuation without first materializing Python rows for the handoff.

## Why This Goal Was Needed

Goal4941 already created generic Layer 2 Numba CUDA continuations, but those continuations ran on caller-supplied device arrays.

Goal4942 defined the generic Layer 1 device-column row-buffer carrier.

Goal4944/Goal4945 proved that directed point-location/PIP can produce `segment_id` and `face_id` native device columns on hardware.

The remaining gap was execution:

```text
native PIP device id column -> row-buffer -> Numba continuation
```

Goal4946 closes that gap with one small, generic continuation.

## Implementation

Added a generic Numba preview operation:

```text
uint32_equal_mask
```

Contract:

```text
input column: values:uint32
scalar input: target:uint32
output:       mask:bool
behavior:     mask[i] = values[i] == target
```

Files changed:

- `src/rtdsl/partner_continuation_protocol.py`
- `src/rtdsl/numba_partner_continuation.py`
- `src/rtdsl/__init__.py`
- `tests/goal4946_native_device_columns_numba_execution_test.py`

This operation is intentionally app-neutral:

- no RayJoin naming
- no overlay/output-chain semantics
- no polygon or paper-reproduction vocabulary
- no app-specific schema
- no user raw kernel
- no traversal replacement

It is a generic `uint32` id-column filter. PIP `face_id` is only the first hardware producer used to validate the chain.

## Local Verification

Commands:

```powershell
$env:PYTHONPATH='src'
py -m unittest tests.goal4946_native_device_columns_numba_execution_test `
  tests.goal4941_layer2_numba_columnar_continuations_test `
  tests.goal4944_pip_point_location_device_column_carrier_test

py -m py_compile src/rtdsl/partner_continuation_protocol.py `
  src/rtdsl/numba_partner_continuation.py src/rtdsl/__init__.py `
  tests/goal4946_native_device_columns_numba_execution_test.py
```

Result:

```text
Ran 14 tests in 0.027s
OK (skipped=4)

py_compile: pass
```

The skipped tests are CUDA execution tests on the local Windows environment. They are expected to run on the POD.

## Post-Review Reference Fallback Amendment

Antigravity approved the Goal4946 preview execution gate and identified one non-blocking completeness gap: `execute_v2_5_partner_continuation_reference(...)` did not yet have a Python reference fallback branch for `uint32_equal_mask`.

That gap has been fixed in this goal:

- `execute_v2_5_partner_continuation_reference("uint32_equal_mask", ...)` now returns the same generic boolean mask contract.
- The reference path validates that `values` and `target` fit `uint32`.
- `tests/goal4946_native_device_columns_numba_execution_test.py` now covers the reference fallback and out-of-range validation.

This amendment does not change the claim boundary. The Numba/CUDA path remains preview-only and no performance or release claim is authorized.

## POD Verification

POD:

```text
host: 157.157.221.29:24344
key: ~/.ssh/id_ed25519_rtdl_codex_current_pod
container: ce489c3fad22
project path: /root/rtdl_goal4937
```

POD focused tests:

```bash
cd /root/rtdl_goal4937
export PYTHONPATH=src
export RTDL_OPTIX_LIB=/root/rtdl_goal4937/build/librtdl_optix.so
export RTDL_OPTIX_LIBRARY=/root/rtdl_goal4937/build/librtdl_optix.so
export LD_LIBRARY_PATH=/usr/local/cuda-12.8/lib64:$LD_LIBRARY_PATH
python3 -m unittest \
  tests.goal4946_native_device_columns_numba_execution_test \
  tests.goal4941_layer2_numba_columnar_continuations_test
```

Initial result before the reference-fallback amendment:

```text
Ran 8 tests in 0.887s
OK
```

After adding the `uint32_equal_mask` Python reference fallback branch and tests, the same POD suite was rerun:

```text
Ran 10 tests in 0.854s
OK
```

The CUDA warning about grid size 1 is expected for the tiny correctness fixture. It is not a performance measurement.

## Native Producer To Numba Runtime Fixture

The final runtime fixture used the rebuilt Goal4945 backend and a tiny directed point-location scene:

1. Prepared four directed segments.
2. Prepared three query points.
3. Produced a native `face_id` device column with `face_id_device_columns(...)`.
4. Adapted it through `device_column_row_buffer_from_point_location_id_columns(...)`.
5. Planned the v2.6 neutral Numba handoff.
6. Executed:

```python
rt.run_numba_uint32_equal_mask(face_rb.columns["face_id"], target=100)
```

Observed result:

```json
{
  "native_symbol": "rtdl_optix_prepared_directed_segment_point_location_2d_device_face_id_columns",
  "row_count": 3,
  "ids_device_ptr_observed": true,
  "row_buffer_source_mode": "native_device_columns",
  "handoff_status": "accept",
  "numba_operation": "uint32_equal_mask",
  "numba_partner": "numba",
  "mask_values": [true, true, false],
  "mask_true_count": 2,
  "host_column_materialization_used": false,
  "app_specific_semantics_allowed": false,
  "public_speedup_claim_authorized": false,
  "true_zero_copy_claim_authorized": false
}
```

This proves that the `RtdlRawCudaColumn` view produced from native point-location output is accepted by Numba through `__cuda_array_interface__` and that the Numba continuation executed over the native device column.

The post-amendment fixture also checked the Python reference fallback:

```json
{
  "reference_fallback_check": [true, false, true]
}
```

## What This Solves

Goal4946 proves the Layer 1/2 bridge in executable form:

- native producer output is not just planned;
- a generic Numba continuation can consume it;
- no Python host rows are materialized before handoff;
- the operation remains app-neutral;
- no new partner API was invented.

## What This Does Not Solve

Goal4946 does not prove:

- RayJoin whole-app speedup;
- PIP app speedup;
- LSI app speedup;
- Layer 3 writer improvement;
- true zero-copy in public wording;
- release readiness;
- broad Numba partner superiority.

The fixture copies the final mask to host for test validation. That validation copy is not part of a public hot-path claim.

## Exit Label

`completed_native_pip_device_columns_to_generic_numba_execution__no_speedup_claim`
