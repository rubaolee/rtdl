# Goal4409 V3.0 M13 Hit-Stream No-Hidden-Copy Evidence

Date: 2026-06-15

Status: complete for the second-workload M12 no-hidden-copy gate.

## Purpose

M11 proved no-hidden-copy readiness for the fixed-radius grouped-union pilot. M12 extracted that rule into an app-agnostic contract. M13 applies the M12 contract to a different workload: an OptiX ray-triangle hit-stream producer followed by a CuPy same-stream row-reduction consumer.

This matters because the no-hidden-copy gate is no longer tied only to fixed-radius/component-label output.

## Measurement

Source artifact:

- `docs/reports/goal4409_v3_0_m13_hit_stream_no_hidden_copy_evidence_8192_2026-06-15.json`

Pod hardware:

- NVIDIA RTX 4000 Ada Generation, driver 550.127.08, 20,475 MiB

Workload:

- Graph: `ray_triangle_hit_stream_row_reduction_no_hidden_copy_pilot`
- Rays: 8,192
- Triangles: 2
- Stored hit rows: 16,384
- Partner: CuPy RawKernel row reduction
- Warmups: 2
- Repeats: 5
- Primitive deduplication: false, so the reduction covers all stored hit rows

Measured window:

- Starts after the native OptiX producer has enqueued the hit-stream work.
- Covers the same-stream CuPy row-reduction consumer.
- Ends before final summary materialization with `cp.asnumpy`.

## Results

| Partner | Host median ms | Native enqueue ms | Consumer+summary ms | Hit rows | Counter calls/bytes | HtoD | DtoH | DtoD | Unknown | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| CuPy | 13.815 | 2.253 | 1.122 | 16,384 | 0 / 0 | 0 | 0 | 0 | 0 | pass |

Validation signature:

- `[16384, 16384, 16384, 67100672, 8192, 0, 0, 1]`

The signature stayed stable across all five repeats.

## Interpretation

The M12 classifier observed no CUDA transfer calls in the measured handoff window:

- no host-to-device transfer;
- no device-to-host transfer;
- no device-to-device transfer;
- no unknown-direction transfer.

The smallest named output column in this workload is 131,072 bytes. Observed transfer bytes were zero, so the measured same-stream producer-to-partner row-reduction window has no hidden named-column movement.

Readiness:

- `same_stream_ready`: true
- `transfer_counter_observed`: true
- `no_hidden_column_copy_ready`: true
- `true_zero_copy_ready`: true
- `public_claim_authorized`: false

## Important Boundary

This M13 artifact proves only the post-native-enqueue producer-to-partner handoff window. It does not claim end-to-end zero-copy for query input upload, final scalar summary materialization, or whole-application performance.

Allowed internal wording:

RTDL's M12 no-hidden-copy contract now passes on a second workload: OptiX hit-stream device rows consumed by a CuPy same-stream row-reduction partner before summary materialization.

Disallowed public wording:

- Do not claim all hit-stream APIs are zero-copy.
- Do not claim end-to-end application I/O is zero-copy.
- Do not claim public speedup from this artifact alone.
- Do not generalize from the bounded CuPy row-reduction consumer to arbitrary partner callbacks.

## Engineering Notes

The first measurement attempt exposed an honest workload issue: with primitive deduplication enabled, the retained ray-id winner per primitive is nondeterministic under parallel hits. M13 therefore fixes the evidence workload to `deduplicate_primitives=false`, matching the stated row-reduction contract: reduce all stored hit rows.

The runtime hook disables the transfer counter before `cp.asnumpy(summary)`, so the final scalar summary download is intentionally outside the no-hidden-copy window.
