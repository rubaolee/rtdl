# Goal4407 V3.0 M11 No-Hidden-Copy Evidence

Date: 2026-06-15

Status: complete for the M11 internal evidence gate.

## Purpose

M10 proved that RTDL can launch native OptiX work and continue into a Python partner on the same CUDA stream. M11 tightens that claim: during the measured window from native OptiX launch through Python partner continuation, RTDL must not secretly move named handoff/output columns through host memory or rematerialize them with extra CUDA copies.

This is an internal readiness claim. It does not authorize a public speedup claim by itself.

## Measurement

Source artifact:

- `docs/reports/goal4407_v3_0_m11_no_hidden_copy_evidence_65536_2026-06-15.json`

Pod hardware:

- NVIDIA RTX 4000 Ada Generation, driver 550.127.08, 20,475 MiB

Workload:

- Graph: `fixed_radius_component_no_hidden_copy_evidence_pilot`
- Points: 65,536
- Radius: 1.01
- Component threshold: 7
- Warmups: 2
- Repeats: 5
- Partners: CuPy and Numba

Instrumentation:

- Native CUDA event pair for OptiX launch to partner continuation timing.
- Same CUDA stream pointer checked across native metadata and partner continuation.
- `LD_PRELOAD` CUDA transfer counter around only the measured continuation window.
- Validation/materialization happens after the measured window.

## Results

| Partner | Prepare s | Host median ms | CUDA event total ms | Native ms | Partner ms | Counter calls/bytes | HtoD bytes | DtoH/DtoD/unknown calls | Min named column bytes | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| CuPy | 1.457 | 0.906 | 0.761 | 0.756 | 0.005 | 1 / 96 | 96 | 0 / 0 / 0 | 262,144 | pass |
| Numba | 0.171 | 1.222 | 0.767 | 0.761 | 0.006 | 1 / 96 | 96 | 0 / 0 / 0 | 262,144 | pass |

Every measured repeat had the same transfer-counter shape: one 96-byte host-to-device transfer, zero device-to-host transfers, zero device-to-device transfers, and zero unknown transfers.

## Interpretation

The observed 96-byte HtoD transfer is launch-parameter sized. The M11 classifier allows up to 4,096 bytes of non-column HtoD setup. The smallest named column in this workload is 262,144 bytes, so the observed transfer is far below a plausible hidden column materialization. No DtoH, DtoD, or unknown copies were observed in the measured continuation window.

Therefore, for this M11 fixed-radius grouped-union pilot:

- `same_stream_ready`: true
- `transfer_counter_observed`: true
- `no_hidden_column_copy_ready`: true
- `true_zero_copy_ready`: true
- `public_claim_authorized`: false

## Claim Boundary

Allowed internal wording:

RTDL now has measured internal evidence that its native OptiX to Python partner same-stream handoff can avoid hidden named-column host/device movement in the measured continuation window, for both CuPy and Numba partners.

Disallowed public wording:

- Do not claim all RTDL apps are zero-copy.
- Do not claim end-to-end application I/O is zero-copy.
- Do not use this artifact as a standalone public speedup claim.
- Do not generalize from this pilot to arbitrary partner logic without per-app evidence.

## Engineering Notes

Two measurement-tool issues were fixed before accepting this artifact:

- The runner no longer rebuilds the preloaded transfer-counter shared object after re-exec.
- The CUDA transfer-counter shim now uses explicit `libcuda.so.1` / `libcudart.so.12` fallback symbol lookup when `RTLD_NEXT` cannot see locally loaded CUDA libraries.

The final artifact was generated after both fixes.
