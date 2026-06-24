# Goal2510 OptiX Device-Column ABI Validation

Date: 2026-05-22

## Summary

Goal2510 strengthens the Goal2507 fail-closed native symbol. The symbol now does
ABI validation before returning the unsupported execution error. This is still
not native execution.

native execution remains unauthorized.

## Native Validation Added

The native scaffold now checks:

- at least one field
- nonzero row count
- non-empty field names
- CUDA device-column descriptors only
- nonzero `device_ptr`
- each field length matches `row_count`
- all fields are on the same CUDA device
- dtype is one of `int64`, `uint32`, or `float64`
- logical kind matches dtype
- contiguous stride only
- exactly one `row_id` field is present

The expected success-through-validation error now includes:

```text
device-column descriptors validated
partner-resident columnar native execution is not implemented
```

## Header Constants

The native header now exposes public DB kind constants:

- `kRtdlDbKindInt64`
- `kRtdlDbKindFloat64`
- `kRtdlDbKindBool`
- `kRtdlDbKindText`

These pair with the device payload constants introduced in Goal2507.

## Claim Boundary

This goal validates descriptor shape only. It does not build an OptiX accel,
does not evaluate predicates, does not reduce on device, and does not authorize
speedup or zero-copy claims.

The path is still fail-closed.

## Tests

Focused local validation:

```text
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest tests.goal2510_optix_device_column_abi_validation_test
```

Expected result:

```text
4 tests OK
```

Observed local result:

```text
4 tests OK
```

Combined RayDB-style local validation through Goal2510:

```text
73 tests OK, 4 skipped
```

## Pod Validation

Observed pod command:

```text
ssh root@69.30.85.198 -p 22017 -i ~/.ssh/id_ed25519_rtdl_codex
```

Observed build log:

```text
docs/reports/goal2510_make_build_optix_2026-05-22.txt
```

Observed CUDA validation artifact:

```text
docs/reports/goal2510_optix_partner_resident_validation_probe_pod_2026-05-22.json
```

Observed result:

```text
probe_status=expected_fail_closed
```

The pod artifact records that real CUDA PyTorch descriptors reached native ABI
validation and then failed closed with:

```text
device-column descriptors validated
partner-resident columnar native execution is not implemented
```

Focused pod unittest validation:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2506_optix_partner_resident_native_execution_boundary_test \
  tests.goal2507_optix_device_column_abi_scaffold_test \
  tests.goal2508_optix_partner_resident_python_scaffold_test \
  tests.goal2509_optix_partner_resident_scaffold_pod_probe_packet_test \
  tests.goal2510_optix_device_column_abi_validation_test
```

Observed result:

```text
19 tests OK
```

## Next Target

The next pod step is to rebuild the OptiX backend again and rerun Goal2509. The
expected pod error should now include `device-column descriptors validated`,
proving that real CUDA descriptors passed native ABI validation before execution
was rejected.
