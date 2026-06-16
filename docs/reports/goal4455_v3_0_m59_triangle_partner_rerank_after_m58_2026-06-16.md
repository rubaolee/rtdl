# Goal4455 / V3.0 M59: triangle partner rerank after M58

## Result

Goal4455 re-ranks the triangle-counting RT-Graph summary-contract partners after the Goal4454 Numba summary fast paths. The conclusion is unchanged but now current: CuPy remains the large-scale performance route, while Numba is the no-C++ Python-source reference route.

The important nuance is that M58 materially improved Numba, but not enough to overtake CuPy. On the 200,000 K4-clique dense/sorted fixture, CuPy is still about 2.85x faster in total wall time for both RT-2A1 and RT-1A2.

## Pod Measurement

Measured on the NVIDIA/CUDA pod with 200,000 K4 cliques, 1,200,000 input edges, and an expected 800,000 triangle count. Each row used `backend=optix`, `warmup=1`, `repeat=3`, and reports the median of three full app runs per mode/partner after a small prewarm.

| Mode | Partner | Build Contract | Build Geometry | Prepare Scene | Query Median | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `rt_graph_2a1_generic_rt` | CuPy | 51.832 ms | 0.493 ms | 7.535 ms | 1.966 ms | 70.486 ms |
| `rt_graph_2a1_generic_rt` | Numba | 176.820 ms | 5.797 ms | 7.359 ms | 1.952 ms | 200.690 ms |
| `rt_graph_1a2_generic_rt` | CuPy | 50.473 ms | 2.723 ms | 5.821 ms | 3.286 ms | 74.211 ms |
| `rt_graph_1a2_generic_rt` | Numba | 176.755 ms | 14.370 ms | 5.638 ms | 3.283 ms | 211.922 ms |

CuPy total-time advantage over optimized Numba:

| Mode | CuPy Faster By | Main Reason |
| --- | ---: | --- |
| `rt_graph_2a1_generic_rt` | 2.85x | CuPy builds the summary/device columns in about 52 ms versus Numba's about 177 ms. |
| `rt_graph_1a2_generic_rt` | 2.86x | Same; RT query times are near-identical, so partner construction dominates. |

## Boundary

This rerank does not authorize automatic partner selection. It supports guidance only: choose CuPy for current maximum performance when CuPy is available; choose Numba when no-C++ Python-source partner code matters. It does not authorize triangle-counting RT-core speedup wording, because the scalar benchmark remains primitive-first and the explicit partner route is still dominated by graph-summary construction.

## Evidence

- Measurement artifact: `docs/reports/goal4455_v3_0_m59_triangle_partner_rerank_after_m58_200000_2026-06-16.json`
- Related implementation evidence: Goal4453 device geometry and Goal4454 summary fast paths.
