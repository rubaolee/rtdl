# Goal4456 / V3.0 M60: triangle bounded-id remap fast path

## Result

Goal4456 extends the triangle-counting Numba direct-binary summary builder beyond dense labels. For nonnegative graph ids whose observed id range is reasonably bounded by the input size, the builder now uses `np.bincount` plus a remap array instead of `np.unique(..., return_inverse=True)`.

This is still a generic graph-summary optimization. It is not a K4 special case and it preserves the fallback for sparse id spaces with very large gaps.

## Pod Measurement

Measured on the NVIDIA/CUDA pod with a 200,000 K4-clique topology but stride-2 vertex ids, so the graph is gapped but bounded: `0,2,4,...`. The expected triangle count is 800,000. Each full-app row used `partner=numba`, `backend=optix`, `warmup=1`, `repeat=3`, and reports the median of three full app runs after a small prewarm.

Compaction subphase on the same gapped input:

| Path | Median Time |
| --- | ---: |
| Old `np.unique(..., return_inverse=True)` compaction | 117.338 ms |
| New bounded-id remap compaction | 24.913 ms |
| Subphase speedup | 4.71x |

Full app rows:

| Mode | Build Contract | Build Geometry | Prepare Scene | Query Median | Total | Fast Path Flags |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `rt_graph_2a1_generic_rt` | 188.323 ms | 5.860 ms | 7.345 ms | 1.949 ms | 212.372 ms | bounded-id yes; dense no; sorted directed yes; sorted two-hop yes |
| `rt_graph_1a2_generic_rt` | 188.556 ms | 14.164 ms | 5.625 ms | 3.289 ms | 223.666 ms | bounded-id yes; dense no; sorted directed yes; sorted two-hop yes |

Both rows matched the oracle triangle count.

## Boundary

This reduces avoidable host summary-construction work for bounded gapped id spaces. It does not authorize a triangle-counting RT-core speedup claim, whole-app speedup wording, or automatic partner selection. CuPy remains the measured performance partner after Goal4455; Numba remains the no-C++ Python-source reference route.

## Evidence

- Implementation: `examples/current/research_benchmarks/triangle_counting/rt_graph_contract.py`
- Test: `tests/goal4456_v3_0_m60_triangle_bounded_id_remap_fast_path_test.py`
- Measurement artifact: `docs/reports/goal4456_v3_0_m60_triangle_bounded_id_remap_fast_path_200000_2026-06-16.json`
