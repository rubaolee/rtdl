# Goal4943 - LSI/PIP Device-Column Producer Audit

Date: 2026-07-04

## Verdict Requested

`completed_lsi_producer_adapter__pip_pointer_carrier_gap_recorded`

## Objective

After Goal4942 created a generic `RtdlDeviceColumnRowBuffer` carrier, audit whether the RayJoin-relevant public primitives already have compatible device-column producers.

Scope:

- LSI / segment-pair intersection pair-id output
- PIP / directed segment point-location face/segment-id output

This goal is a producer audit plus one narrow adapter. It does **not** claim speedup, true zero-copy, or full RayJoin pipeline residency.

## Findings

### LSI / Segment-Pair

LSI already had a real Python-visible native device-column producer:

- Native symbol:
  - `rtdl_optix_prepared_segment_pair_candidate_device_columns`
- Python route:
  - `PreparedOptixSegmentPairIntersector2D.candidate_device_columns(...)`
- Output object:
  - `OptixNativeDevicePairColumnOutput`
- Device columns:
  - `left_ids_device_ptr`
  - `right_ids_device_ptr`
- Existing metadata:
  - row count
  - capacity
  - overflow
  - candidate event count
  - device ordinal
  - native symbol
  - traversal seconds

Goal4943 added:

- `device_column_row_buffer_from_native_pair_columns(...)`

This adapts `OptixNativeDevicePairColumnOutput` to the generic Goal4942 `RtdlDeviceColumnRowBuffer`:

```text
OptixNativeDevicePairColumnOutput(left_ids_device_ptr, right_ids_device_ptr)
  -> RtdlRawCudaColumn("left_id", ...)
  -> RtdlRawCudaColumn("right_id", ...)
  -> RtdlDeviceColumnRowBuffer
  -> v2.6 neutral partner handoff
```

This closes the Layer 1 carrier gap for generic LSI pair-id candidate columns.

Boundary:

- This does **not** make full exact witness rows device-resident.
- `run_pair_id_rows(...)` still returns a host `OptixRowView`.
- The device-resident route is specifically the native pair-column producer, not every LSI route.

### PIP / Directed Segment Point-Location

PIP already has native device-column-ish symbols:

- `rtdl_optix_count_prepared_directed_segment_point_location_2d_device_points`
- `rtdl_optix_write_prepared_directed_segment_point_location_2d_device_segment_ids`
- `rtdl_optix_write_prepared_directed_segment_point_location_2d_device_face_ids`

and RayJoin-compatible aliases:

- `rtdl_optix_count_prepared_rayjoin_cdb_point_location_2d_device_points`
- `rtdl_optix_write_prepared_rayjoin_cdb_point_location_2d_device_segment_ids`
- `rtdl_optix_write_prepared_rayjoin_cdb_point_location_2d_device_face_ids`

But the current Python methods:

- `PreparedOptixRayjoinCdbPointLocation2D.count_positive_faces_device_points(...)`
- `PreparedOptixRayjoinCdbPointLocation2D.write_segment_ids_device_points(...)`
- `PreparedOptixRayjoinCdbPointLocation2D.write_face_ids_device_points(...)`

return only scalar/count metadata such as:

```python
{"row_count": int(point_count.value)}
```

They do **not** expose:

- face-id device pointer
- segment-id device pointer
- owner/lifetime object
- reusable output buffer handle
- `RtdlRawCudaColumn`
- `RtdlDeviceColumnRowBuffer`

Therefore PIP is not complete for Layer 1 producer residency. It has native internal device writes/counts, but no Python-level pointer carrier that can be borrowed by Numba/CuPy continuation through Goal4942.

## Code Added / Updated

Updated:

- `src/rtdsl/device_column_row_buffer.py`
  - added `device_column_row_buffer_from_native_pair_columns(...)`

- `src/rtdsl/__init__.py`
  - imported `device_column_row_buffer_from_native_pair_columns` for explicit access
  - kept it out of `rtdsl.__all__`

Updated tests:

- `tests/goal4942_device_column_row_buffer_handoff_test.py`
  - added `test_native_lsi_pair_columns_can_be_adapted_to_generic_row_buffer`

New tests:

- `tests/goal4943_lsi_pip_device_column_producer_audit_test.py`
  - asserts LSI has Python-visible native pair-column producer and Layer 1 adapter
  - asserts PIP has native device symbols but no Python pointer carrier yet
  - preserves no-speedup/no-zero-copy boundary

## Verification

Command:

```powershell
$env:PYTHONPATH='src'; py -m unittest tests.goal4942_device_column_row_buffer_handoff_test tests.goal4943_lsi_pip_device_column_producer_audit_test tests.goal2990_v2_6_neutral_partner_handoff_test tests.goal4941_layer2_numba_columnar_continuations_test
```

Result:

```text
Ran 21 tests in 0.027s
OK (skipped=2)
```

Command:

```powershell
$env:PYTHONPATH='src'; py -m unittest tests.goal2685_device_resident_hit_stream_handoff_test tests.goal2708_hit_stream_cuda_array_torch_carrier_adapter_test tests.goal4942_device_column_row_buffer_handoff_test tests.goal4943_lsi_pip_device_column_producer_audit_test
```

Result:

```text
Ran 31 tests in 18.826s
OK (skipped=2)
```

The second run emitted existing optional Embree build warnings/linker diagnostics during runtime probing, but unittest result was `OK`.

## Interpretation

Goal4943 improves Layer 1 status from:

```text
carrier exists, producer status unknown
```

to:

```text
LSI pair-id device-column producer: carrier-compatible
PIP face/segment-id device output: native symbols exist, Python pointer carrier missing
```

This is the right next cut: close the part that is already supported, and explicitly record the part that is still a real product gap.

## Next Goal

Goal4944 should target the PIP gap:

> expose a generic directed-point-location device-column output carrier for face/segment IDs, reusing the existing native device write/count path and the Goal4942 row-buffer carrier, without RayJoin-specific schema names and without true-zero-copy/speedup claims.

Exit should require:

- Python object with device pointer(s), row count, owner/lifetime, native symbol, and phase timing.
- `RtdlRawCudaColumn` or equivalent neutral descriptor for `point_id` plus `face_id` or `segment_id`.
- `RtdlDeviceColumnRowBuffer` adapter.
- v2.6 neutral handoff acceptance for Numba.
- fail-closed behavior for missing native symbols or missing pointers.

## Exit Label

`completed_lsi_producer_adapter__pip_pointer_carrier_gap_recorded`
