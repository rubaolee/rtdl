# Goal2605 GPU-RMQ Prepared Grouped-Argmin Inputs

Date: 2026-05-24

## Purpose

Goal2604 showed that generic prepared-ray grouped argmin is the right direction
for medium/large GPU-RMQ batches, but each query still uploaded the group map,
candidate values, and candidate tie-break indices. This goal removes that
repeated transfer with a generic prepared grouped-input handle.

No GPU-RMQ-specific native code was added. The new native handle stores only:

- `ray_group_ids`: map from caller-owned ray ids to output group ids;
- `candidate_values`: map from closest-hit triangle ids to values;
- `candidate_indices`: caller-owned tie-break indices;
- reusable grouped output scratch arrays.

The handle does not know RMQ, ranges, blocks, sparse tables, or queries.

## Implementation

Native OptiX:

- added `PreparedClosestHitGroupedArgmin3D`;
- extended `PreparedRayBatch3D` with a reusable closest-hit output buffer;
- added `rtdl_optix_closest_hit_grouped_argmin_inputs_3d_create`;
- added `rtdl_optix_closest_hit_grouped_argmin_inputs_3d_destroy`;
- added `rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin`.

Python runtime:

- added `PreparedOptixClosestHitGroupedArgmin3D`;
- added `PreparedOptixStaticTriangleScene3D.prepare_closest_hit_grouped_argmin_inputs`;
- added `PreparedOptixStaticTriangleScene3D.ray_closest_hit_prepared_grouped_argmin`;
- metadata records `PREPARED_TRIANGLE_SCENE_3D_PREPARED_RAY_BATCH_PREPARED_GROUPED_ARGMIN_V1`.

GPU-RMQ app:

- prepares grouped-input handles inside `PreparedPaperRtRmq.prepare_query_batch`
  for larger batches only;
- uses prepared grouped inputs when both the prepared ray batch and prepared
  grouped-input handle are available;
- keeps compact arrays for small batches and fallback safety.

## Validation

Local Mac:

```text
PYTHONPATH=src:. python3 -m py_compile \
  src/rtdsl/optix_runtime.py \
  examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py

PYTHONPATH=src:. python3 -m unittest \
  tests.goal2594_gpu_rmq_benchmark_front_door_test \
  tests.goal2598_optix_generic_closest_hit_contract_test -v

Ran 20 tests in 0.162s
OK (skipped=1)
```

Pod:

- SSH: `root@203.57.40.101 -p 10082`
- Key used from Mac: `~/.ssh/id_ed25519_rtdl_codex`
- Remote repo: `/workspace/rtdl_goal2598`
- Backend library: `/workspace/rtdl_goal2598/build/librtdl_optix.so`
- GPU: NVIDIA RTX A5000
- OptiX SDK: `/workspace/optix-8.1`
- CUDA prefix: `/usr/local/cuda`

```text
make build-optix OPTIX_PREFIX=/workspace/optix-8.1 CUDA_PREFIX=/usr/local/cuda

PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/workspace/rtdl_goal2598/build/librtdl_optix.so \
  python3 -m unittest \
  tests.goal2594_gpu_rmq_benchmark_front_door_test \
  tests.goal2598_optix_generic_closest_hit_contract_test -v

Ran 20 tests in 0.743s
OK
```

## Performance

Prepared-reuse public app entry point, 10 repeated query runs on the RTX A5000
pod. All measured payloads matched the exact CPU oracle. The first run may
include one-time OptiX/CUDA initialization; the median is robust to that outlier.

| Case | Auto row format | Prepared grouped inputs | Median query time | ns/query | QPS |
| --- | --- | --- | ---: | ---: | ---: |
| repeated 4K values / 1K queries / block 64 | compact NumPy arrays | no | 0.5475 ms | 547.53 | 1.83M |
| random 16K values / 4K queries / block 256 | native grouped argmin | yes | 0.6592 ms | 164.81 | 6.07M |
| repeated 64K values / 8K queries / block 512 | native grouped argmin | yes | 1.4525 ms | 181.56 | 5.51M |

Comparison against the previous prepared paths:

| Case | Goal2603 prepared ray compact | Goal2604 grouped, host maps | Goal2605 prepared grouped inputs |
| --- | ---: | ---: | ---: |
| repeated 4K / 1K / block 64 | 0.5454 ms | 0.5700 ms | 0.5475 ms |
| random 16K / 4K / block 256 | 1.5852 ms | 1.5085 ms | 0.6592 ms |
| repeated 64K / 8K / block 512 | 1.9323 ms | 1.6694 ms | 1.4525 ms |

Query-batch preparation cost remains small and is paid once per fixed query
set:

| Case | Query-batch prepare |
| --- | ---: |
| random 16K / 4K / block 256 | 2.901 ms |
| repeated 64K / 8K / block 512 | 3.530 ms |

## Interpretation

Prepared grouped inputs are a strong generic runtime improvement:

- they avoid repeated group/value/index upload for repeated prepared query
  batches;
- they reuse grouped output scratch arrays;
- prepared ray batches also reuse closest-hit output scratch space;
- they keep the engine app-independent;
- they substantially reduce medium/large GPU-RMQ query time.

The remaining cost still includes closest-hit output scratch allocation inside
host-launched OptiX parameter buffers and host download of per-group result
arrays. Those are generic runtime concerns and can be considered later, but this
goal already turns the main repeated-map overhead into one-time query-batch
preparation.

## Conclusion

Goal2605 is the current best GPU-RMQ RTDL path for medium and large prepared
batches. It preserves the Python+partner+RTDL design: Python owns the app
semantics, while native OptiX owns generic prepared scene/ray/grouped-reduction
execution.

This is benchmark engineering evidence, not a public speedup claim.
