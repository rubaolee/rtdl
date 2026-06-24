# Goal2612 GPU-RMQ Grouped Candidate Argmin Decision

Date: 2026-05-25

## Scope

The user asked for one final GPU-RMQ round before deciding whether this app can
be promoted to a benchmark app. Author code is explicitly excluded for this
round. The added runtime feature is a generic, device-resident grouped candidate
argmin/finalize primitive:

- inputs: `group_id`, `candidate_value`, and `tie_index`;
- output: one minimum value and tie index per group;
- native contract: no RMQ, GPU-RMQ, sparse table, interval, or paper-specific
  vocabulary in the OptiX engine.

The GPU-RMQ app uses this only as a generic finalization primitive after its
Python/partner scheduling has produced candidate arrays.

## Pod Evidence

- SSH command supplied by user: `ssh root@213.192.2.118 -p 40017 -i ~/.ssh/id_ed25519`
- Actual working key on this Mac: `~/.ssh/id_ed25519_rtdl_codex`
- Hostname: `12eeb8f708d3`
- GPU: NVIDIA GeForce RTX 3090
- Driver: 580.126.20
- CUDA: `/usr/local/cuda`
- OptiX SDK installed for this run:
  `/opt/optix-8.1/NVIDIA-OptiX-SDK-8.1.0-linux64-x86_64`
- Artifact:
  `docs/reports/goal2612_gpu_rmq_grouped_candidate_argmin_vs_cuda_2026-05-25.json`

Validation:

```bash
make build-optix OPTIX_PREFIX=/opt/optix-8.1/NVIDIA-OptiX-SDK-8.1.0-linux64-x86_64 CUDA_PREFIX=/usr/local/cuda NVCC=/usr/local/cuda/bin/nvcc
PYTHONPATH=src:. python3 -m py_compile src/rtdsl/__init__.py src/rtdsl/optix_runtime.py examples/v2_0/research_benchmarks/gpu_rmq/rtdl_gpu_rmq_benchmark_app.py scripts/goal2609_gpu_rmq_non_author_baselines.py
PYTHONPATH=src:. python3 -m unittest tests.goal2594_gpu_rmq_benchmark_front_door_test tests.goal2595_gpu_rmq_author_runner_test tests.goal2598_optix_generic_closest_hit_contract_test
```

Result: 28 focused tests passed on the pod.

Comparison command:

```bash
PYTHONPATH=src:. python3 scripts/goal2609_gpu_rmq_non_author_baselines.py \
  --out docs/reports/goal2612_gpu_rmq_grouped_candidate_argmin_vs_cuda_2026-05-25.json \
  --repeats 12 \
  --threads "$(nproc)" \
  --reduction-factor 32 \
  --scan-threshold 64 \
  --rt-top-block-size 1
```

## Results

All workloads matched the CPU reference. The new finalize primitive was active:
`partner_candidate_finalize.backend=optix`,
`native_device_grouped_candidate_argmin=true`.

| Dataset | Values | Queries | CUDA sparse query median | Previous RTDL prepared RT median | Paper-hybrid RTDL+partner median | Previous RTDL vs CUDA | Hybrid vs CUDA |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| repeated | 4,096 | 1,000 | 0.0133 ms | 0.3128 ms | 0.8123 ms | 23.5x slower | 61.0x slower |
| random | 16,384 | 4,000 | 0.0358 ms | 0.4937 ms | 2.2927 ms | 13.8x slower | 64.0x slower |
| repeated | 65,536 | 8,000 | 0.0727 ms | 1.0266 ms | 4.7388 ms | 14.1x slower | 65.2x slower |

The generic candidate finalize kernel itself is not the bottleneck: measured
native finalize time is roughly 0.017-0.019 ms in these runs. The losing cost is
the total RTDL/Python/partner execution shape around it: query scheduling,
candidate construction, RT traversal/reduction overhead, and per-group result
materialization. A direct CUDA sparse-query kernel has the right data structure
and avoids the RT geometry/traversal machinery entirely.

## Decision

GPU-RMQ should not be promoted to a benchmark app in the current RTDL line. It
should remain a research/learner app that documents useful design pressure:

- generic closest-hit and grouped-argmin RT contracts;
- prepared reusable scenes and prepared candidate inputs;
- the need for true device-resident partner/runtime continuation;
- the boundary that native engines must not learn RMQ-specific formulas.

The app is useful for RTDL design, but not as a performance benchmark. Keeping
it as a benchmark would weaken the benchmark suite because the strongest
available same-workload CUDA baseline is already one to two orders of magnitude
faster on query time.

## Follow-Up Boundary

The only plausible future reconsideration is not another app-specific
optimization. It would require a generic device-resident partner/runtime
pipeline where partner-generated candidate arrays, RTDL traversal, grouped
candidate merge/finalize, and downstream consumers stay on device without
host-round trips. Until that exists and beats a direct CUDA sparse-query
baseline, GPU-RMQ remains demoted.
