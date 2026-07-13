# Goal4945 - Native PIP Device-Column Runtime Gate

## Status

`completed_native_pod_compile_runtime_gate__pip_device_columns_proven_on_hardware__no_speedup_claim`

Goal4945 closes the native hardware gate left open by Goal4944. Goal4944 added a generic directed point-location device-column carrier for `segment_id` and `face_id`, but local static tests could not prove that the new native ABI rebuilt and returned valid device pointers on NVIDIA hardware.

This goal is only a native compile/runtime gate. It does not start Layer 2 numeric continuation work, does not optimize RayJoin, and does not authorize performance, release, or true-zero-copy wording.

## POD Access Correction

An earlier attempt incorrectly used the default SSH key and failed:

```text
ssh -i ~/.ssh/id_ed25519 root@157.157.221.29 -p 24344
Permission denied (publickey,password).
```

The correct project POD key is:

```text
~/.ssh/id_ed25519_rtdl_codex_current_pod
```

Using that key, the POD was reachable:

```text
host: ce489c3fad22
project path: /root/rtdl_goal4937
```

## Native Build Gate

The Goal4944 source changes were synced into `/root/rtdl_goal4937` and the OptiX backend was rebuilt with:

```bash
cd /root/rtdl_goal4937
make build-optix OPTIX_PREFIX=/root/vendor/optix-dev CUDA_PREFIX=/usr/local/cuda-12.8
```

Result:

```text
build-optix: pass
rebuilt library: /root/rtdl_goal4937/build/librtdl_optix.so
```

## Runtime Fixture

The runtime fixture loaded the rebuilt backend with:

```bash
export PYTHONPATH=src
export RTDL_OPTIX_LIB=/root/rtdl_goal4937/build/librtdl_optix.so
export RTDL_OPTIX_LIBRARY=/root/rtdl_goal4937/build/librtdl_optix.so
export LD_LIBRARY_PATH=/usr/local/cuda-12.8/lib64:$LD_LIBRARY_PATH
python3 goal4945_runtime_fixture.py
```

The fixture:

1. Prepared a tiny directed point-location map.
2. Prepared three query points.
3. Called `segment_id_device_columns(prepared_points)`.
4. Called `face_id_device_columns(prepared_points)`.
5. Adapted both outputs with `device_column_row_buffer_from_point_location_id_columns(...)`.
6. Planned Numba handoff with `plan_device_column_row_buffer_partner_handoff(...)`.

## Runtime Evidence

Observed `segment_id` output:

```json
{
  "native_symbol": "rtdl_optix_prepared_directed_segment_point_location_2d_device_segment_id_columns",
  "field_name": "segment_id",
  "schema": "rtdl.optix.directed_point_location_device_id_column.v1",
  "engine_boundary": "generic_directed_point_location_id_column",
  "dtype": "uint32",
  "row_count": 3,
  "capacity": 3,
  "device_ordinal": 0,
  "device_resident": true,
  "ids_device_ptr_observed": true,
  "overflow": false,
  "true_zero_copy_claim_authorized": false,
  "public_speedup_claim_authorized": false,
  "release_authorized": false
}
```

Observed `face_id` output:

```json
{
  "native_symbol": "rtdl_optix_prepared_directed_segment_point_location_2d_device_face_id_columns",
  "field_name": "face_id",
  "schema": "rtdl.optix.directed_point_location_device_id_column.v1",
  "engine_boundary": "generic_directed_point_location_id_column",
  "dtype": "uint32",
  "row_count": 3,
  "capacity": 3,
  "device_ordinal": 0,
  "device_resident": true,
  "ids_device_ptr_observed": true,
  "overflow": false,
  "true_zero_copy_claim_authorized": false,
  "public_speedup_claim_authorized": false,
  "release_authorized": false
}
```

Both row-buffer adapters reported:

```text
source_mode: native_device_columns
device_resident_candidate: true
native_device_column_output_proven_on_hardware: true
host_rows_materialized_before_partner_handoff: false
materializes_host_rows_for_bridge: false
producer_consumer_stream_ordering: host_synchronized_before_consumer
stream_synchronization_proven: true
neutral_partner_handoff_version: rtdl.v2_6.neutral_partner_handoff.v1
handoff_status: accept
```

## Local Test Status On POD

The POD bundle did not contain `tests.goal4942_device_column_row_buffer_handoff_test`, so the three-test command could not fully reproduce the local test bundle. The synced Goal4944/Goal4943 tests executed before the missing-module error and passed.

This is not counted as a native gate failure because the missing file is a POD bundle coverage issue, not a runtime ABI failure. The full local Goal4942/Goal4943/Goal4944 bundle already passed before the native gate:

```text
Ran 15 tests in 0.034s
OK
```

## What This Proves

Goal4945 proves that the Goal4944 native path is not merely a Python/static carrier:

- `segment_id` native device-column output rebuilds and runs on NVIDIA hardware.
- `face_id` native device-column output rebuilds and runs on NVIDIA hardware.
- Both return nonzero device pointers with valid row count/capacity metadata.
- Both adapt into the generic Layer 1 row-buffer contract.
- Both are accepted by the v2.6 neutral Numba handoff planner.

## What This Does Not Prove

Goal4945 does not prove:

- Numba continuation execution over these columns.
- CuPy continuation execution over these columns.
- RayJoin whole-app acceleration.
- PIP/overlay application acceleration.
- true zero-copy in public wording.
- public release readiness.
- any Layer 2 numeric continuation.

## Exit Label

`completed_native_pod_compile_runtime_gate__pip_device_columns_proven_on_hardware__no_speedup_claim`
