# Call For Review - Goal4944 PIP Directed Point-Location Device-Column Carrier

Please review:

`history/internal_docs/goal4944_pip_point_location_device_column_carrier_2026-07-03.md`

## Requested Verdict

One of:

- `approve_goal4944_local_gate_passed_authorize_native_pod_gate`
- `approve_with_required_amendments`
- `block_goal4944_as_app_specific_or_unsafe_lifetime`

## Review Questions

1. Does Goal4944 correctly close the Goal4943 PIP pointer-carrier gap without smuggling overlay/RayJoin output semantics into the Layer 1 row-buffer?
2. Is the native lifetime model correct: `segment_id` and `face_id` buffers are owned by the prepared query-points handle, with no separate hidden release owner?
3. Is it valid to make `face_id` persistent inside `PreparedRayjoinCdbPointLocationPoints2D` rather than returning a pointer to a temporary `DevPtr`?
4. Is the new C ABI generic enough under the name `directed_segment_point_location_2d_device_*_id_columns`, despite legacy RayJoin-CDB aliases remaining for compatibility?
5. Is extending `RtdlRawCudaColumn` to scalar `uint32`/`int32`/`uint64`/`float32` appropriate and consistent with the existing neutral-buffer seam?
6. Does the Python `OptixPointLocationDeviceIdColumnOutput` + `device_column_row_buffer_from_point_location_id_columns(...)` route preserve claim boundaries: no speedup, no true-zero-copy, no release claim?
7. Are the local static/Python tests sufficient to authorize a native POD compile/runtime gate?
8. Should any additional tiny hardware fixture be required before Goal4944 closes fully?

## Boundary Reminder

This review is not about RayJoin overlay correctness, paper reproduction claims, or performance. It is only about whether the PIP directed point-location primitive can now expose generic device-resident id columns to the Layer 1 row-buffer / v2.6 partner handoff path.
