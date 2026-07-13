# Goal4974: Directed Point-Location Face-ID Device Columns for RayJoin Binary Operator

Date: 2026-07-04

## Purpose

Goal4973 showed that, after exact LSI setup is separated from steady-state replay, the writer-free RayJoin binary route is dominated by downstream work rather than by LSI traversal:

- vertex PIP / point-location, especially map1-in-map0
- midpoint point generation and midpoint PIP
- reprojection / sort / grouping

Goal4974 tests one specific generic Layer 1/2 question: can the directed point-location primitive produce `face_id` as a device-resident column and hand it to the binary route without materializing full point-location rows first?

## Boundary

This is a generic RTDL primitive-output-column route, not a RayJoin-specific kernel.

Allowed:

- Use existing directed point-location/PIP device-id column APIs.
- Add a RayJoin app flag that chooses `face_id_device_columns()` instead of `run_point_location()`.
- Copy device `face_id` columns to NumPy only where the current downstream app still requires NumPy arrays, and report that copy cost explicitly.
- Record Layer-1 row-buffer metadata via `device_column_row_buffer_from_point_location_id_columns`.
- Compare the same RayJoin top4 representative input against the existing rows path.

Forbidden:

- No RayJoin output-chain semantics in RTDL core.
- No app-specific schema in the generic row buffer.
- No “true zero-copy” or broad speedup claim.
- No hiding device-to-host copies inside a hot-path headline.
- No changing correctness comparators.

## Work

1. Add a `--point-location-device-face-columns` route to `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`.
2. For vertex PIP:
   - prepare query points
   - call `face_id_device_columns()`
   - record row-buffer metadata
   - copy the `uint32 face_id` column to NumPy for current downstream compatibility
3. For midpoint PIP:
   - reuse the same route for scaled midpoint points
   - preserve owner indexing and assignment semantics
4. Add focused local tests for:
   - generic row-buffer accepts point-location face columns
   - app route metadata is bounded and does not claim true zero-copy
5. Run POD top4 matrix:
   - baseline device-columnar binary route
   - new point-location device-face-column route
6. Write result packet and call-for-review.

## Verification

The result must report:

- byte-equal / semantic fingerprint parity with the previous binary route
- `point_location_device_face_columns_used`
- per-stage timing for:
  - native face-id column production
  - device-to-host face column copy
  - total vertex PIP phases
  - total midpoint PIP phases
- row-buffer metadata proving:
  - producer is directed point-location
  - fields are only `face_id`
  - app-specific schema is not allowed
  - true-zero-copy claim is not authorized

## Exit Labels

- `completed_point_location_device_face_columns_moves_downstream_floor`
- `completed_point_location_device_face_columns_no_perf_win_but_generic_handoff_proven`
- `blocked_by_existing_runtime_capability_gap`
- `fail_redo_due_to_app_specific_core_or_hidden_copy_claim`

## Expected Honest Outcome

The likely useful result is not a dramatic speedup. The current downstream still needs NumPy arrays for grouping, so this route may mainly replace full row materialization with a narrower `face_id` column copy. If it does not move the top4 hot path materially, that is still useful: it means the persistent floor is not point-location row materialization alone, and the next bottleneck remains true device-resident downstream grouping/consumer work.
