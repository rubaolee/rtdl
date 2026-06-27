# Goal4410 V3.0 M14 Hit-Stream Full-Window Transfer Audit

Date: 2026-06-15

Status: complete for the current host-packed ray hit-stream full-window transfer audit.

## Purpose

M13 proved that the post-native-enqueue handoff from OptiX hit-stream output columns to a CuPy same-stream row-reduction partner has no hidden CUDA transfer before final scalar summary materialization.

M14 intentionally expands the measured window. The counter starts before the native producer enqueue and stops after the same-stream CuPy reduction, before `cp.asnumpy(summary)`. This answers a different question: when the native producer itself is included, are the observed transfers explainable, or is RTDL hiding output-column movement?

## Measurement

Source artifact:

- `docs/reports/goal4410_v3_0_m14_hit_stream_full_window_transfer_audit_8192_2026-06-15.json`

Pod hardware:

- NVIDIA RTX 4000 Ada Generation, driver 550.127.08, 20,475 MiB

Workload:

- Graph: `ray_triangle_hit_stream_full_window_transfer_audit`
- Rays: 8,192
- Triangles: 2
- Stored hit rows: 16,384
- Partner: CuPy RawKernel row reduction
- Warmups: 2
- Repeats: 5
- Primitive deduplication: false, so the reduction covers all stored hit rows

Measured window:

- Starts before the native OptiX producer enqueue.
- Covers stream-ordered query-ray upload, launch-parameter upload, OptiX launch, and CuPy same-stream row reduction.
- Ends before final summary materialization with `cp.asnumpy`.

## Results

| Partner | Host median ms | Native enqueue ms | Consumer+summary ms | Hit rows | Counter calls/bytes | HtoD bytes | Explained HtoD | DtoH | DtoD | Unknown | Full true zero-copy | Handoff verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| CuPy | 13.661 | 2.233 | 1.090 | 16,384 | 2 / 262,232 | 262,232 | 262,144 ray bytes + 88 param bytes | 0 | 0 | 0 | no | pass |

Validation signature:

- `[16384, 16384, 16384, 67100672, 8192, 0, 0, 1]`

The signature stayed stable across all five repeats.

## Interpretation

The full producer+consumer window is not an end-to-end true-zero-copy claim. That is expected for the current host-packed ray API: the native producer uploads the query rays on the CUDA stream before the OptiX launch.

The observed transfer bytes match the implementation:

- Expected query-ray upload: `8,192 * 32 = 262,144` bytes.
- Observed HtoD: `262,232` bytes.
- Remaining HtoD: `88` bytes, explained by native launch parameters.
- Observed DtoH: `0`.
- Observed DtoD: `0`.
- Observed unknown-direction copies: `0`.

Therefore M14 supports this narrower but important statement:

RTDL's current host-packed hit-stream path still uploads query rays per run, but the RT output columns are not secretly copied back to host or copied device-to-device before the same-stream CuPy partner consumes them.

## Boundary

Allowed internal wording:

RTDL now has measured full-window transfer accounting for the OptiX hit-stream plus CuPy same-stream partner path. The only observed full-window transfers are expected query-ray HtoD upload and a small launch-parameter upload; no DtoH, DtoD, or unknown transfer is observed before summary materialization.

Disallowed public wording:

- Do not claim the current host-packed ray path is end-to-end true-zero-copy.
- Do not claim all hit-stream APIs avoid query input upload.
- Do not claim public application speedup from this artifact alone.
- Do not claim arbitrary partner callbacks inherit this behavior.

## Engineering Consequence

M14 turns the next optimization target into a concrete item: prepared/device-resident query-ray batches. If a future M15/M16 path accepts already device-resident rays, then the same full-window audit should be able to remove the `262,144` byte ray upload. That would move the evidence from "handoff no-hidden-output-copy" toward a true producer+partner zero-copy window for prepared query workloads.
