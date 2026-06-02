# Goal3002: RayJoin Numba Compact Mask Wiring

## Purpose

Goal3002 wires the v2.6 Numba `compact_mask_i64` continuation into the RayJoin-style benchmark app.

This is an app-level row-stream continuation surface. It is not the scalar fast path. Prepared generic RTDL count/parity primitives remain the recommended path when the user only needs counts.

## What Changed

- Added `RAYJOIN_V2_6_NUMBA_COMPACT_MASK_VERSION`.
- Added `describe_rayjoin_v2_6_numba_compact_mask_continuation(workload=...)`.
- Added `v2_6_numba_compact_mask_plan_payload(workload=...)`.
- Added `run_rayjoin_v2_6_numba_compact_mask_preview(inputs, workload=..., block_size=...)`.
- Added CLI route `--execution-route v2_6_numba_compact_mask_plan`.

## Contract

RayJoin app code owns the meaning of the candidate rows:

| Workload | App Interpretation |
| --- | --- |
| `pip` | Positive point/closed-shape rows. |
| `lsi` | Segment-pair intersection rows. |
| `overlay_seed` | Pair-dependency seed rows. |

RTDL/Numba sees only:

| Generic Operation | Inputs | Outputs |
| --- | --- | --- |
| `compact_mask_i64` | `candidate_row_ids:int64`, `keep_mask:bool` | `selected_candidate_row_ids:int64`, `original_indices:int64` |

RayJoin paper policy, positive-hit filtering, face metadata, and overlay interpretation remain Python benchmark-app logic.

## Boundary

- Not a RayJoin paper reproduction claim.
- Not a RayJoin performance claim.
- Not a Numba speedup claim.
- Not a whole-app speedup claim.
- Not an RT-core speedup claim.
- Not a true-zero-copy claim.
- Not v2.6 release authorization.

CUDA pod runtime evidence for this app wiring is still pending.
