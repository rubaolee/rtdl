# Goal4458 / V3.0 M62 - Barnes-Hut Current Route Rerank

Status: complete internal V3 evidence.

M62 reruns the current Barnes-Hut app front doors under one force-summary
contract:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
python scripts/v3_0_m62_barnes_hut_current_route_rerank.py \
  --body-counts 8192,16384,32768 --repeat 31 --warmup 3 \
  --output docs/reports/goal4458_v3_0_m62_barnes_hut_current_route_rerank_2026-06-16.json
```

All rows use theta `0.5`, bucket size `64`, max depth `32`, force-summary
output, 31 measured repeats, and 3 warmups on the RTX 4000 Ada pod.

## Result

The current fastest measured Barnes-Hut route is still the fused CPU/Numba
route. The fused Numba CUDA route is the no-C++ GPU fused partner lane. The
prepared RTDL/OptiX route is valid RT-core aggregate-frontier device-column
evidence, but it is not the fastest force-summary route and does not authorize
Barnes-Hut RT-core speedup wording.

| Bodies | Fused CPU/Numba | Fused Numba CUDA | Prepared OptiX+Numba | Prepared OptiX+CuPy | Fastest |
| ---: | ---: | ---: | ---: | ---: | --- |
| 8,192 | 1.396 ms | 3.283 ms | 15.277 ms | 22.264 ms | CPU/Numba |
| 16,384 | 8.050 ms | 8.418 ms | 30.776 ms | 61.790 ms | CPU/Numba |
| 32,768 | 7.268 ms | 10.638 ms | 82.250 ms | 119.221 ms | CPU/Numba |

Diagnostic ratios:

| Bodies | Numba CUDA / CPU Numba | OptiX+Numba / CPU Numba | OptiX+Numba / Numba CUDA | OptiX+CuPy / OptiX+Numba |
| ---: | ---: | ---: | ---: | ---: |
| 8,192 | 2.35x slower | 10.94x slower | 4.65x slower | 1.46x slower |
| 16,384 | 1.05x slower | 3.82x slower | 3.66x slower | 2.01x slower |
| 32,768 | 1.46x slower | 11.32x slower | 7.73x slower | 1.45x slower |

The 32,768-body CPU/Numba median is lower than the 16,384-body median on this
pod run. Read that as CPU scheduling/tree-shape timing noise, not as a monotonic
scaling law. The route ordering is still clear enough for current guidance.

## Correctness Shape

The large timing rows skip full CPU-reference validation, but all four routes
agree on contribution counts and force checksums within floating-point ordering
noise for each body count.

| Bodies | Contribution rows |
| ---: | ---: |
| 8,192 | 3,406,489 |
| 16,384 | 12,727,680 |
| 32,768 | 15,514,679 |

The prepared OptiX rows report `rt_core_accelerated_metadata=true`. The fused
CPU/Numba and fused Numba CUDA rows report `rt_core_accelerated_metadata=false`.

## Interpretation

M45 showed that eliminating frontier-row materialization makes CPU/Numba much
faster than the older prepared RTDL/OptiX+Numba route. M52/M54 showed the same
lesson on the GPU side: a fused Numba CUDA traversal-plus-force route beats the
prepared aggregate-frontier row-emission contract.

M62 confirms the current app front doors still have that shape. For Barnes-Hut,
the key performance boundary is not "GPU versus CPU" or "RT cores versus CPU
cores" yet. It is whether the route fuses tree traversal and force accumulation
instead of emitting aggregate-frontier rows and then reducing them.

## Claim Boundary

What M62 can say:

- Current Barnes-Hut route guidance is mixed explicit.
- `fused_frontier_force_sum_bucketized_cpu_numba` is the fastest measured route
  in this rerank.
- `fused_frontier_force_sum_bucketized_numba_cuda` is the current no-C++ GPU
  fused partner route.
- `prepared_aggregate_frontier_weighted_vector_optix --partner numba` remains
  RTDL/OptiX RT-core aggregate-frontier device-column evidence.
- For the prepared OptiX contract, Numba is faster than CuPy on this run.

What M62 cannot say:

- It is not a Barnes-Hut RT-core speedup claim.
- It is not an OptiX-vs-Embree publication row.
- It is not a whole N-body speedup claim.
- It does not authorize automatic route or partner selection.
- It does not prove a fused RT-native/device route is impossible; it shows that
  such a route must avoid aggregate-frontier row emission to be competitive.

## Artifacts

- `scripts/v3_0_m62_barnes_hut_current_route_rerank.py`
- `docs/reports/goal4458_v3_0_m62_barnes_hut_current_route_rerank_2026-06-16.json`
- `tests/goal4458_v3_0_m62_barnes_hut_current_route_rerank_test.py`
