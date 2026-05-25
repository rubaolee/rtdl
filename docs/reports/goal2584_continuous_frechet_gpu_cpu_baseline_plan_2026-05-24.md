# Goal2584 Continuous Frechet GPU/CPU Baseline Plan

Date: 2026-05-24
Status: implemented; pod evidence collected

## Purpose

Compare the attempted Continuous Frechet benchmark candidate against
same-contract CPU and GPU baselines before deciding whether it deserves active
benchmark status.

## Baselines

| Baseline | Source | Contract |
| --- | --- | --- |
| CPU C++ all-cells | learner-owned C++ helper embedded in `rtdl_continuous_frechet_distance_app.py` | exact continuous Frechet binary-search estimate over all free-space cells |
| GPU CFT | locally written Torch CUDA wavefront baseline in `scripts/goal2584_continuous_frechet_gpu_cpu_baselines.py` | same all-cells continuous Frechet decision/search contract |
| RTDL OptiX | existing RTDL segment/expanded-shape broadphase plus learner-owned C++ continuation | RT-core broadphase plus exact continuation, guarded by pruning fallback |

No usable external same-contract GPU continuous Frechet implementation is
assumed. Discrete Frechet GPU repositories are not same-contract substitutes for
this candidate.

These baselines are internal evidence only and do not authorize public speedup
wording.

## Correctness Rule

For each fixture size, the GPU baseline and RTDL OptiX path must match the CPU
C++ all-cells distance estimate within `1e-5` relative/absolute tolerance.

## Pod Environment

Provided SSH command:

```text
ssh root@69.30.85.177 -p 22184 -i ~/.ssh/id_ed25519
```

Actual working key on this Mac:

```text
~/.ssh/id_ed25519_rtdl_codex
```

Observed pod:

- GPU: NVIDIA RTX A5000
- Driver: 570.211.01
- Torch: `2.8.0+cu128`
- CUDA toolkit: `/usr/local/cuda-12.8`
- OptiX SDK installed from local `NVIDIA-OptiX-SDK-8.1.0-linux64-x86_64-35015278.sh`
- `make build-optix OPTIX_PREFIX=/root/vendor/NVIDIA-OptiX-SDK-8.1.0-linux64-x86_64 CUDA_PREFIX=/usr/local/cuda-12.8 NVCC=/usr/local/cuda-12.8/bin/nvcc` succeeded
