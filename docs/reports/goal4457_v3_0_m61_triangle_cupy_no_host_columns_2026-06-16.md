# Goal4457 / V3.0 M61: triangle CuPy no-host-column summary route

## Result

Goal4457 removes an avoidable host materialization step from the triangle-counting CuPy summary-contract app route. The reusable CuPy builder still materializes host columns by default for compatibility, but the app's `--partner cupy --backend optix --detail summary` route now requests `materialize_host_columns=False` and uses partner-resident device arrays plus lightweight host placeholders for summary metadata.

This keeps the same RTDL/OptiX primitive contract and the same app-level output contract. It removes unnecessary host downloads from the fastest current partner route.

## Pod Measurement

Measured on the NVIDIA/CUDA pod with 200,000 K4 cliques, 1,200,000 input edges, and an expected 800,000 triangle count. Each row used `partner=cupy`, `backend=optix`, `warmup=1`, `repeat=3`, and reports the median of three full app runs after a small prewarm.

| Mode | M59 Total | M61 Total | Total Speedup | M59 Build Contract | M61 Build Contract | Build Speedup |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `rt_graph_2a1_generic_rt` | 70.486 ms | 51.596 ms | 1.37x | 51.832 ms | 32.904 ms | 1.58x |
| `rt_graph_1a2_generic_rt` | 74.211 ms | 52.912 ms | 1.40x | 50.473 ms | 29.604 ms | 1.70x |

The old `download_needed_columns_ms` phase was replaced by `device_count_summary_ms`:

| Mode | Host Columns Materialized | Device Count Summary | Total Partner |
| --- | --- | ---: | ---: |
| `rt_graph_2a1_generic_rt` | no | 0.064 ms | 32.215 ms |
| `rt_graph_1a2_generic_rt` | no | 0.070 ms | 28.913 ms |

Both rows matched the oracle triangle count.

## Boundary

This is a host-materialization cleanup in the CuPy partner route, not a new RT primitive and not a triangle-counting RT-core speedup claim. CuPy remains the measured performance partner; Numba remains the no-C++ Python-source reference route.

## Evidence

- Implementation: `examples/current/research_benchmarks/triangle_counting/rt_graph_contract.py`
- App route: `examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py`
- Test: `tests/goal4457_v3_0_m61_triangle_cupy_no_host_columns_test.py`
- Measurement artifact: `docs/reports/goal4457_v3_0_m61_triangle_cupy_no_host_columns_200000_2026-06-16.json`
