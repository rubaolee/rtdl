# Goal2604 GPU-RMQ Prepared-Ray Grouped-Argmin Auto Path

Date: 2026-05-24

## Purpose

Goal2603 made the fastest GPU-RMQ path a phase-batched compact closest-hit
array path. This follow-up promotes the generic grouped-argmin boundary into
the prepared app path where it is beneficial, without adding RMQ semantics to
native OptiX.

The native/runtime contract remains app-agnostic:

- input: prepared static triangle scene, rays or prepared ray batch, ray-id to
  group map, caller-owned candidate values, caller-owned tie-break indices;
- operation: closest-hit triangle id followed by grouped argmin;
- output: one value/index/has-value record per group;
- no RMQ names, block ranges, query intervals, or min-table logic in native
  OptiX.

## Implementation

`PreparedPaperRtRmq.query_prepared_batch_arrays` now uses an auto strategy:

- small prepared batches keep the compact closest-hit array path;
- larger prepared batches use generic prepared-ray grouped argmin when native
  prepared ray batches are available;
- any grouped-argmin runtime failure falls back to the compact closest-hit array
  path and records the fallback reason in metadata.

The app-side lowering is still responsible for RMQ-specific work: block
construction, phase scheduling, ray construction, candidate-value arrays, and
cross-phase merge. The runtime only performs a generic closest-hit plus grouped
argmin over arrays supplied by the caller.

Metadata now records:

- `runtime_grouped_argmin_used`;
- `prepared_ray_batch_grouped_argmin`;
- `compact_arrays`;
- `native_engine_customization: False`;
- per-phase native closest-hit/grouped-argmin timing.

## Validation

Local Mac:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2594_gpu_rmq_benchmark_front_door_test \
  tests.goal2598_optix_generic_closest_hit_contract_test -v

Ran 20 tests in 0.150s
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

Ran 20 tests in 0.742s
OK
```

All measured payloads below matched the exact CPU oracle.

## Performance

Prepared-reuse public app entry point, 10 repeated query runs on the RTX A5000
pod. The first run may include one-time OptiX/CUDA initialization; the reported
median is robust to that outlier.

| Case | Auto row format | Grouped used | Median query time | ns/query | QPS |
| --- | --- | --- | ---: | ---: | ---: |
| repeated 4K values / 1K queries / block 64 | compact NumPy arrays | no | 0.5700 ms | 570.00 | 1.75M |
| random 16K values / 4K queries / block 256 | native grouped argmin | yes | 1.5085 ms | 377.11 | 2.65M |
| repeated 64K values / 8K queries / block 512 | native grouped argmin | yes | 1.6694 ms | 208.67 | 4.79M |

Comparison to the Goal2603 prepared-query/ray compact medians:

| Case | Goal2603 compact | Goal2604 auto | Delta |
| --- | ---: | ---: | ---: |
| repeated 4K / 1K / block 64 | 0.5454 ms | 0.5700 ms | within noise; auto stays compact |
| random 16K / 4K / block 256 | 1.5852 ms | 1.5085 ms | 1.05x faster |
| repeated 64K / 8K / block 512 | 1.9323 ms | 1.6694 ms | 1.16x faster |

Direct same-process A/B also showed that the grouped primitive is not ideal for
very small batches: the 4K/1K case measured 0.557 ms compact versus 0.571 ms
grouped after warmup. That is why the app keeps a small-batch compact path.

## Interpretation

This is the right architectural direction for GPU-RMQ because it removes
per-ray closest-hit row downloads when the query batch is large enough. It also
keeps the primitive generic: the engine does not know what an RMQ query is.

The remaining runtime overhead is still not purely traversal:

- grouped argmin still uploads the ray-group map and candidate arrays per query;
- native grouped argmin still allocates temporary device buffers per query;
- the app still performs the final cross-phase merge in Python.

The next runtime improvement, if GPU-RMQ remains the active target, should be a
generic prepared grouped-reduction input handle: device-resident group maps,
candidate values, and candidate indices that can be reused across repeated
query batches. That would reduce allocation/upload overhead without introducing
RMQ-specific native code.

## Conclusion

Goal2604 improves the prepared GPU-RMQ RT path while preserving the RTDL design
principle: app-specific semantics stay in Python, and native OptiX receives only
generic prepared scene/ray/group/value/index primitives. The current app auto
path is now:

- compact closest-hit arrays for small batches;
- prepared-ray native grouped argmin for larger batches;
- compact fallback if grouped argmin is unavailable or fails.

This is correctness and engineering evidence for the benchmark implementation,
not a public speedup claim.
