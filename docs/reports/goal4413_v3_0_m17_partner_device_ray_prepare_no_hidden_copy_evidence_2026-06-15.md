# Goal4413 V3.0 M17 Partner-Device-Ray Prepare No-Hidden-Copy Evidence

Date: 2026-06-15

Status: complete for the partner-device-ray prepare and prepared hot-path no-hidden-copy gate.

## Purpose

M16 proved that the prepared hit-stream hot path could start from partner-owned CuPy device ray columns without per-run query-ray upload or hidden hot-window column copies. It still left one honest debt: `prepare_ray_batch_device_columns` downloaded ray IDs once into host memory for native bookkeeping.

M17 removes that prepare-time device-to-host ray-id bookkeeping from the hit-stream-safe device-column prepared-ray contract.

## Implementation

Native change:

- `PreparedRayBatch3D` now distinguishes host-ray-id batches from device-only batches.
- Host-packed ray batches still populate `ray_ids` and set `host_ray_ids_available=true`.
- Partner-device-column ray batches now pack GPU rays on device without downloading `ray_ids` to host.
- Grouped argmin paths that still need host ray IDs call `require_host_ray_ids(...)` and fail closed for device-only batches.

Python metadata change:

- `ray_id_host_bookkeeping_downloaded=false`
- `host_ray_ids_available=false`
- `grouped_host_ray_id_contract_available=false`

This keeps the V3 contract precise: the new device-only prepared ray batch is valid for hit-stream/closest-hit-style device execution paths, while grouped host-indexed paths need a future device-side grouped contract.

## Measurement

Source artifact:

- `docs/reports/goal4413_v3_0_m17_partner_device_ray_prepare_no_hidden_copy_evidence_8192_2026-06-15.json`

Pod hardware:

- NVIDIA RTX 4000 Ada Generation, driver 550.127.08, 20,475 MiB

Build:

- `make build-optix`
- Auto-detected CUDA arch: `sm_89`

Workload:

- Graph: `partner_device_ray_prepare_and_hit_stream_no_hidden_copy_pilot`
- Rays: 8,192
- Triangles: 2
- Stored hit rows: 16,384
- Partner ray producer: CuPy device arrays
- Partner consumer: CuPy RawKernel row reduction on the same stream
- Warmups: 2
- Repeats: 5
- Primitive deduplication: false

Measured windows:

- Prepare window: `prepare_ray_batch_device_columns(ray_columns)` after partner CuPy ray columns already exist on GPU.
- Hot window: native prepared-ray OptiX hit-stream producer through same-stream CuPy row reduction, before final scalar materialization.

## Results

| Path | Prepare median ms | Hot host median ms | Native enqueue ms | Consumer+summary ms | Prepare counter bytes | Hot counter bytes | DtoH | DtoD | Unknown | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| M16 partner-device rays | 2.801 | 3.018 | 1.960 | 1.007 | not gated | 88 | 0 | 0 | 0 | hot path pass |
| M17 partner-device rays | 0.296 | 2.989 | 1.920 | 1.014 | 0 | 88 | 0 | 0 | 0 | prepare + hot path pass |

Validation signature:

- `[16384, 16384, 16384, 67100672, 8192, 0, 0, 1]`

The signature stayed stable across all five repeats.

Prepare transfer-counter classification:

- Total calls: `0`
- Total bytes: `0`
- HtoD: `0`
- DtoH: `0`
- DtoD: `0`
- Unknown: `0`
- Min named ray column size: `32,768` bytes

Hot-path transfer-counter classification:

- Total calls: `1`
- Total bytes: `88`
- HtoD: `88`
- DtoH: `0`
- DtoD: `0`
- Unknown: `0`
- Min named output column size: `131,072` bytes

## Interpretation

M17 closes the M16 prepare-time ray-id copy debt for the hit-stream-safe path.

The important claims now supported internally are:

- Partner-owned CuPy device ray columns can be handed to RTDL.
- RTDL can prepare a device-resident ray batch from those columns without a measured CUDA copy.
- The prepared OptiX hit-stream hot path still has no per-run query-ray upload.
- Same-stream CuPy reduction consumes the device hit-stream output before host scalar materialization.

This is a stronger contract than M16. M16 said "after preparation, the hot path is clean." M17 says "for this device-only hit-stream contract, the preparation from partner device columns is also clean."

## Runtime Smoke

An additional pod smoke checked the guard boundary after rebuilding `librtdl_optix.so`:

- Host-packed prepared rays still ran `ray_closest_hit_prepared_grouped_argmin` successfully.
- Partner-device-column prepared rays failed closed for `ray_closest_hit_prepared_grouped_argmin` with: `prepared closest-hit grouped argmin requires host ray-id bookkeeping; device-column prepared ray batches use the hit-stream-safe device-only contract`.

That is the intended behavior for M17. The optimized device-only batch is promoted for hit-stream-safe execution, not for host-indexed grouped argmin yet.

## Boundary

Allowed internal wording:

RTDL now has a partner-device-ray hit-stream contract where CuPy-owned device ray columns are prepared into a device-resident RTDL ray batch with zero measured CUDA transfer calls in the prepare window, and the subsequent prepared OptiX producer through same-stream CuPy row-reduction hot path passes the M12 no-hidden-copy gate.

Short form: no prepare-time ray-id DtoH and no per-run query-ray upload for the partner-device-ray prepared hit-stream path.

Disallowed public wording:

- Do not claim grouped argmin paths support device-only ray batches yet.
- Do not claim final scalar materialization is inside the no-hidden-copy window.
- Do not claim automatic partner selection from this evidence alone.
- Do not claim application-level speedup from this micro-evidence alone.

## Engineering Consequence

M17 makes the V3 data-movement story materially cleaner. A Python partner can create ray columns on GPU, RTDL can prepare the ray batch without ray-id host bookkeeping, and the RT producer/partner-consumer hot path stays on device until the intentionally bounded final scalar summary.

The remaining design work is no longer about this hit-stream data path. It is about extending the same device-only discipline to grouped reductions that currently rely on host ray-id maps.
