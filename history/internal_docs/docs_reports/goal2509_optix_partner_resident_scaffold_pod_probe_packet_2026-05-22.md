# Goal2509 OptiX Partner-Resident Scaffold Pod Probe Packet

Date: 2026-05-22

## Summary

Goal2509 prepares the exact GPU-pod probe for the Goal2507/Goal2508
partner-resident columnar scaffold. This is not a performance run. It only
checks that a freshly built OptiX backend exports
`rtdl_optix_columnar_payload_create_from_device_columns` and returns the expected
fail-closed unsupported error when called with real CUDA partner tensors.

GPU pod required.

native execution remains unauthorized.

## Probe Script

Script:

```text
scripts/goal2509_optix_partner_resident_scaffold_probe_pod.py
```

Expected artifact:

```text
docs/reports/goal2509_optix_partner_resident_scaffold_probe_pod_2026-05-22.json
```

Observed pod artifact:

```text
docs/reports/goal2509_optix_partner_resident_scaffold_probe_pod_2026-05-22.json
```

Observed build log:

```text
docs/reports/goal2509_make_build_optix_2026-05-22.txt
```

The script creates real CUDA PyTorch tensors for:

- `row_ids`
- `region_id`
- `ship_year`
- `revenue`

It builds a Goal2505 partner-resident descriptor, calls
`prepare_optix_partner_resident_columnar_record_set(..., allow_scaffold_probe=True)`,
and requires this exact result:

```text
expected_fail_closed
```

The accepted error must include:

```text
fail-closed ABI scaffold
native execution is not implemented
```

## Pod Preconditions

Run only after the pod checkout is synchronized to the current git state and the
OptiX backend has been rebuilt.

Observed pod command:

```text
ssh root@69.30.85.198 -p 22017 -i ~/.ssh/id_ed25519_rtdl_codex
```

Expected runtime library:

```text
build/librtdl_optix.so
```

The pod command shape should be:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIB=build/librtdl_optix.so python3 scripts/goal2509_optix_partner_resident_scaffold_probe_pod.py
```

## Claim Boundary

Passing this probe does not show native execution. It shows only that the native
symbol and Python wrapper agree on the fail-closed boundary.

No speedup, zero-copy, SQL, DBMS, or RayDB whole-app claim is authorized.

## Local Validation

Focused local packet test:

```text
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest tests.goal2509_optix_partner_resident_scaffold_pod_probe_packet_test
```

Observed result:

```text
3 tests OK
```

Combined RayDB-style local validation through Goal2509:

```text
69 tests OK, 4 skipped
```

## Pod Validation

Observed command:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIB=$(pwd)/build/librtdl_optix.so python3 scripts/goal2509_optix_partner_resident_scaffold_probe_pod.py
```

Observed result:

```text
probe_status=expected_fail_closed
```

The pod artifact records:

- CUDA available: `true`
- PyTorch: `2.8.0+cu128`
- descriptor device: `cuda:0`
- descriptor source protocol: `torch`
- native symbol: `rtdl_optix_columnar_payload_create_from_device_columns`
- error contains `fail-closed ABI scaffold`

Focused pod unittest validation:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2506_optix_partner_resident_native_execution_boundary_test \
  tests.goal2507_optix_device_column_abi_scaffold_test \
  tests.goal2508_optix_partner_resident_python_scaffold_test \
  tests.goal2509_optix_partner_resident_scaffold_pod_probe_packet_test
```

Observed result:

```text
15 tests OK
```

## Next After Probe

If the probe passes, the next real engineering target is the first executable
device-side numeric slice:

- validate `RtdlDevicePayloadField` inputs in C++
- build row metadata without full table staging to host
- evaluate predicates on device
- reduce count and int64 sum on device
- copy only compact result rows back to host
