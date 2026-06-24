# Goal4450 / V3.0 M54 - Barnes-Hut Fused Numba CUDA App Mode

Status: complete internal V3 evidence.

Goal4450 wires the reusable M53 aggregate-tree fused Numba CUDA partner API into
the Barnes-Hut benchmark front door:

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py \
  --mode fused_frontier_force_sum_bucketized_numba_cuda \
  --body-count 8192 --bucket-size 64 --theta 0.5 \
  --skip-validation --warmup 2 --repeat 11 --force-output-mode force_summary
```

The mode calls:

```python
rt.prepare_aggregate_tree_fused_weighted_vectors_2d_numba_cuda(...)
```

It is the app-facing path for the no-C++ fused GPU partner route. It avoids
frontier rows and contribution rows, but it is not an RT-core primitive and does
not authorize Barnes-Hut RT-core speedup wording.

## Pod Evidence

Machine: NVIDIA/CUDA pod used for V3 M52/M53 evidence.

| Run | Bodies | Bucket | Theta | Validation | Contribution rows | Kernel median | Partner wall median | Call wall median |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| 64 smoke | 64 | 8 | 0.5 | passed vs CPU reference | 2,091 | 0.350 ms | 0.499 ms | 0.784 ms |
| 8192 r11 | 8,192 | 64 | 0.5 | skipped by request | 3,406,489 | 3.312 ms | 3.497 ms | 3.738 ms |

The 64-body smoke matched the CPU reference with max absolute differences:

| Axis | Max absolute difference |
| --- | ---: |
| x | `7.993605777301127e-15` |
| y | `7.105427357601002e-15` |

The 8192 checksum matches the M52 validation-scale checksum within normal
floating-point ordering noise:

| Metric | Value |
| --- | ---: |
| checksum x | `-1836.571773996014` |
| checksum y | `4948.3206048876245` |

## Comparison To M52

M52's standalone prototype recorded an 8192-body kernel median of `3.207 ms`.
The M54 app front-door mode records `3.312 ms`. That is the expected result: the
front door preserves the same fused workload shape and adds benchmark payload
packaging, metadata, and app-mode dispatch without materially changing the hot
kernel path.

For the same 8192/body-count ladder, M52 reported:

| Baseline | Hot time | Reading |
| --- | ---: | --- |
| M41 prepared RTDL/OptiX+Numba | `14.712 ms` | M52 fused CUDA was 4.59x faster |
| M42 prepared app-mode RTDL/OptiX+Numba | `16.139 ms` | M52 fused CUDA was 5.03x faster |
| M45 fused CPU/Numba | `1.304 ms` | M52 fused CUDA was 2.46x slower at 8192 |

M54 does not change those conclusions. It makes the fused CUDA route runnable
from the benchmark app itself.

## Claim Boundary

- This is a Barnes-Hut app front-door route for a reusable, app-agnostic
  aggregate-tree fused weighted-vector partner API.
- It uses Numba CUDA Python source. No C++ extension, raw CUDA file, or Torch
  extension is required.
- It does not use RT cores.
- It does not compare OptiX and Embree.
- It does not prove RT-core acceleration for Barnes-Hut.
- It does prove that the current highest-performance no-C++ GPU direction is
  fused traversal plus force accumulation without frontier/contribution row
  materialization.

## Artifacts

- `docs/reports/goal4450_v3_0_m54_barnes_hut_numba_cuda_app_mode_64_smoke_2026-06-16.json`
- `docs/reports/goal4450_v3_0_m54_barnes_hut_numba_cuda_app_mode_8192_r11_2026-06-16.json`
- `tests/goal4450_v3_0_m54_barnes_hut_numba_cuda_app_mode_test.py`
