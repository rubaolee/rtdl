# Goal2603 GPU-RMQ Phase-Batched Prepared-Query/Ray Compact Path

Date: 2026-05-24

## Purpose

Goal2602 added a generic grouped-argmin runtime boundary for prepared OptiX
closest-hit results. That boundary is architecturally useful and remains
available, but the CUDA-side grouped reducer was not the fastest path for the
current GPU-RMQ benchmark. This follow-up keeps the engine app-agnostic and
optimizes the app/runtime boundary actually used by the benchmark:

- one prepared element-triangle scene launch for `same_block`, `left_partial`,
  and `right_partial` element phases;
- one prepared block-triangle scene launch for `full_blocks`;
- compact NumPy row-array transfer instead of Python dict row materialization;
- app-side phase slicing and final cross-phase RMQ selection;
- reusable app-side query batches so fixed benchmark query columns are packed
  once instead of rebuilt for every repeated prepared query run;
- reusable generic device-resident 3-D ray batches so repeated closest-hit
  launches do not upload the same rays every run.

No GPU-RMQ-specific formula, query range logic, or app vocabulary was added to
the native engine.

## Implementation

`PreparedPaperRtRmq.query_arrays` now batches all element phases into a single
generic closest-hit row-array call. The first attempt reduced all batched
element rows in one NumPy assignment, but that was incorrect because cross-block
queries produce both left- and right-partial candidates with the same query id.
NumPy advanced assignment is not a reduction for duplicate indices.

The accepted implementation keeps the single element-scene OptiX launch, then
slices the returned compact row arrays back into phase-local ranges. Each
phase-local accept step has unique query ids, so it preserves leftmost-minimum
tie semantics without a global sort.

Metadata now distinguishes each element phase's own ray count from the combined
batched launch ray count:

- `ray_count`: rays in the logical phase;
- `batched_combined_ray_count`: total rays in the combined element launch.

The app also exposes `PreparedPaperRtRmq.prepare_query_batch`. The benchmark
payload prepares that fixed query batch once, then calls
`query_prepared_batch_arrays` for each repeated query run. This is a language
and runtime boundary improvement: it separates static geometry preparation,
fixed query/ray packing, and repeated RT execution without adding app semantics
to native OptiX.

The runtime now also exposes `PreparedOptixRayBatch3D` through
`PreparedOptixStaticTriangleScene3D.prepare_ray_batch`. GPU-RMQ query batches use
that generic boundary when available. The native engine stores only 3-D rays; it
does not know RMQ phases, query ranges, block ids, or values.

## Pod Evidence

Pod:

- SSH: `root@203.57.40.101 -p 10082`
- Key used from Mac: `~/.ssh/id_ed25519_rtdl_codex`
- Remote repo: `/workspace/rtdl_goal2598`
- Backend library: `/workspace/rtdl_goal2598/build/librtdl_optix.so`
- GPU: NVIDIA RTX A5000
- OptiX SDK: `/workspace/optix-8.1`
- CUDA prefix: `/usr/local/cuda`

Build:

```text
make build-optix OPTIX_PREFIX=/workspace/optix-8.1 CUDA_PREFIX=/usr/local/cuda
```

Validation after syncing the final phase-batched prepared-query app:

```text
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/workspace/rtdl_goal2598/build/librtdl_optix.so \
  python3 -m unittest \
  tests.goal2594_gpu_rmq_benchmark_front_door_test \
  tests.goal2598_optix_generic_closest_hit_contract_test -v

Ran 20 tests in 0.750s
OK
```

Local validation on the Mac:

```text
PYTHONPATH=src:. python3 -m py_compile \
  examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py

PYTHONPATH=src:. python3 -m unittest \
  tests.goal2594_gpu_rmq_benchmark_front_door_test \
  tests.goal2598_optix_generic_closest_hit_contract_test -v

Ran 20 tests in 0.182s
OK (skipped=1)
```

## Performance

All accepted rows matched the exact CPU oracle. Times below are prepared-query
times on the RTX A5000 pod. The first run may include one-time warmup.

| Case | Prior prepared compact | Goal2602 grouped argmin | Phase-batched compact | Prepared-query/ray compact | Delta vs prior compact |
| --- | ---: | ---: | ---: | ---: | ---: |
| repeated 4K values / 1K queries / block 64 | 1.63 ms | 1.55 ms | 1.07 ms | 0.55 ms | 3.0x faster |
| random 16K values / 4K queries / block 256 | 2.76 ms | 2.83 ms | 2.30 ms | 1.59 ms | 1.7x faster |
| repeated 64K values / 8K queries / block 512 | 6.87 ms | 5.49 ms | 4.74 ms | 1.93 ms | 3.6x faster |

Raw accepted runs:

| Case | Query runs, ms | Median, ms | Warmup-excluded median, ms |
| --- | --- | ---: | ---: |
| repeated 4K / 1K / block 64 | 0.5484, 0.5644, 0.5460, 0.5439, 0.5680, 0.5917, 0.5448, 0.5430 | 0.5466 | 0.5454 |
| random 16K / 4K / block 256 | 1.5995, 1.5872, 1.5884, 1.5855, 1.5901, 1.5846, 1.5840, 1.5849 | 1.5864 | 1.5852 |
| repeated 64K / 8K / block 512 | 1.9459, 1.9367, 1.9366, 1.9339, 1.9323, 1.9319, 1.9211, 1.9322 | 1.9331 | 1.9323 |

The query-batch preparation costs were small relative to scene preparation and
are paid once per fixed query set:

| Case | Query-batch prepare |
| --- | ---: |
| repeated 4K / 1K / block 64 | 0.9317 ms |
| random 16K / 4K / block 256 | 1.6244 ms |
| repeated 64K / 8K / block 512 | 3.0516 ms |

Same-process A/B against the host-packed prepared query batch shows the
device-resident ray batch is beneficial on the tested cases:

| Case | Host-packed rays | Device-resident rays |
| --- | ---: | ---: |
| repeated 4K / 1K / block 64 | 0.5936 ms | 0.5454 ms |
| random 16K / 4K / block 256 | 1.7068 ms | 1.5852 ms |
| repeated 64K / 8K / block 512 | 2.1378 ms | 1.9323 ms |

Rejected intermediate result:

- A naive two-launch implementation with one global sorted accept was correct
  but too slow on larger cases: 1.39 ms, 3.15 ms, and 15.19 ms
  warmup-excluded medians for the three cases above.
- The final phase-sliced implementation keeps correctness and avoids that sort
  penalty.

## Block-Size Sweep

Block size materially affects the RT workload shape. The pod became noisy during
long sweeps, especially after repeated CPU-oracle work, so this table is
diagnostic rather than claim-grade tuning. Every listed run matched the CPU
oracle.

| Dataset | Values | Queries | Block size | Warmup-excluded median |
| --- | ---: | ---: | ---: | ---: |
| repeated | 4,096 | 1,000 | 32 | 0.6420 ms |
| repeated | 4,096 | 1,000 | 64 | 0.6050 ms |
| repeated | 4,096 | 1,000 | 128 | 0.6236 ms |
| repeated | 4,096 | 1,000 | 256 | 0.7621 ms |
| repeated | 4,096 | 1,000 | 512 | 0.8899 ms |
| random | 16,384 | 4,000 | 64 | 1.0316 ms in one sweep; 1.48 ms in a later query-only rerun |
| random | 16,384 | 4,000 | 128 | 1.3331 ms in one sweep; later pod-noisy reruns were slower |
| random | 16,384 | 4,000 | 256 | 1.4140 ms in one sweep; 1.15 ms in the stable query-only matrix |
| repeated | 65,536 | 8,000 | 64 | 3.2131 ms |
| repeated | 65,536 | 8,000 | 128 | 3.2847 ms |
| repeated | 65,536 | 8,000 | 256 | 6.1584 ms |
| repeated | 65,536 | 8,000 | 512 | 2.4496 ms |
| repeated | 65,536 | 8,000 | 1024 | 5.1875 ms |

The best block size is workload-dependent. The app default remains conservative;
benchmark runs should report the block size explicitly.

## Conclusion

The best current GPU-RMQ RTDL path is not the new device grouped-argmin reducer;
it is the phase-batched prepared-query compact closest-hit path:

- it is correct against the exact CPU oracle;
- it reduces OptiX launches from four logical phases to two native launches;
- it prepares fixed query/ray batches once and reuses packed rays across
  repeated prepared query runs;
- it keeps prepared rays resident on the device, eliminating repeated ray
  uploads for fixed query batches;
- it keeps native OptiX app-independent;
- it is faster than both the prior prepared compact path and the grouped-argmin
  path on the measured cases.

The remaining bottleneck is now mostly host row-array slicing, final reduction,
and host/device row transfer. Native traversal itself is much smaller than total
query time on mid-size workloads. Future runtime work should target a generic
device-side compact reduction that avoids downloading per-ray closest-hit rows.
