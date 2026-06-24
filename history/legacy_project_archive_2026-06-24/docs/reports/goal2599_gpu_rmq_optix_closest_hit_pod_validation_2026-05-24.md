# Goal2599: GPU-RMQ Generic OptiX Closest-Hit Pod Validation

Status: passed for correctness readiness.

This report records pod validation for the app-agnostic RTDL OptiX 3-D
`ray_triangle_closest_hit` primitive and the GPU-RMQ paper-style RT lowering
that uses it. The pod was used only for RTDL validation. The GPU-RMQ authors'
code was not run on this pod.

## Environment

- Pod SSH command requested by user:
  `ssh root@203.57.40.101 -p 10082 -i ~/.ssh/id_ed25519`
- Working key used from this Mac:
  `~/.ssh/id_ed25519_rtdl_codex`
- Remote working directory:
  `/workspace/rtdl_goal2598`
- Source commit cloned on pod:
  `dc6b91d29a37ad335e2ebe0cf553cd01606530fc`
- GPU:
  `NVIDIA RTX A5000, driver 565.57.01, 24564 MiB`
- CUDA:
  `/usr/local/cuda`, nvcc `12.8.93`
- OptiX SDK:
  local `NVIDIA-OptiX-SDK-8.1.0-linux64-x86_64-35015278.sh` extracted to
  `/workspace/optix-8.1`
- Native library built:
  `/workspace/rtdl_goal2598/build/librtdl_optix.so`

The pod repo had a local Goal2598/Goal2599 delta applied over the cloned commit;
the source identity above is therefore the clone base plus the local files under
review.

## Build Command

```bash
cd /workspace/rtdl_goal2598
export PATH=/usr/local/cuda/bin:$PATH
make build-optix OPTIX_PREFIX=/workspace/optix-8.1 CUDA_PREFIX=/usr/local/cuda
```

Result: `build/librtdl_optix.so` built successfully.

## Issues Found And Fixed

- Runtime cache bug: backend prepared-execution caches used `id(payload)` for
  tuple identity tokens without retaining the tuple. Python can reuse freed
  tuple ids, causing a later OptiX call to reuse a stale prepared execution.
  This was exposed by GPU-RMQ's separate left/right/full phase calls.
- Fix: `_PayloadIdentityCacheToken` now keeps the tuple alive and compares by
  object identity, preventing stale cache hits while preserving identity-cache
  behavior for live payloads.
- App-side f32 boundary issue: the GPU-RMQ interval-edge epsilon was too small
  after the OptiX path packed RT coordinates as f32, so edge triangles just
  outside a query interval could be accepted.
- Fix: the GPU-RMQ app-side encoding now uses a larger interval-boundary epsilon
  and a stronger x-coordinate tie-break offset that preserves value ordering.
  This is app-side geometry encoding, not native engine customization.

## Validation Commands And Results

Primitive-only and default GPU-RMQ validation:

```bash
cd /workspace/rtdl_goal2598
export RTDL_OPTIX_LIBRARY=/workspace/rtdl_goal2598/build/librtdl_optix.so
PYTHONPATH=src:. python3 scripts/goal2598_optix_closest_hit_validation.py --backend optix
```

Result:

- `closest_hit.matches_cpu_reference`: `true`
- `gpu_rmq.matches_cpu_reference`: `true`
- `overall_matches_cpu_reference`: `true`
- Default GPU-RMQ fixture:
  `dataset=repeated`, `value_count=4096`, `query_count=1024`,
  `block_size=64`
- Default timing, diagnostic only:
  CPU reference `0.0049s`, OptiX paper RT lowering `0.0602s`

Targeted unit tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2594_gpu_rmq_benchmark_front_door_test \
  tests.goal2595_gpu_rmq_author_runner_test \
  tests.goal2598_optix_generic_closest_hit_contract_test -v
```

Result: `Ran 19 tests ... OK`.

Larger repeated fixture:

```bash
PYTHONPATH=src:. python3 scripts/goal2598_optix_closest_hit_validation.py \
  --backend optix --dataset repeated --value-count 65536 --query-count 8192 \
  --max-width 4096 --block-size 128
```

Result:

- `gpu_rmq.matches_cpu_reference`: `true`
- `overall_matches_cpu_reference`: `true`
- Diagnostic timing:
  CPU reference `0.5565s`, OptiX paper RT lowering `0.7890s`

Random fixture:

```bash
PYTHONPATH=src:. python3 scripts/goal2598_optix_closest_hit_validation.py \
  --backend optix --dataset random --value-count 16384 --query-count 4096 \
  --max-width 2048 --block-size 128
```

Result:

- `gpu_rmq.matches_cpu_reference`: `true`
- `overall_matches_cpu_reference`: `true`
- Diagnostic timing:
  CPU reference `0.1430s`, OptiX paper RT lowering `0.2381s`

## Claim Boundary

- Correctness readiness for the generic OptiX 3-D
  `ray_triangle_closest_hit` primitive is now validated on NVIDIA hardware.
- GPU-RMQ's paper-style RT lowering can call the generic primitive through
  RTDL's OptiX backend and match the CPU RMQ reference on the tested fixtures.
- The native engine remains app-agnostic: RMQ geometry construction, interval
  scheduling, tie-breaking policy, and primitive-id decoding stay in Python app
  code.
- This evidence does not authorize public speedup wording. The timings above
  are diagnostic and include Python scheduling, repeated GAS construction, and
  host/device transfer overhead.
