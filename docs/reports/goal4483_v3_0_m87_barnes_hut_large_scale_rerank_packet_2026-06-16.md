# Goal4483 / V3.0 M87: Barnes-Hut Large-Scale Rerank

## Verdict

Barnes-Hut current guidance is now scale-dependent.

Goal4458 showed fused CPU/Numba was fastest on the 8,192 / 16,384 / 32,768-body force-summary ladder. M87 extends the same front-door rerank to 65,536 and 131,072 bodies. At these larger rows, `fused_frontier_force_sum_bucketized_numba_cuda` becomes the fastest measured route.

This is a real no-C++ GPU partner result, not an RT-core speedup result. The prepared RTDL/OptiX aggregate-frontier route still uses RT cores and still remains useful device-column evidence, but it loses because the row-emission frontier contract is the wrong hot-path shape for peak Barnes-Hut performance.

## Matrix

Runner: `scripts/v3_0_m62_barnes_hut_current_route_rerank.py`.

The raw runner version remains `rtdl.v3_0.barnes_hut_current_route_rerank.goal4458.v1`; M87 is a scale-extension evidence packet using that runner.

All rows use theta `0.5`, bucket size `64`, max depth `32`, force-summary output, 11 repeats, and 2 warmups on the RTX 4000 Ada pod.

| Bodies | Contribution rows | CPU/Numba fused | Numba CUDA fused | OptiX+Numba prepared frontier | OptiX+CuPy prepared frontier | Fastest |
|---:|---:|---:|---:|---:|---:|---|
| 65,536 | 55,935,606 | 100.097 ms | 33.964 ms | 179.026 ms | 319.275 ms | Numba CUDA fused |
| 131,072 | 68,023,506 | 103.804 ms | 44.909 ms | 618.309 ms | 782.600 ms | Numba CUDA fused |

Diagnostic ratios:

| Bodies | Numba CUDA vs CPU/Numba | Numba CUDA vs OptiX+Numba | OptiX+Numba vs CPU/Numba |
|---:|---:|---:|---:|
| 65,536 | 2.946x faster | 5.271x faster | 1.789x slower |
| 131,072 | 2.312x faster | 13.768x faster | 5.957x slower |

## Why

The fused Numba CUDA route keeps tree traversal and force accumulation in one Python-source CUDA partner kernel. It avoids frontier rows and contribution rows entirely.

The prepared RTDL/OptiX route does not materialize frontier rows on the host, which is good, but it still emits the generic aggregate-frontier device-column stream before partner vector accumulation. At 131,072 bodies, the OptiX frontier traversal median is about 594 ms before the partner sum, so the contract shape itself is the bottleneck.

The V3 implication is sharper now: a competitive RT-core Barnes-Hut route needs a fused, app-agnostic RT-native/device aggregate-vector primitive. More tuning of the current aggregate-frontier row-emission contract is unlikely to catch the fused partner route.

## Current Guidance

- Small tested rows from Goal4458: fused CPU/Numba remains fastest at 8,192 / 16,384 / 32,768 bodies.
- Larger tested rows from Goal4483: fused Numba CUDA is fastest at 65,536 / 131,072 bodies.
- Prepared RTDL/OptiX+Numba remains the RT-core aggregate-frontier device-column evidence route.
- Prepared RTDL/OptiX+CuPy remains a same-contract comparison partner, not a promoted route.

## Claim Boundary

- no Barnes-Hut RT-core speedup claim;
- no whole N-body speedup claim;
- no public backend speedup wording;
- no automatic route or partner selection;
- no app-specific native engine callback.

## Artifacts

- `goal4483_v3_0_m87_barnes_hut_large_scale_rerank_2026-06-16.json`
- `goal4483_v3_0_m87_barnes_hut_large_scale_rerank_packet_2026-06-16.json`
