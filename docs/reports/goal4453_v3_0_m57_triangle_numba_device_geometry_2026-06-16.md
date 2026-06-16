# Goal4453 / V3.0 M57: triangle Numba device-geometry cleanup

## Result

Goal4453 removes the remaining obvious host/device churn in the triangle-counting RT-Graph Numba summary-contract path. RT-1A2 and RT-2A1 Numba geometry fill now starts from partner-resident device columns produced by the direct-binary summary builder instead of rebuilding full geometry columns on the Python host and uploading them again.

This is an implementation cleanup and partner-route optimization. It does not authorize a triangle-counting RT-core speedup claim, and it does not change the scalar-answer guidance: use the generic RT graph relationship-count composition for the benchmark's scalar result.

## What Changed

- RT-1A2 Numba geometry fill now uses `row_offsets`, `column_indices`, and `directed_src` from the summary contract's Numba device arrays.
- RT-2A1 Numba geometry fill now uses `directed_src`, `column_indices`, `two_hop_src`, `two_hop_dst`, and `two_hop_weights` from the same partner-resident device columns.
- RT-2A1 ray weights reuse `device_arrays["two_hop_weights"]` directly instead of creating a host `ray_weights_host` array and uploading it again.
- Small host scheduling metadata remains for allocation sizing and prefix offsets in RT-1A2; the large geometry columns are filled on device.

## Boundary

The remaining debt is graph-summary construction: the direct-binary Numba summary path still constructs CSR/two-hop summary columns before the geometry fill stage. A true next step is a streamed/segmented graph-summary construction path that avoids global two-hop materialization on paper-scale inputs.

Public wording should say that RTDL removed unnecessary data movement in the explicit no-C++ Numba partner route. It should not say that triangle counting is now a demonstrated RT-core acceleration case.

## Pod Measurement

Measured on the NVIDIA/CUDA pod with 200,000 K4 cliques, 1,200,000 undirected input edges, and an expected 800,000 triangle count. Each row used `partner=numba`, `backend=optix`, `warmup=1`, `repeat=3`, and the table reports the median of three full app runs per mode after a small prewarm.

| Mode | Build contract | Build geometry | Prepare scene | Query median | Total | Interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `rt_graph_2a1_generic_rt` | 311.847 ms | 5.936 ms | 7.348 ms | 1.952 ms | 335.981 ms | Device geometry fill is no longer the dominant cost; graph-summary construction dominates. |
| `rt_graph_1a2_generic_rt` | 304.422 ms | 14.063 ms | 5.643 ms | 3.283 ms | 339.267 ms | Same conclusion; the RT query itself is only a few milliseconds. |

Both rows matched the oracle triangle count. The evidence supports the M57 cleanup claim, not a public RT-core triangle-counting speedup claim.

## Evidence

- Implementation: `examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py`
- Test: `tests/goal4453_v3_0_m57_triangle_numba_device_geometry_test.py`
- Measurement artifact: `docs/reports/goal4453_v3_0_m57_triangle_numba_device_geometry_200000_2026-06-16.json`
