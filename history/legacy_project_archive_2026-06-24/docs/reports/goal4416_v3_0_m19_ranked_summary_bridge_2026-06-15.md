# Goal4416 / V3.0 M19 RTNN ranked-summary bridge

Status: `accept-with-boundary`

This milestone closes the RTNN-specific lesson from the midterm review without pretending it is a public speedup result. The benchmark app is RTNN ranked-summary, but the new V3 graph id is app-agnostic: `prepared_ranked_summary_graph_partner_bridge`.

## What Changed

M19 extends the current prepared OptiX fixed-radius ranked-summary graph path with a split device-result contract:

| Piece | Result |
|---|---|
| Native RT producer | Existing OptiX prepared graph emits `RtdlFixedRadiusRankedNeighborAggregate` partial rows on device. |
| Device handoff | Runtime now exposes device-only CuPy and Numba same-stream reducers before aggregate materialization. |
| Finalization | Aggregate materialization is a separate `.materialize()` step after the hot measured window. |
| Partner rows | Both CuPy and Numba are measured for the same prepared graph and the same 65,536-point self-query workload. |
| Toolchain fix | Numba PTX mismatch is solved by running Numba against CUDA 12.4 NVVM/ptxas for the driver-550 pod, so Numba emits PTX 8.4 instead of unsupported PTX 8.7. |

## Pod Evidence

Artifact: `docs/reports/goal4416_v3_0_m19_ranked_summary_bridge_uniform_65536_2026-06-15.json`

Hardware: RTX 4000 Ada pod, driver 550 path. Workload: 65,536 3D points, self-query, uniform distribution, 3 ranked-summary requests: radius 0.015/0.020/0.025, `k_max=50`, 2 warmups, 5 repeats.

| Partner | Hot device median | Materialize median | Hot transfer counter | Signature |
|---|---:|---:|---|---|
| CuPy | 0.000601s | 0.0000462s | 0 bytes copied, no D2H/D2D/unknown | matched |
| Numba | 0.000622s | 0.0000848s | 0 bytes copied, no D2H/D2D/unknown | matched |

Cold preparation is intentionally separate: 2.587s, 4.45MB H2D, 6 H2D calls. That is expected initial data residency and graph build, not hidden-copy hot-path evidence.

## Interpretation

This is the right V3 bridge for RTNN: after prepared scene/query/graph residency, RTDL can keep native RT output on device, run a bounded same-stream partner reduction, and defer host materialization until after the measured hot device window.

It is not a public speedup claim, not a whole-app RTNN claim, and not paper parity. It specifically proves the missing architectural point: the current RTNN route can be made partner-continuation clean without extra hot-window data movement.

## Toolchain Note

The original Numba failure was real: Numba 0.65/llvmlite 0.47 with CUDA 12.8 NVVM emits PTX 8.7, while the driver-550 pod accepts PTX 8.4. The pod solution was to provide a CUDA 12.4 compiler home and run:

```bash
python scripts/v3_0_m19_ranked_summary_bridge_measure.py \
  --point-count 65536 \
  --distribution uniform \
  --warmups 2 \
  --repeats 5 \
  --numba-cuda-home /tmp/rtdl_cuda124_home \
  --output docs/reports/goal4416_v3_0_m19_ranked_summary_bridge_uniform_65536_2026-06-15.json
```

The runner records `runner_numba_cuda_home` in the artifact. This is a reproducible environment fix, not a benchmark excuse.

## Claim Boundary

Allowed internal wording: M19 proves an app-agnostic prepared ranked-summary graph partials contract with CuPy and Numba same-stream device reductions and no hidden hot-window copies.

Forbidden wording: public RT-core speedup, whole-app speedup, author-code parity, automatic partner selection, or end-to-end zero-copy.
