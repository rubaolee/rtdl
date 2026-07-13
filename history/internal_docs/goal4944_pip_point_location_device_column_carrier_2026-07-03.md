# Goal4944 - PIP Directed Point-Location Device-Column Carrier

## Status

`completed_local_static_and_python_gate__pending_native_pod_compile_runtime_gate`

Goal4944 closes the specific gap found in Goal4943: directed point-location/PIP had native prepared device-points execution, but Python could only observe `row_count`; it could not hand the produced `face_id` or `segment_id` device column into the Layer 1 row-buffer / v2.6 CuPy-Numba handoff path.

This is a Layer 1 plumbing goal. It does not optimize RayJoin application logic, does not add overlay/output-chain semantics, does not claim true zero-copy, and does not claim speedup.

## What Changed

### Native C ABI

Files:
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`

Added a generic native output record:

```cpp
struct RtdlNativePointLocationDeviceIdColumns {
    uint64_t ids_device_ptr;
    uint64_t row_count;
    uint64_t capacity;
    uint32_t overflow;
    int32_t device_ordinal;
    double traversal_seconds;
};
```

Added directed point-location ABI symbols:

```text
rtdl_optix_prepared_directed_segment_point_location_2d_device_segment_id_columns
rtdl_optix_prepared_directed_segment_point_location_2d_device_face_id_columns
```

Legacy RayJoin-CDB aliases remain present for compatibility, but the public Python path prefers the directed point-location names.

### Native Ownership Fix

Before Goal4944:
- `segment_id` device writes used `prepared_points->d_segment_ids`, so a persistent device buffer existed.
- `face_id` device writes allocated a temporary `DevPtr d_face_ids` inside the write call, then returned only `row_count`; the pointer could not safely be exposed after return.

After Goal4944:
- `PreparedRayjoinCdbPointLocationPoints2D` owns both:
  - `d_segment_ids`
  - `d_face_ids`
- `face_id` writes target `prepared_points->d_face_ids.ptr`.
- The new ABI returns the buffer pointer and metadata while lifetime remains owned by the prepared query-points handle.

No new release-owned native allocation owner was introduced.

### Python Runtime Carrier

File:
- `src/rtdsl/optix_runtime.py`

Added:
- `_RtdlNativePointLocationDeviceIdColumns`
- `OptixPointLocationDeviceIdColumnOutput`
- `PreparedOptixRayjoinCdbPointLocation2D.segment_id_device_columns(...)`
- `PreparedOptixRayjoinCdbPointLocation2D.face_id_device_columns(...)`

The old methods remain for compatibility:
- `write_segment_ids_device_points(...) -> {"row_count": ...}`
- `write_face_ids_device_points(...) -> {"row_count": ...}`

### Layer 1 Row-Buffer Adapter

File:
- `src/rtdsl/device_column_row_buffer.py`

Added:
- `device_column_row_buffer_from_point_location_id_columns(...)`

The adapter accepts only:
- `face_id`
- `segment_id`

It rejects app-specific names. It carries a single generic primitive-output id column and deliberately does not encode output chains, domain semantics, or application-specific output schema.

### Raw CUDA Column Dtype Support

File:
- `src/rtdsl/hit_stream_handoff.py`

Extended `RtdlRawCudaColumn` scalar dtype support from only `int64`/`float64` to:
- `int64`
- `uint64`
- `int32`
- `uint32`
- `float64`
- `float32`

This is needed because native point-location ids are `uint32_t`. The neutral buffer seam already understands `<u4` as `uint32`; Goal4944 only makes `RtdlRawCudaColumn` able to describe it.

## Why This Is Generic

The new carrier represents a directed point-location primitive id vector:

```text
face_id[] or segment_id[]
```

It does not expose:
- overlay chains
- author output format
- RayJoin-specific output schema
- polygon-overlap semantics
- application-specific writer state

The row-buffer module remains free of RayJoin / polygon / overlay vocabulary under the existing Goal4942 source guard.

## Verification Run

Commands:

```powershell
$env:PYTHONPATH='src'
py -m unittest tests.goal4944_pip_point_location_device_column_carrier_test tests.goal4943_lsi_pip_device_column_producer_audit_test tests.goal4942_device_column_row_buffer_handoff_test
py -m py_compile src/rtdsl/optix_runtime.py src/rtdsl/hit_stream_handoff.py src/rtdsl/device_column_row_buffer.py src/rtdsl/__init__.py
git diff --check
```

Results:

```text
Ran 15 tests in 0.034s
OK

py_compile: pass
git diff --check: pass
```

Additional probe:

```text
RtdlRawCudaColumn("x", "uint32", ...).__cuda_array_interface__["typestr"] == "<u4"
hasattr(rtdsl, "device_column_row_buffer_from_point_location_id_columns") == True
"device_column_row_buffer_from_point_location_id_columns" in rtdsl.__all__ == False
```

## Non-Blocking Existing Test Noise

The broader historical test:

```text
tests.goal3180_ray_triangle_hit_stream_typed_producer_metadata_test
```

still fails because it expects an old `docs/reports/...` file that has been moved into history and because its expected bottleneck text is stale. This is unrelated to Goal4944. It is not counted as a Goal4944 failure.

## Still Required

Because Goal4944 changes C++ native ABI/workloads, the next verification should be:

1. Build `librtdl_optix.so` on Linux/POD.
2. Load the rebuilt backend.
3. Run a tiny directed point-location fixture:
   - prepare directed segments
   - prepare query points
   - call `face_id_device_columns(...)`
   - call `segment_id_device_columns(...)`
   - wrap each with `device_column_row_buffer_from_point_location_id_columns(...)`
   - plan a `numba` neutral handoff
4. Confirm row-count / pointer / dtype metadata.

Until that native gate passes, the status is local-static/Python complete, not hardware-proven.

## Not Authorized

Goal4944 does not authorize:
- RayJoin application speedup claims
- whole-app speedup claims
- true-zero-copy wording
- public release wording
- overlay/output-chain semantics in RTDL core
- any claim that a Numba continuation has executed over the PIP ids
