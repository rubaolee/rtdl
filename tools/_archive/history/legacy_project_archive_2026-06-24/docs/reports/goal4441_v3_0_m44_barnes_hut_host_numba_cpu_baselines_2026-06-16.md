# Goal4441 / V3.0 M44 - Barnes-Hut Host Numba CPU Baselines

## Result

M44 adds optimized no-C++ CPU continuation modes for the Barnes-Hut prepared
aggregate-frontier route:

```text
aggregate_frontier_weighted_vector_cpu_host_numba
aggregate_frontier_weighted_vector_embree_host_numba
```

These modes keep the same logical frontier/vector semantics as M43, but replace
the Python dict-based host vector accumulation with a Numba CPU `njit`
continuation over `frontier_i64_rows` and `row_offsets`. The continuation is
parallelized by source, so it avoids atomics and does not require C++, CUDA
source, or RawKernel code.
They replace the Python dict-based host vector accumulation.

## 8192-Body Matrix

Configuration:

- RTX 4000 Ada pod
- 8192 bodies
- bucket size 64
- theta 0.5
- app softening 0.05
- `--warmup 1 --repeat 5`
- validation skipped for the 8192-body timing rows
- force rows suppressed with `--force-output-mode force_summary`

| Route | Frontier rows | Frontier collect | Vector continuation | Frontier+vector hot | Total wall |
| --- | ---: | ---: | ---: | ---: | ---: |
| CPU host + Python vector | 3,406,489 | 6.938711 s | 3.146279 s | 10.084990 s | 10.231974 s |
| CPU host + Numba CPU vector | 3,406,489 | 6.911888 s | 0.004341 s | 6.916229 s | 10.066979 s |
| Embree host + Python vector | 3,406,489 | 8.064940 s | 3.269292 s | 11.334233 s | 11.480454 s |
| Embree host + Numba CPU vector | 3,406,489 | 8.121634 s | 0.004800 s | 8.126434 s | 11.015057 s |
| RTDL/OptiX + Numba GPU vector | 3,406,489 | 0.014865 s | 0.001296 s | 0.016139 s | 0.022338 s |

The M44 optimized continuation improves the measured CPU-side vector phase by:

| Baseline | Python vector | Numba CPU vector | Vector-phase improvement |
| --- | ---: | ---: | ---: |
| CPU host | 3.146279 s | 0.004341 s | 724.7x |
| Embree host | 3.269292 s | 0.004800 s | 681.1x |

Checksum agreement remains tight:

| Route | checksum force x | checksum force y |
| --- | ---: | ---: |
| CPU host + Numba CPU vector | -1836.571773996123 | 4948.320604887711 |
| Embree host + Numba CPU vector | -1836.571773996123 | 4948.320604887711 |
| RTDL/OptiX + Numba GPU vector | -1836.5717739965667 | 4948.320604887265 |

## Interpretation

M44 removes a real optimization debt. The CPU/Embree host baselines no longer
lose the force-vector continuation because of Python dict accumulation.

After this fix, the remaining Barnes-Hut CPU-side bottleneck is not the vector
math. It is aggregate-frontier collection and host row materialization:

- CPU host + Numba CPU vector: 6.911888 s frontier collect versus 0.004341 s
  vector continuation.
- Embree host + Numba CPU vector: 8.121634 s frontier collect versus 0.004800 s
  vector continuation.

Against the M42 RTDL/OptiX + Numba hot window, the optimized host baselines are
still diagnostic-only ratios:

| Comparison | Ratio | Boundary |
| --- | ---: | --- |
| CPU host+Numba frontier+vector / OptiX+Numba hot | 428.5x | diagnostic; host-materialized versus device-resident |
| Embree host+Numba frontier+vector / OptiX+Numba hot | 503.5x | diagnostic; host-materialized versus device-resident |

These ratios are engineering evidence, not public backend speedup claims.

## 128-Body Correctness Smokes

Both Numba CPU host modes were run at 128 bodies with CPU reference validation
enabled.

| Route | Frontier rows | max abs diff x | max abs diff y | Result |
| --- | ---: | ---: | ---: | --- |
| CPU host + Numba CPU vector | 8,766 | 0.0 | 0.0 | pass |
| Embree host + Numba CPU vector | 8,766 | 0.0 | 0.0 | pass |

## Boundary

What M44 can say:

- The CPU-side vector continuation for the host baselines is now optimized with
  a no-C++ Numba CPU partner.
- The optimized continuation matches the reference and the OptiX route's
  checksum at the measured scales.
- The remaining backend gap is concentrated in frontier collection and host
  row materialization.

What M44 cannot say:

- It is still not a same device-resident OptiX-vs-Embree comparison.
- It is still not a public RT-core or GPU-vs-CPU speedup claim.
- It does not prove whole Barnes-Hut N-body acceleration.
- It does not authorize automatic partner selection.

## Raw Evidence

- `docs/reports/goal4441_v3_0_m44_barnes_hut_cpu_host_numba_128_smoke_2026-06-16.json`
- `docs/reports/goal4441_v3_0_m44_barnes_hut_embree_host_numba_128_smoke_2026-06-16.json`
- `docs/reports/goal4441_v3_0_m44_barnes_hut_cpu_host_numba_8192_2026-06-16.json`
- `docs/reports/goal4441_v3_0_m44_barnes_hut_embree_host_numba_8192_2026-06-16.json`
- `docs/reports/goal4440_v3_0_m43_barnes_hut_cpu_host_8192_2026-06-16.json`
- `docs/reports/goal4440_v3_0_m43_barnes_hut_embree_host_8192_2026-06-16.json`
- `docs/reports/goal4439_v3_0_m42_barnes_hut_app_mode_numba_8192_2026-06-16.json`

## Next

The next clean target is the frontier side, not more vector continuation work:
avoid or fuse host row materialization on the CPU/Embree baseline, or explicitly
keep Barnes-Hut backend comparisons scoped as diagnostic until such a baseline
exists.
