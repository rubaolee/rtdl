# Goal4497 / V3 M101 Barnes-Hut RT-Native Fused Feasibility

## Conclusion

Barnes-Hut should stay mixed explicit for current V3 guidance. The fastest measured route is scale-dependent: fused CPU/Numba wins the Goal4458 smaller rows, and fused Numba CUDA wins the Goal4483 larger rows. The RTDL/OptiX route is real RT-core aggregate-frontier device-column evidence, but it is not a Barnes-Hut RT-core speedup route because its hot contract still emits aggregate-frontier rows before vector accumulation.

A competitive RT-core Barnes-Hut path requires a new app-agnostic native primitive, tentatively `generic_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_v1`, that fuses traversal, opening-rule acceptance, exact fallback, and weighted vector accumulation into device output columns. More tuning of the current frontier-row contract is not the right next optimization.

## Evidence Matrix

| Bodies | Source | Fastest route | CPU/Numba | Numba CUDA | OptiX+Numba | OptiX+CuPy | OptiX slower than best |
|---:|---|---|---:|---:|---:|---:|---:|
| 8,192 | Goal4458 | `cpu_numba_fused` | 1.396ms | 3.283ms | 15.277ms | 22.264ms | 10.94x |
| 16,384 | Goal4458 | `cpu_numba_fused` | 8.050ms | 8.418ms | 30.776ms | 61.790ms | 3.82x |
| 32,768 | Goal4458 | `cpu_numba_fused` | 7.268ms | 10.638ms | 82.250ms | 119.221ms | 11.32x |
| 65,536 | Goal4483 | `numba_cuda_fused` | 100.097ms | 33.964ms | 179.026ms | 319.275ms | 5.27x |
| 131,072 | Goal4483 | `numba_cuda_fused` | 103.804ms | 44.909ms | 618.309ms | 782.600ms | 13.77x |

## Required Primitive Boundary

- It must be generic aggregate-tree weighted-vector math, not Barnes-Hut app-specific native code.
- It must output per-source vector/count columns directly and avoid aggregate-frontier row emission.
- It must be compared against Goal4458 small-row fused CPU/Numba and Goal4483 large-row fused Numba CUDA under the same force-summary contract.
- Until this primitive exists, no Barnes-Hut RT-core speedup, whole-app acceleration, public speedup, automatic partner selection, or app-specific native-engine claim is authorized.

## Current Decision

Keep Barnes-Hut as mixed explicit current guidance. If RT-core acceleration for Barnes-Hut remains a V3 target, implement the proposed app-agnostic RT-native fused weighted-vector primitive and compare it against the current fused CPU/Numba and fused Numba CUDA force-summary routes. Do not spend more V3 effort optimizing the aggregate-frontier row-emission route as if it were the final RT-core Barnes-Hut shape.

Artifacts:

- `docs/reports/goal4497_v3_0_m101_barnes_hut_rt_native_fused_feasibility_2026-06-17.json`
- `docs/reports/goal4497_v3_0_m101_barnes_hut_rt_native_fused_feasibility_2026-06-17.jsonl`
