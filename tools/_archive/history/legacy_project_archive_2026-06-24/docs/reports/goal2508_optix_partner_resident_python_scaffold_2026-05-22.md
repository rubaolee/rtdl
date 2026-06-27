# Goal2508 OptiX Partner-Resident Python Scaffold

Date: 2026-05-22

## Summary

Goal2508 connects the Goal2507 native device-column ABI scaffold to the Python
OptiX runtime without authorizing execution. The new Python entry point is:

```python
prepare_optix_partner_resident_columnar_record_set(...)
```

It fails before backend load by default. This is intentional: Goal2505
partner-resident descriptors are metadata only, and the Goal2507 native symbol is
a fail-closed ABI scaffold.

native execution remains unauthorized.

## Runtime Surface

Added exported symbol:

```python
OPTIX_PARTNER_RESIDENT_COLUMNAR_DEVICE_SYMBOL = "rtdl_optix_columnar_payload_create_from_device_columns"
```

Added Python ctypes struct:

```python
class _RtdlDevicePayloadField(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("kind", ctypes.c_uint32),
        ("dtype", ctypes.c_uint32),
        ("device_type", ctypes.c_uint32),
        ("device_id", ctypes.c_uint32),
        ("element_count", ctypes.c_size_t),
        ("stride_bytes", ctypes.c_size_t),
        ("device_ptr", ctypes.c_uint64),
    ]
```

Added optional native symbol registration:

```python
ctypes.POINTER(_RtdlDevicePayloadField)
```

Added device descriptor encoder:

```python
_encode_partner_resident_device_payload_fields(...)
```

The encoder preserves device pointers and column metadata. It does not copy
column values into host row mappings.

## Fail-Closed Behavior

The public Python entry point raises unless called with
`allow_scaffold_probe=True`. Default behavior does not load the OptiX library and
does not call the native symbol. This prevents a user from accidentally treating
the scaffold as an executable path.

With `allow_scaffold_probe=True`, the wrapper may call the native symbol only to
verify that the compiled backend returns the expected fail-closed unsupported
error. This mode is a scaffold probe only, not an execution API.

## Claim Boundary

No speedup, zero-copy, SQL, DBMS, or whole-app RayDB claim is authorized.

Allowed wording:

- RTDL can encode partner-resident CUDA column descriptors for the future OptiX
  device-column ABI.
- Python and native OptiX scaffolds both fail closed.

Forbidden wording:

- RTDL executes partner-resident columnar payloads natively.
- RTDL has true zero-copy RayDB-style execution.
- RTDL has a complete database engine.

## Tests

Focused local validation:

```text
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest tests.goal2508_optix_partner_resident_python_scaffold_test
```

Expected result:

```text
5 tests OK
```

Combined RayDB-style local validation through Goal2508:

```text
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest \
  tests.goal2497_raydb_style_embree_count_sum_parity_test \
  tests.goal2498_raydb_style_optix_count_sum_parity_test \
  tests.goal2499_raydb_style_lowering_plan_test \
  tests.goal2500_raydb_style_backend_matrix_runner_test \
  tests.goal2501_raydb_style_optix_pod_results_test \
  tests.goal2502_raydb_style_benchmark_slice_closeout_test \
  tests.goal2503_direct_columnar_record_set_preparation_test \
  tests.goal2504_columnar_typed_host_buffer_handoff_test \
  tests.goal2505_partner_resident_columnar_descriptor_contract_test \
  tests.goal2506_optix_partner_resident_native_execution_boundary_test \
  tests.goal2507_optix_device_column_abi_scaffold_test \
  tests.goal2508_optix_partner_resident_python_scaffold_test
```

Observed result:

```text
66 tests OK, 4 skipped
```

## Next Target

The next target that likely needs a GPU pod is a compiled fail-closed symbol
probe: build the OptiX backend, call
`prepare_optix_partner_resident_columnar_record_set(..., allow_scaffold_probe=True)`
with real CUDA partner tensors, and record that the backend exports the symbol
and returns the explicit unsupported error.
