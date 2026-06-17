# Goal4512 / V3 M116 Barnes-Hut Clean-Target Audit

## Conclusion

Barnes-Hut is closed as a current V3 route-policy target, not as an RT-core acceleration success. Use fused CPU/Numba for the tested 8192/16384/32768 rows, fused Numba CUDA for the tested 65536/131072 rows, and prepared RTDL/OptiX+Numba only as RT-core aggregate-frontier device-column evidence. A real Barnes-Hut RT-core win requires the future app-agnostic RT-native fused weighted-vector primitive from Goal4497.

## Current Route Matrix

| Bodies | Source | Fastest route | Best time | OptiX+Numba time | OptiX+Numba slower than best |
| ---: | --- | --- | ---: | ---: | ---: |
| 8,192 | Goal4458 | `cpu_numba_fused` | 0.001396s | 0.015277s | 10.94x |
| 16,384 | Goal4458 | `cpu_numba_fused` | 0.008050s | 0.030776s | 3.82x |
| 32,768 | Goal4458 | `cpu_numba_fused` | 0.007268s | 0.082250s | 11.32x |
| 65,536 | Goal4483 | `numba_cuda_fused` | 0.033964s | 0.179026s | 5.27x |
| 131,072 | Goal4483 | `numba_cuda_fused` | 0.044909s | 0.618309s | 13.77x |

## Route Policy

- Small tested rows: `fused_frontier_force_sum_bucketized_cpu_numba`.
- Large tested rows: `fused_frontier_force_sum_bucketized_numba_cuda`.
- RT evidence row: `prepared_aggregate_frontier_weighted_vector_optix --partner numba`.
- Prepared RTDL/OptiX+Numba loses all measured rows to the current fused route.
- Fused Numba CUDA is no-C++ Python-source GPU partner evidence; it is not RT-core evidence.

## Future RT-Native Primitive

- Required contract: `generic_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_v1`.
- Implemented now: `False`.
- Purpose: Fuse aggregate-tree traversal, opening-rule acceptance, exact leaf fallback, and weighted vector accumulation inside an RT-native/device execution path.
- Must avoid: aggregate-frontier row emission, host frontier materialization, host contribution materialization, app-specific native callbacks, and automatic partner dispatch.

## M113 Applicability

- Current route should use M113: `False`.
- Reason: Barnes-Hut does not need a prepared graph chunk executor for the current bottleneck. It needs a fused weighted-vector RT-native primitive that combines traversal, opening acceptance, exact fallback, and vector accumulation without aggregate-frontier row emission.

## Closed

- Scale-dependent current route guidance is explicit and evidence-bounded.
- Prepared RTDL/OptiX+Numba is correctly scoped as RT-core device-column evidence.
- More aggregate-frontier row-emission tuning is not the final RT-core Barnes-Hut path.

## Still Blocked

- Public Barnes-Hut RT-core speedup wording.
- Whole-application speedup wording.
- Automatic route or partner selection.
- Claiming V3 already has the future RT-native fused weighted-vector primitive.
