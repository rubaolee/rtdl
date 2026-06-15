# Goal4411 V3.0 M15 Prepared Hit-Stream No-Hidden-Copy Evidence

Date: 2026-06-15

Status: complete for the prepared-ray full-window no-hidden-copy gate.

## Purpose

M14 expanded the transfer-counter window to include native producer enqueue. That correctly exposed the current host-packed ray path: each run uploaded 262,144 bytes of query rays plus 88 bytes of launch parameters before the OptiX hit-stream launch.

M15 fixes that optimization debt for the hit-stream row-reduction pilot. It uses a prepared device-resident 3-D ray batch, then measures the full prepared-ray producer enqueue through same-stream CuPy row-reduction window before final scalar summary materialization.

## Measurement

Source artifact:

- `docs/reports/goal4411_v3_0_m15_prepared_hit_stream_no_hidden_copy_evidence_8192_2026-06-15.json`

Pod hardware:

- NVIDIA RTX 4000 Ada Generation, driver 550.127.08, 20,475 MiB

Workload:

- Graph: `prepared_ray_batch_hit_stream_full_window_no_hidden_copy_pilot`
- Rays: 8,192
- Triangles: 2
- Stored hit rows: 16,384
- Partner: CuPy RawKernel row reduction
- Warmups: 2
- Repeats: 5
- Primitive deduplication: false, so the reduction covers all stored hit rows

Measured window:

- Starts before native prepared-ray producer enqueue.
- Covers status reset, OptiX launch over a prepared device-resident ray batch, and CuPy same-stream row reduction.
- Ends before final summary materialization with `cp.asnumpy`.
- Does not include one-time ray batch preparation.

## Results

| Path | Host median ms | Native enqueue ms | Consumer+summary ms | Counter calls/bytes | HtoD bytes | DtoH | DtoD | Unknown | Query rays uploaded each run | M12 full-window verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| M14 host-packed rays | 13.661 | 2.233 | 1.090 | 2 / 262,232 | 262,232 | 0 | 0 | 0 | yes | audit only |
| M15 prepared rays | 2.975 | 1.921 | 0.993 | 1 / 88 | 88 | 0 | 0 | 0 | no | pass |

Validation signature:

- `[16384, 16384, 16384, 67100672, 8192, 0, 0, 1]`

The signature stayed stable across all five repeats.

## Interpretation

M15 removes the per-run query-ray upload from the measured producer+partner window:

- M14 observed HtoD: `262,232` bytes.
- M15 observed HtoD: `88` bytes.
- Reduction: `262,144` bytes, exactly `8,192 * 32` ray bytes.
- Remaining HtoD: 88 bytes, the small launch-parameter upload allowed by the M12 no-hidden-copy contract.
- Observed DtoH: `0`.
- Observed DtoD: `0`.
- Observed unknown-direction copies: `0`.

The M12 classifier therefore passes on the full prepared-ray producer+partner window:

- `same_stream_ready`: true
- `transfer_counter_observed`: true
- `prepared_ray_batch_used`: true
- `query_rays_uploaded_each_run`: false
- `no_hidden_column_copy_ready`: true
- `true_zero_copy_ready`: true
- `public_claim_authorized`: false

## Boundary

Allowed internal wording:

RTDL now has a prepared-ray hit-stream path where the full native producer enqueue through same-stream CuPy row-reduction window passes the M12 no-hidden-copy gate. Query rays are prepared once and are not uploaded in each measured run.

Short form: no per-run query-ray upload in the measured prepared-ray hot path.

Disallowed public wording:

- Do not claim arbitrary non-prepared hit-stream calls avoid query upload.
- Do not include final scalar summary materialization in the no-hidden-copy window.
- Do not claim public application speedup from this micro-evidence alone.
- Do not generalize from the bounded CuPy row-reduction consumer to arbitrary partner callbacks.

## Engineering Consequence

M15 is the concrete solution implied by M14: prepared/device-resident query batches are the right implementation strategy for hot repeated RT workloads. For V3, this is the pattern to generalize: separate one-time preparation from hot-path producer enqueue, keep outputs and status device-resident, and let same-stream partners consume bounded device rows before any host materialization.
