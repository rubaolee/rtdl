# Goal4506 / V3 M110 RTNN Chunked Runtime

## Conclusion

The M19 RTNN partner-continuation route now has measured chunked runtime evidence on a 1,048,576-query uniform workload. The route executed 16 explicit 65,536-query chunks, reused the prepared scene across chunks, prepared query points and CUDA graph state per chunk, ran both CuPy and Numba same-stream device reductions, matched combined signatures, and kept result materialization after the hot window. This does not authorize public speedup wording or comparison against the aggregate-only full-batch direct route because the output contracts differ.

## Measured Row

| Field | Value |
| --- | ---: |
| raw evidence | `docs/reports/goal4506_rtnn_chunked_uniform_1048576q1048576_w1r3_2026-06-17.json` |
| point/query count | 1,048,576 |
| chunk count | 16 |
| max query count per chunk | 65,536 |
| warmups / repeats | 1 / 3 |
| CuPy hot median-sum | 0.082908s |
| Numba hot median-sum | 0.083390s |
| signature match | `True` |
| no-hidden-column-copy hot gate | `True` |
| materialization after hot window | `True` |

## Boundary

- This is large chunked runtime evidence for the same-stream partner-continuation route.
- It is not aggregate-only full-batch direct evidence and must not be compared as the same output contract.
- Public speedup, RT-core speedup, whole-app speedup, true-zero-copy, and automatic partner-selection claims remain blocked.
- The Numba toolchain is auto-configured through `configure_numba_cuda_toolchain_environment()` so the pod uses CUDA 12.4 ptxas/NVVM instead of emitting unsupported PTX 8.7.
