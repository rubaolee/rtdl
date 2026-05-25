# Goal2602 GPU-RMQ Generic Grouped-Argmin Runtime Boundary

Date: 2026-05-24

## Purpose

Goal2601 showed that prepared OptiX scenes plus compact closest-hit row arrays
made the GPU-RMQ benchmark credible. The remaining app-side bottleneck was that
GPU-RMQ still owned the repeated `closest-hit rows -> per-query argmin` assembly.

This goal promotes that step into a generic runtime boundary:

- Input: prepared static 3-D triangle scene, rays, ray-id-to-group map,
  triangle-id-to-candidate-value map, and triangle-id-to-candidate-index map.
- Output: per-group `has_value`, `index`, and `value` arrays.
- Reduction rule: minimum value, tie-broken by smaller index.
- Native engine vocabulary remains app-agnostic. There is no GPU-RMQ formula,
  query range logic, block logic, or app name in the native ABI.

The current implementation performs the grouped argmin in native host code after
the OptiX closest-hit traversal downloads the generic per-ray records. It is not
yet a true device-side final combine or zero-copy path. The ABI is deliberately
shaped so a future CUDA-side grouped reducer can replace the native-host combine
without changing app code.

## Implemented Changes

- Added OptiX ABI:
  `rtdl_optix_static_triangle_scene_3d_ray_closest_hit_grouped_argmin`.
- Added runtime API:
  `PreparedOptixStaticTriangleScene3D.ray_closest_hit_grouped_argmin`.
- Added a fallback that derives the same grouped argmin from generic closest-hit
  row arrays when the native grouped symbol is unavailable.
- Updated GPU-RMQ `PreparedPaperRtRmq.query_arrays` to use the generic grouped
  argmin boundary for element phases and full-block phases.
- Kept final cross-phase selection in Python because it is app scheduling logic:
  same-block, left-partial, right-partial, and full-block phases are GPU-RMQ
  concepts, not native engine concepts.
- Added source-contract tests for the new generic ABI and benchmark boundary.

## Pod Evidence

Pod:

- SSH: `root@203.57.40.101 -p 10082`
- Key used from Mac: `~/.ssh/id_ed25519_rtdl_codex`
- Remote repo: `/workspace/rtdl_goal2598`
- Backend library: `/workspace/rtdl_goal2598/build/librtdl_optix.so`
- GPU: NVIDIA RTX A5000

Build:

```text
make build-optix OPTIX_PREFIX=/workspace/optix-8.1 CUDA_PREFIX=/usr/local/cuda
```

Validation:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/workspace/rtdl_goal2598/build/librtdl_optix.so \
  python3 -m unittest \
  tests.goal2594_gpu_rmq_benchmark_front_door_test \
  tests.goal2598_optix_generic_closest_hit_contract_test -v

Ran 20 tests in 0.810s
OK
```

## Performance

All rows matched the exact CPU oracle. Times below are prepared-query medians
from six repeated query batches on the RTX A5000 pod. The first 4K run includes a
one-time warmup outlier, but the median remains stable because six runs were
recorded.

| Case | Prior prepared compact query | New grouped-argmin query | Delta |
| --- | ---: | ---: | ---: |
| repeated 4K values / 1K queries | 1.63 ms | 1.55 ms | 1.05x faster |
| random 16K values / 4K queries | 2.76 ms | 2.83 ms | 0.97x, within noise/slight regression |
| repeated 64K values / 8K queries | 6.87 ms | 5.49 ms | 1.25x faster |

Raw new runs:

| Case | Query runs, ms | Median, ms | Warmup-excluded median, ms |
| --- | --- | ---: | ---: |
| repeated 4K / 1K | 83.7821, 1.6369, 1.5486, 1.5393, 1.5447, 1.5373 | 1.5466 | 1.5447 |
| random 16K / 4K | 3.3347, 2.8616, 2.8120, 2.8169, 2.8001, 2.8510 | 2.8339 | 2.8169 |
| repeated 64K / 8K | 6.0772, 5.5179, 5.4842, 5.4676, 5.4824, 5.4984 | 5.4913 | 5.4842 |

Each phase reported `native_grouped_argmin=true`:

- `same_block`
- `left_partial`
- `right_partial`
- `full_blocks`

## Conclusion

This is a real runtime boundary improvement, not an app-specific engine shortcut.
It removes another layer of GPU-RMQ-owned result assembly and exposes a reusable
primitive shape: closest-hit records grouped by caller-provided ray ids, reduced
by caller-provided candidate maps.

The result is positive but bounded:

- Correctness: passes exact CPU oracle on the tested workloads.
- Engine purity: preserved; no GPU-RMQ semantics entered native OptiX.
- Performance: improves the largest prior case by about 25%, keeps small cases
  roughly stable, and shows a slight 16K regression that is likely overhead/noise.
- Remaining runtime target: move the grouped argmin combine from native host code
  to a generic CUDA-side reducer and reduce or eliminate closest-hit record
  download for this class of workloads.
