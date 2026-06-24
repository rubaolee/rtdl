# Goal4412 V3.0 M16 Partner-Device-Ray Hit-Stream No-Hidden-Copy Evidence

Date: 2026-06-15

Status: complete for the partner-device-ray prepared hot-path no-hidden-copy gate.

## Purpose

M15 proved the prepared-ray hit-stream hot path after rays were prepared from host-packed input. M16 moves one step closer to the user-facing V3 contract: a partner creates ray columns directly on the GPU, RTDL prepares a device-resident ray batch from those partner-owned device columns, then the same prepared-ray OptiX producer and same-stream CuPy row-reduction consumer run without hidden column copies.

This is the important user question M16 answers:

Can a Python partner hand GPU ray columns to RTDL without RTDL secretly moving the hot-path workload back through the CPU?

For the measured hot path, yes.

## Measurement

Source artifact:

- `docs/reports/goal4412_v3_0_m16_partner_device_ray_hit_stream_no_hidden_copy_evidence_8192_2026-06-15.json`

Pod hardware:

- NVIDIA RTX 4000 Ada Generation, driver 550.127.08, 20,475 MiB

Build note:

- The pod has a CUDA 12.8 toolkit with a 550-series driver exposing CUDA 12.4.
- `build-optix` now auto-detects the local GPU compute capability and passes `-arch=sm_89` on this pod.
- This avoids leaving the CUDA helper kernel to fall back to PTX that the installed driver cannot load.

Workload:

- Graph: `partner_device_ray_prepared_hit_stream_full_window_no_hidden_copy_pilot`
- Rays: 8,192
- Triangles: 2
- Stored hit rows: 16,384
- Partner ray producer: CuPy device arrays
- Partner consumer: CuPy RawKernel row reduction on the same stream
- Warmups: 2
- Repeats: 5
- Primitive deduplication: false, so the reduction covers all stored hit rows

Measured window:

- Starts before native prepared-ray producer enqueue.
- Covers status reset, OptiX launch over a prepared device-resident ray batch, and CuPy same-stream row reduction.
- Ends before final scalar summary materialization with `cp.asnumpy`.
- Does not include one-time ray-batch preparation.

## Results

| Path | Ray source | Host median ms | Native enqueue ms | Consumer+summary ms | Counter calls/bytes | HtoD bytes | DtoH | DtoD | Unknown | Query rays uploaded each run | M12 hot-window verdict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| M15 prepared rays | host-packed rays prepared once | 2.975 | 1.921 | 0.993 | 1 / 88 | 88 | 0 | 0 | 0 | no | pass |
| M16 partner-device rays | partner-owned CuPy device ray columns prepared once | 3.018 | 1.960 | 1.007 | 1 / 88 | 88 | 0 | 0 | 0 | no | pass |

Validation signature:

- `[16384, 16384, 16384, 67100672, 8192, 0, 0, 1]`

The signature stayed stable across all five repeats.

One-time prepare timing:

- M16 reported `2.801 ms` to create the prepared ray batch from partner-owned CuPy device columns.
- That prepare phase is outside the hot-path transfer-counter window.

## Interpretation

M16 preserves the M15 hot-path result while changing the source contract from host-packed rays to partner-owned GPU columns:

- `ray_columns_partner_owned`: true
- `source_protocols`: `cupy`
- `ray_batch_created_from`: `partner_device_columns`
- `prepared_ray_batch_used`: true
- `query_rays_uploaded_each_run`: false
- `prepared_rays_resident_on_device`: true
- Observed HtoD in measured hot window: `88` bytes
- Observed DtoH in measured hot window: `0`
- Observed DtoD in measured hot window: `0`
- Observed unknown-direction copies in measured hot window: `0`

The M12 classifier passes because the only observed hot-window transfer is the allowed small native launch-parameter upload. No named input, output, or handoff column is copied through host memory in the measured producer+consumer window.

## Boundary

Allowed internal wording:

RTDL now has a partner-device-ray prepared hit-stream path where CuPy-owned device ray columns are prepared once into a device-resident RTDL ray batch, and the repeated native OptiX producer through same-stream CuPy reduction hot path passes the M12 no-hidden-copy gate.

Short form: partner-generated GPU ray columns can feed the prepared RTDL OptiX hit-stream hot path without per-run query-ray upload or hidden hot-window column copy.

Disallowed public wording:

- Do not claim the one-time `prepare_ray_batch_device_columns` phase is fully no-copy.
- Do not include final scalar summary materialization in the no-hidden-copy window.
- Do not claim automatic partner selection from this evidence alone.
- Do not generalize from this bounded CuPy producer/consumer pair to every possible partner callback.
- Do not claim application-level speedup from this micro-evidence alone.

## Remaining Debt

The native `PreparedRayBatch3D` constructor for device ray columns still downloads ray IDs once into a host vector for bookkeeping used by some prepared grouped-query paths. The M16 hot path does not use that host vector, but the one-time prepare phase is therefore not yet a full end-to-end zero-copy prepare.

The next clean target is to split prepared ray batches into two contracts:

- hit-stream/closest-hit hot paths that do not require host ray IDs and can prepare from device columns without the one-time ray-id DtoH bookkeeping;
- grouped host-indexed paths that explicitly require host-side ray IDs or a device-side grouped-input contract.

## Engineering Consequence

M16 is the practical bridge from "RTDL can run fast after preparation" to "a Python partner can generate GPU-resident ray inputs and hand them to RTDL." It keeps V3's design intact: RTDL owns the app-agnostic primitive and prepared OptiX execution path, while the partner owns GPU-side data generation and same-stream summary logic.

The result is not a miracle claim. It is a concrete systems contract: no unnecessary hot-path data re-movement once partner data is on the GPU and the RTDL prepared ray batch exists.
