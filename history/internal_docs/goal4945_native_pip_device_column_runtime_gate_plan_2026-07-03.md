# Goal4945 - Native Runtime Gate For Goal4944 PIP Device Columns

## Purpose

Verify that Goal4944's native C++ ABI and Python carrier work against a rebuilt Linux `librtdl_optix.so` on NVIDIA hardware.

Goal4944 passed local static/Python tests and Antigravity review, but it changed native C++ code. Therefore it is not fully hardware-closed until this goal passes.

## Scope

This goal is only a native compile/runtime gate.

It does not start Layer 2 numeric continuation work, does not optimize RayJoin, and does not make performance claims.

## Required Environment

- A reachable Linux/POD or local Linux host with:
  - CUDA toolkit
  - OptiX SDK include path
  - repository checkout containing commit `69442cf77` or an equivalent patch
  - working Python import path for `src`
- Rebuilt `build/librtdl_optix.so`

## Work

1. Build `librtdl_optix.so` from current source.
2. Load the rebuilt backend from Python.
3. Run a tiny directed point-location fixture:
   - prepare two or more directed segments with face/segment ids
   - prepare query points
   - call `segment_id_device_columns(prepared_points)`
   - call `face_id_device_columns(prepared_points)`
   - adapt both through `device_column_row_buffer_from_point_location_id_columns(...)`
   - plan `numba` handoff through `plan_device_column_row_buffer_partner_handoff(...)`
4. Confirm metadata:
   - `ids_device_ptr > 0`
   - `row_count == prepared_points.point_count`
   - `dtype == "uint32"`
   - `device_resident == True`
   - `true_zero_copy_claim_authorized == False`
   - `public_speedup_claim_authorized == False`
5. Preserve compatibility:
   - existing `write_segment_ids_device_points(...)`
   - existing `write_face_ids_device_points(...)`
   - existing point-location tests

## Exit Gate

Pass if:

- Native library rebuilds.
- Python fixture observes nonzero device pointers for both segment and face id columns.
- Layer 1 row-buffer and v2.6 Numba handoff planning accept both columns.
- No app-specific schema appears in `src/rtdsl/device_column_row_buffer.py`.

Fail/redo if:

- Native build fails due to ABI/type mismatch.
- `face_id` still points to a temporary/dead buffer.
- row-buffer needs RayJoin/overlay/output-chain vocabulary to pass.
- tests require public speedup or true-zero-copy claims.

## Current Blocker

The POD command provided on 2026-07-03 was not usable with the available key:

```text
ssh -i ~/.ssh/id_ed25519 -o BatchMode=yes root@157.157.221.29 -p 24344
Permission denied (publickey,password).
```

Goal4945 should start as soon as a reachable Linux/POD environment is available.
