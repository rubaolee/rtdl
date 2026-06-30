# Goal2606 GPU-RMQ Generic Two-Source Grouped Merge

Date: 2026-05-24

## Purpose

Goal2605 removed repeated group/value/index uploads by preparing grouped-argmin
input handles. The GPU-RMQ app still launched two generic grouped reductions:
one for element-phase triangles and one for full-block triangles. Python then
downloaded two per-query result arrays and merged them.

Goal2606 moves only that cross-source grouped merge into a generic native
primitive:

- source A: prepared scene, prepared ray batch, prepared grouped-argmin inputs;
- source B: prepared scene, prepared ray batch, prepared grouped-argmin inputs;
- operation: closest-hit grouped argmin for each source, then per-group min
  merge with the same value/index tie-break rule;
- output: one final per-group result array.

The primitive is still app-agnostic. It does not know RMQ, blocks, query ranges,
phase names, or sparse-table structure.

## Implementation

Native OptiX:

- added CUDA kernel `closest_hit_grouped_argmin_merge_two`;
- added generic ABI
  `rtdl_optix_static_triangle_scene_3d_two_ray_batches_closest_hit_prepared_grouped_argmin`;
- factored prepared grouped-argmin execution so it can produce device-resident
  per-source grouped results without immediately downloading them;
- merged source A and source B on the device and downloaded one final grouped
  result.

Python runtime:

- added
  `PreparedOptixStaticTriangleScene3D.two_scene_ray_closest_hit_prepared_grouped_argmin`;
- metadata records
  `PREPARED_TRIANGLE_SCENE_3D_TWO_PREPARED_RAY_BATCHES_PREPARED_GROUPED_ARGMIN_V1`;
- transfer metadata marks `python_cross_source_merge: False` and
  `native_device_two_source_merge: True`.

GPU-RMQ app:

- uses the two-source primitive when element and full-block prepared ray batches
  and prepared grouped inputs are available;
- preserves the single-source grouped path and compact-array fallback for
  smaller or partial workloads.

## Validation

Local Mac:

```text
PYTHONPATH=src:. python3 -m py_compile \
  src/rtdsl/optix_runtime.py \
  examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py

PYTHONPATH=src:. python3 -m unittest \
  tests.goal2594_gpu_rmq_benchmark_front_door_test \
  tests.goal2598_optix_generic_closest_hit_contract_test -v

Ran 20 tests in 0.155s
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

Ran 20 tests in 0.690s
OK
```

## Performance

Prepared-reuse public app entry point, 12 repeated query runs on the RTX A5000
pod. All payloads matched the exact CPU oracle.

| Case | Path | Median query time | ns/query | QPS |
| --- | --- | ---: | ---: | ---: |
| repeated 4K values / 1K queries / block 64 | compact NumPy arrays | 0.5588 ms | 558.83 | 1.79M |
| random 16K values / 4K queries / block 256 | native two-source grouped merge | 0.6475 ms | 161.87 | 6.18M |
| repeated 64K values / 8K queries / block 512 | native two-source grouped merge | 1.2724 ms | 159.05 | 6.29M |

Comparison against prior prepared paths:

| Case | Goal2603 prepared ray compact | Goal2605 prepared grouped inputs | Goal2606 two-source merge |
| --- | ---: | ---: | ---: |
| repeated 4K / 1K / block 64 | 0.5454 ms | 0.5475 ms | 0.5588 ms |
| random 16K / 4K / block 256 | 1.5852 ms | 0.6592 ms | 0.6475 ms |
| repeated 64K / 8K / block 512 | 1.9323 ms | 1.4525 ms | 1.2724 ms |

The small case stays on compact arrays because the extra grouped-reduction
boundary is not worthwhile there.

## Interpretation

The two-source merge confirms the current bottleneck was not just RT traversal.
Avoiding a second per-group download plus Python cross-source merge helps most
on the larger 64K/8K workload. The 16K/4K gain is smaller because the total
group count and output transfer are already modest after Goal2605.

This remains a generic runtime feature. Other apps with multiple independent
prepared grouped reductions can use the same two-source merge without adding
application-specific native code.

## Conclusion

Goal2606 is now the best measured GPU-RMQ RTDL path for medium and large
prepared batches. It keeps app semantics in Python and moves only a generic
two-source grouped argmin merge into native OptiX.

This is benchmark engineering evidence, not a public speedup claim.
