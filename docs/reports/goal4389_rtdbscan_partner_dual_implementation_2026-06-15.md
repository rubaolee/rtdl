# Goal4389 RTDBSCAN Partner Dual Implementation Supplement

Date: 2026-06-15

Status: v2.14 current evidence supplement. This closes the RTDBSCAN
best-partner plus Numba-reference gap for the current prepared-grid contract.

## Conclusion

RTDBSCAN no longer depends on a future V3.0 promise for the current partner
comparison. The benchmark app now reports the same repeat/warmup hot-query
protocol for CuPy prepared-grid continuation and Numba prepared-grid
continuation.

For the current RTDL v2.14 RTDBSCAN contract, Numba is the current best measured
partner at large scale. CuPy remains the required same-contract opponent and
evidence path, but it is not the winner on this prepared-grid component-labeling
contract.

At 524,288 clustered3d points:

- RTDL OptiX RT-core flags plus CuPy continuation: `10.661565s`.
- RTDL OptiX RT-core flags plus Numba continuation: `8.899863s`.
- Same signature: yes.
- Numba advantage over CuPy: `1.20x`.

This does not change the backend comparison rule. The RT-core-vs-Embree row
must remain fixed-continuation and same-contract. It does show that the Numba
path is not merely a slow accessibility fallback here; it is the current best
measured partner for this contract.

## Contract

Benchmark app:

- `examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`

Dataset and parameters:

- dataset: `clustered3d`
- radius: `0.055`
- min-neighbors: `12`
- scales: `4,096`, `65,536`, `262,144`, `524,288`
- repeat protocol: `--repeat 4 --warmup 1`
- reported elapsed: median of the three measured prepared-query iterations
- correctness: 4,096-point rows validated against CPU reference; all large
  rows require same-signature agreement between CuPy and Numba

RT-core modes:

- `optix_rt_core_flags_cupy_prepared_grid_components_3d`
- `optix_rt_core_flags_numba_prepared_grid_components_3d`

Pure partner modes:

- `partner_cupy_prepared_grid_components_3d`
- `partner_numba_prepared_grid_components_3d`

## RT-Core Plus Partner Results

| Points | RT+CuPy elapsed | RT+Numba elapsed | Signature equal | Winner | Numba advantage |
| ---: | ---: | ---: | --- | --- | ---: |
| 4,096 | 0.013938s | 0.014711s | yes | CuPy by tiny margin | 0.95x |
| 65,536 | 0.404125s | 0.378210s | yes | Numba | 1.07x |
| 262,144 | 3.114829s | 2.723396s | yes | Numba | 1.14x |
| 524,288 | 10.661565s | 8.899863s | yes | Numba | 1.20x |

## Pure Partner Prepared-Grid Results

| Points | CuPy elapsed | Numba elapsed | Signature equal | Winner | Numba advantage |
| ---: | ---: | ---: | --- | --- | ---: |
| 4,096 | 0.012528s | 0.011806s | yes | Numba | 1.06x |
| 65,536 | 0.526671s | 0.456513s | yes | Numba | 1.15x |
| 262,144 | 5.878373s | 5.361944s | yes | Numba | 1.10x |
| 524,288 | 22.340643s | 20.243854s | yes | Numba | 1.10x |

## 524K Phase Readout

| Mode | Prepared-query median | Prepare outside hot median | RT threshold | Continuation | Python rows | Densify |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RT+CuPy | 10.661565s | 2.666137s | 1.070107s | 8.953817s | 0.334171s | 0.306304s |
| RT+Numba | 8.899863s | 2.498170s | 1.181214s | 6.917436s | 0.344728s | 0.310608s |
| Pure CuPy | 22.340643s | 0.874885s | n/a | 21.657902s | 0.375228s | 0.309825s |
| Pure Numba | 20.243854s | 0.811750s | n/a | 19.567011s | 0.373372s | 0.308278s |

## Interpretation

The RT-core primitive matters: at 524K, RT+Numba is `2.27x` faster than pure
Numba prepared-grid continuation, and RT+CuPy is `2.10x` faster than pure CuPy
prepared-grid continuation. The native OptiX threshold stage removes a large
part of the partner-only search work.

The full app is still continuation-dominated: even in the RT+Numba winner,
`6.917s` of the `8.900s` prepared-query median is component continuation, while
the RT threshold stage is `1.181s`. Therefore the public v2.14 wording must stay
narrow: this is a fair same-contract engineering row, not a large full-app
RTDBSCAN speedup claim.

Numba remains within the project strategy. It is Python source, does not require
the benchmark user to write C++ or CUDA C kernels, and uses Numba CUDA JIT for
the continuation. For this contract it also wins over the CuPy prepared-grid
implementation, so the no-C++/CUDA-kernel-writing path is not merely a
convenience fallback.

## Evidence Files

All evidence files are under:

- `docs/reports/goal4389_rtdbscan_partner_dual_implementation_2026-06-15/`

Representative files:

- `optix_rt_core_flags_cupy_prepared_grid_components_3d_clustered3d_524288_r4w1_no_validation.json`
- `optix_rt_core_flags_numba_prepared_grid_components_3d_clustered3d_524288_r4w1_no_validation.json`
- `partner_cupy_prepared_grid_components_3d_clustered3d_524288_r4w1_no_validation.json`
- `partner_numba_prepared_grid_components_3d_clustered3d_524288_r4w1_no_validation.json`

## v2.14 Effect

RTDBSCAN is now acceptable on two separate axes:

1. Backend comparison: fixed Numba continuation keeps OptiX-vs-Embree fair.
2. Partner comparison: same-contract CuPy and Numba rows are both measured, and
   Numba is the current large-scale winner.

No claim here depends on V3.0.
