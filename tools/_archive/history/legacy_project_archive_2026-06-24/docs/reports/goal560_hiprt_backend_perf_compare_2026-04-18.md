# Goal 560: HIPRT Backend Performance Comparison

Date: 2026-04-18

Repository: `/Users/rl2025/rtdl_python_only`

Linux validation checkout: `/tmp/rtdl_goal560_hiprt_perf`

Raw result file: `/Users/rl2025/rtdl_python_only/docs/reports/goal560_hiprt_backend_perf_compare_linux_2026-04-18.json`

## Verdict

ACCEPT for a v0.9 release smoke performance/parity comparison.

HIPRT now participates in the same 18-workload matrix as Embree, OptiX, and Vulkan on the Linux host, and every backend/workload result matched the CPU Python reference. This is a correctness and availability comparison with timing evidence, not a throughput benchmark and not a speedup claim.

## Host And Backend Setup

- Host: `lx1`
- OS: Linux `6.17.0-20-generic` x86_64
- GPU: NVIDIA GeForce GTX 1070
- NVIDIA driver: `580.126.09`
- Embree runtime: `4.3.0`
- OptiX runtime: `9.0.0`
- Vulkan RTDL backend: `0.1.0`
- HIPRT runtime: `2.2.15109972`
- HIPRT SDK path used for build: `/home/lestat/vendor/hiprt-official/hiprtSdk-2.2.0e68f54`

Important boundary: this HIPRT validation is HIPRT/Orochi CUDA mode on an NVIDIA GTX 1070. It is not an AMD GPU validation, and GTX 1070 has no hardware RT cores. Do not present these numbers as AMD HIPRT or RT-core acceleration evidence.

## Commands

Build commands:

```bash
cd /tmp/rtdl_goal560_hiprt_perf
make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev CUDA_PREFIX=/usr NVCC=/usr/bin/nvcc
make build-vulkan
make build-embree
```

Runtime command:

```bash
cd /tmp/rtdl_goal560_hiprt_perf
export RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so
export RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so
export RTDL_VULKAN_LIB=$PWD/build/librtdl_vulkan.so
export LD_LIBRARY_PATH=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54/hiprt/linux64:${LD_LIBRARY_PATH:-}
PYTHONPATH=src:. python3 scripts/goal560_hiprt_backend_perf_compare.py \
  --repeats 1 \
  --backends hiprt,embree,optix,vulkan \
  --output docs/reports/goal560_hiprt_backend_perf_compare_linux_2026-04-18.json
```

Local harness smoke test:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest tests.goal560_hiprt_backend_perf_compare_test
```

Result: `Ran 2 tests in 0.001s OK`.

## Summary

- Workloads measured: 18
- Backends requested per workload: 4 (`hiprt`, `embree`, `optix`, `vulkan`)
- Backend/workload checks: 72
- Passed parity checks: 72
- Backend unavailable: 0
- Failures: 0
- Repeats: 1

The benchmark harness compares every backend result against `rt.run_cpu_python_reference` output. A backend timing is only reported as `PASS` when rows are exactly equal to the CPU reference rows for that workload.

## Median Timing Snapshot

These are one-repeat small-fixture medians from the raw JSON. They include backend startup, JIT, module setup, geometry build, and dispatch overhead.

| Workload | HIPRT s | Embree s | OptiX s | Vulkan s |
| --- | ---: | ---: | ---: | ---: |
| segment_intersection | 0.448543 | 0.010263 | 0.255554 | 0.696991 |
| point_in_polygon | 0.380712 | 0.007429 | 0.646032 | 0.315780 |
| overlay_compose | 0.419020 | 0.022935 | 0.393588 | 0.312936 |
| ray_triangle_hit_count_2d | 0.378958 | 0.000585 | 0.122359 | 0.295376 |
| ray_triangle_hit_count_3d | 0.542404 | 0.006814 | 0.126091 | 0.219787 |
| segment_polygon_hitcount | 0.416179 | 0.000255 | 0.000108 | 4.938733 |
| segment_polygon_anyhit_rows | 0.421551 | 0.000175 | 0.000128 | 0.000134 |
| point_nearest_segment | 0.367355 | 0.000202 | 0.308874 | 0.089097 |
| fixed_radius_neighbors_2d | 0.570552 | 0.000537 | 0.318816 | 0.090473 |
| fixed_radius_neighbors_3d | 0.567998 | 0.000525 | 0.319741 | 0.090968 |
| bounded_knn_rows_3d | 0.571572 | 0.000620 | 0.000330 | 0.002733 |
| knn_rows_2d | 0.567054 | 0.000408 | 0.316854 | 0.092588 |
| knn_rows_3d | 0.569451 | 0.000708 | 0.323084 | 0.092927 |
| bfs_discover | 0.556287 | 0.000558 | 0.000247 | 0.000125 |
| triangle_match | 0.554152 | 0.000485 | 0.000213 | 0.000111 |
| conjunctive_scan | 0.569038 | 0.000421 | 0.396148 | 0.301979 |
| grouped_count | 0.564011 | 0.000499 | 0.000574 | 0.004461 |
| grouped_sum | 0.565820 | 0.000468 | 0.000604 | 0.004298 |

Backend median timing range across the 18 small fixtures:

| Backend | Min s | Median s | Max s |
| --- | ---: | ---: | ---: |
| HIPRT | 0.367355 | 0.556287 | 0.571572 |
| Embree | 0.000175 | 0.000537 | 0.022935 |
| OptiX | 0.000108 | 0.255554 | 0.646032 |
| Vulkan | 0.000111 | 0.092588 | 4.938733 |

## Interpretation

HIPRT is functionally online across the full v0.9 workload set: geometric, 2D, nearest-neighbor, graph, and bounded DB-style workloads all execute through `run_hiprt` and match CPU reference output.

Performance is not yet competitive in this small-fixture path. HIPRT timings cluster around 0.36-0.57 seconds because the current implementation pays heavy per-call setup/JIT/module overhead. This is acceptable for v0.9 backend coverage, but it is not acceptable as a performance-forward claim.

Embree and some OptiX/Vulkan paths are much faster on these tiny fixtures because their current implementations either have lower startup overhead, simpler dispatch paths, or existing prepared/fast paths for specific workloads. The comparison therefore identifies the next performance target for HIPRT: prepared context reuse, module/kernel caching, and larger-scale throughput tests after setup amortization.

## Release Claim Boundary

Allowed claims:

- HIPRT backend is available on the tested Linux NVIDIA/CUDA/Orochi environment.
- HIPRT supports all 18 currently matrixed v0.9 workloads through `run_hiprt`.
- HIPRT produced exact row parity with CPU Python reference for all 18 workloads.
- Embree, OptiX, Vulkan, and HIPRT all passed the same release smoke parity matrix on Linux.

Disallowed claims:

- Do not claim AMD GPU validation.
- Do not claim RT-core acceleration from this host.
- Do not claim HIPRT is performance-leading.
- Do not use this one-repeat small-fixture smoke comparison as a throughput benchmark.

## Next Work

The next HIPRT performance goal should separate one-time preparation from repeated query dispatch. That means adding prepared HIPRT contexts for workloads where build/JIT cost dominates, then rerunning multi-repeat and larger-fixture comparisons against OptiX, Vulkan, Embree, and CPU/PostgreSQL where relevant.
