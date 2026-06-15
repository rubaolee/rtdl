# V3.0 M9 Grouped-Stream Partner Evidence

Date: 2026-06-15

Status: passed for OptiX grouped-stream device-resident partner evidence; no public speedup or true-zero-copy claim.

## Result

M9 wraps an existing generic OptiX grouped-stream route with two explicit partners:

- CuPy
- Numba

The route exercises `prepared_rt_core_grouped_union_3d_all_items_self_query` and records device pointers for `point_ids`, `component_labels`, `is_core`, and `neighbor_counts`. Both partners produced matching component-size signatures at all tested scales.

## Numba/PTX Fix

The previous blocker was real: Numba emitted PTX 8.7 while the pod's NVIDIA 550 driver JIT accepted PTX up to 8.4. M9 fixes the runner by using the packaged CUDA 12.4 NVVM path before RTDL imports Numba-facing modules, then re-execing once so the dynamic loader sees `libnvvm.so` at process start.

The final working settings are:

- `CUDA_HOME=/usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvcc`
- `LD_LIBRARY_PATH` prefixed with `/usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvcc/nvvm/lib64`
- `PATH` prefixed with `/usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvcc/bin`
- `NUMBA_CUDA_ENABLE_MINOR_VERSION_COMPATIBILITY=0`

Two older Numba availability guards were also hardened to accept `cuda.get_current_device()` as proof when `cuda.is_available()` is a false negative under this compatibility setup.

## Perf Matrix

| Point Count | CuPy Median | Numba Median | CuPy/Numba | Native Path | Signature Match |
| ---: | ---: | ---: | ---: | --- | --- |
| 512 | 0.000355s | 0.000483s | 0.735x | RT grouped union | yes |
| 8,192 | 0.000388s | 0.000509s | 0.762x | RT grouped union | yes |
| 65,536 | 0.000598s | 0.000721s | 0.830x | RT grouped union | yes |

Raw evidence:

- `docs/reports/goal4403_v3_0_m9_grouped_stream_partner_512_2026-06-15.json`
- `docs/reports/goal4403_v3_0_m9_grouped_stream_partner_8192_2026-06-15.json`
- `docs/reports/goal4403_v3_0_m9_grouped_stream_partner_65536_2026-06-15.json`

## Interpretation

This is not a human-scale benchmark result; the all-core grouped-union path is too small and too fast for public performance wording. Its value is architectural evidence:

1. The Numba/PTX blocker is solved for this route on the pod.
2. CuPy and Numba are both viable explicit partner choices for the grouped-stream continuation.
3. RTDL records device-resident output pointers and avoids neighbor-row materialization.
4. The V3 instrumentation correctly says `device_resident_ready=true`.
5. The same packet correctly says `same_stream_ready=false` and `true_zero_copy_ready=false`, because stream-ordering and transfer-counter evidence are not yet complete.

## Next Gate

The next V3 step should turn M9 into a stricter same-stream evidence gate:

- capture CUDA event pairs around the native RT phase and partner continuation
- record transfer counters or equivalent no-hidden-copy evidence
- keep CuPy and Numba rows side by side
- run a nontrivial predicate/mixed-core case where the continuation does real work
- only then consider benchmark-scale backend comparisons
