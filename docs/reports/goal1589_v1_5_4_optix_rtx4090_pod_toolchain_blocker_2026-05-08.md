# Goal 1589: RTX 4090 Pod Toolchain Blocker

## Verdict

The pod at `root@103.196.86.121 -p 16167` is reachable and has an `NVIDIA GeForce RTX 4090`, but it did not produce accepted RTDL OptiX evidence. All runtime attempts failed before timing with:

```text
CUDA driver error: the provided PTX was compiled with an unsupported toolchain.
```

This is an environment/toolchain blocker, not an RTDL parity failure and not negative performance evidence.

## Environment

- Host: `1c20d70b1297`
- OS: Ubuntu 24.04.4, Linux `6.8.0-59-generic`
- GPU: `NVIDIA GeForce RTX 4090`
- Driver: `550.127.05`
- `nvidia-smi` CUDA banner: `12.4`
- Repo checkout: `/root/rtdl_goal1589_pod`
- Commit used for the final smoke: `73abc49d672b0a47e4bac23aae6fb25f8b78d29b`
- OptiX SDK: `/root/vendor/optix-sdk`, tag `v8.0.0`

## What Worked

- SSH succeeded with `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`.
- The repo cloned and synced to `main`.
- OptiX SDK `v8.0.0` cloned successfully.
- CUDA 13 host build could compile `build/librtdl_optix.so` after exposing `nvrtc.h/libnvrtc`.
- CUDA 12.8 apt packages installed successfully.
- CUDA 12.1 and 12.4 NVRTC/runtime Python wheels installed successfully.
- Focused static tests ran successfully after adding `tests/__init__.py`.

## Fixes Landed

Two repo hardening fixes were made while investigating this pod:

- `tests/__init__.py` was added so `python -m unittest tests.goal...` resolves to the repo tests even on images with an installed third-party `tests` package.
- `RTDL_OPTIX_PTX_ARCH` was added as an opt-in PTX architecture override for NVRTC/NVCC PTX generation, for example `RTDL_OPTIX_PTX_ARCH=compute_89`.

## Attempts

The following combinations all reached the same runtime blocker:

- CUDA 13 toolkit with CUDA 13 NVRTC.
- CUDA 12.4 NVRTC/runtime Python wheels with CUDA 12 include shim.
- CUDA 12.8 apt toolkit packages with `/usr/local/cuda-12.8`.
- CUDA 12.1 NVRTC/runtime Python wheels with CUDA 12 include shim.
- `RTDL_OPTIX_PTX_ARCH=compute_89`.
- `RTDL_OPTIX_PTX_ARCH=compute_80`.

The smallest smoke command used `candidate_count=7`, so the failure occurs before any meaningful collect-k performance measurement:

```bash
RTDL_OPTIX_PTX_ARCH=compute_80 \
LD_LIBRARY_PATH=/root/vendor/cuda121-shim/lib64:/usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvrtc/lib:/usr/lib/x86_64-linux-gnu \
PYTHONPATH=src:. \
python3 scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py \
  --library build/librtdl_optix.so \
  --counts 7 \
  --repeats 1 \
  --profile-jsonl /tmp/goal1589_cuda121_smoke.jsonl \
  --json-out /tmp/goal1589_cuda121_smoke.json \
  --md-out /tmp/goal1589_cuda121_smoke.md
```

## Interpretation

This pod is Ada, not the needed non-Ada architecture. It could still have been useful as a second Ada validation target, but the CUDA driver/PTX toolchain mismatch prevents accepted OptiX runtime evidence.

Do not use this pod's failed runtime as performance evidence. The correct next step is to use a pod whose driver/toolkit combination can load RTDL's generated PTX, preferably a non-Ada NVIDIA architecture.

## Claim Boundary

This report does not authorize public speedup wording, true zero-copy wording, stable primitive promotion, whole-application claims, or release action.
