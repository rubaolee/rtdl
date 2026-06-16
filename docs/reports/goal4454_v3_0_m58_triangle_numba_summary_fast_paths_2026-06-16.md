# Goal4454 / V3.0 M58: triangle Numba summary fast paths

## Result

Goal4454 reduces the remaining triangle-counting Numba partner summary-construction cost without changing the RTDL/OptiX primitive contract. The NumPy direct-binary summary builder now uses three generic fast paths when the input permits them:

- Dense nonnegative contiguous vertex labels skip `np.unique(..., return_inverse=True)` remapping.
- Already sorted directed edge keys skip full `np.unique` sorting for directed CSR construction.
- Already sorted two-hop keys use run-length aggregation instead of full `np.unique(..., return_counts=True)`.

This keeps the no-C++ Numba partner route app-agnostic: the fast paths are data-shape checks inside the generic graph-summary builder, not K4-specific or triangle-paper-specific logic.

## Pod Measurement

Measured on the NVIDIA/CUDA pod with 200,000 K4 cliques, 1,200,000 input edges, and an expected 800,000 triangle count. Each row used `partner=numba`, `backend=optix`, `warmup=1`, `repeat=3`, and the table reports the median of three full app runs per mode after a small prewarm.

| Mode | M57 Total | M58 Total | Total Speedup | M57 Build Contract | M58 Build Contract | Build Speedup | M57 Direct Summary | M58 Direct Summary | Summary Speedup |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `rt_graph_2a1_generic_rt` | 335.981 ms | 204.218 ms | 1.65x | 311.847 ms | 179.649 ms | 1.74x | 280.652 ms | 155.681 ms | 1.80x |
| `rt_graph_1a2_generic_rt` | 339.267 ms | 211.792 ms | 1.60x | 304.422 ms | 176.824 ms | 1.72x | 279.916 ms | 152.815 ms | 1.83x |

All measured rows matched the oracle triangle count. The dense-label, directed-sorted, and two-hop sorted-RLE fast paths were active on the dense K4 fixture.

## Boundary

This improves the explicit Numba summary-contract route and removes avoidable NumPy sorting/compaction work for common dense/sorted graph inputs. It does not authorize a triangle-counting RT-core speedup claim, whole-app speedup wording, or automatic partner selection. Direct-binary summary construction still dominates total time, so the next deeper step would be a device or segmented summary builder rather than more geometry/query tuning.

## Evidence

- Implementation: `examples/current/research_benchmarks/triangle_counting/rt_graph_contract.py`
- Test: `tests/goal4454_v3_0_m58_triangle_numba_summary_fast_paths_test.py`
- Measurement artifact: `docs/reports/goal4454_v3_0_m58_triangle_numba_summary_fast_paths_200000_2026-06-16.json`
