# Goal698 RTX Cloud Validation Runbook

Date: 2026-04-21

Purpose: run RTDL's fixed-radius OptiX app profiler on real RTX-class hardware,
preferably NVIDIA L4, without changing the code under test.

## Recommended Cloud Choice

Use AWS EC2 `g6.xlarge` or `g6.2xlarge` first.

Reason:

- the G6 family uses NVIDIA L4 GPUs with hardware RT cores;
- 1 GPU and roughly 24 GB GPU memory is enough for the current fixed-radius
  profiler;
- AWS Deep Learning / NVIDIA-driver AMIs reduce driver setup time;
- the machine can be terminated immediately after the run.

Fallback: Google Cloud `g2-standard-4` with NVIDIA L4 if AWS G-family quota is
blocked.

## Minimal User Action

The user only needs to provide:

- cloud provider and region;
- SSH access to one running NVIDIA L4/A10/RTX Linux VM;
- confirmation that the VM can be terminated after the report is copied.

Do not ask the user to debug RTDL internals on the cloud machine.

## Required VM State

Before running RTDL:

- `nvidia-smi` must show an RTX-class GPU such as L4/A10/Ada/Ampere/Lovelace;
- `nvcc` must be available;
- NVIDIA OptiX SDK headers must be present, including `optix.h`;
- the RTDL checkout must be on the intended commit.

Important boundary: CUDA/NVIDIA driver images often do not include the OptiX
SDK headers. If `OPTIX_PREFIX/include/optix.h` is missing, install/extract the
OptiX SDK first and set `OPTIX_PREFIX`.

## Validation Command

From the RTDL repo root on the cloud VM:

```bash
chmod +x scripts/goal698_rtx_cloud_validation_commands.sh

OPTIX_PREFIX=$HOME/vendor/optix-dev \
CUDA_PREFIX=/usr \
NVCC=/usr/bin/nvcc \
COPIES=128 \
ITERATIONS=5 \
scripts/goal698_rtx_cloud_validation_commands.sh
```

If CUDA is installed under `/usr/local/cuda`, use:

```bash
OPTIX_PREFIX=$HOME/vendor/optix-dev \
CUDA_PREFIX=/usr/local/cuda \
NVCC=/usr/local/cuda/bin/nvcc \
COPIES=128 \
ITERATIONS=5 \
scripts/goal698_rtx_cloud_validation_commands.sh
```

## Expected Artifacts

The script writes:

- `docs/reports/goal698_rtx_cloud_environment_YYYY-MM-DD.txt`
- `docs/reports/goal698_rtx_cloud_fixed_radius_phase_profile_YYYY-MM-DD.json`

The JSON comes from:

- `/Users/rl2025/rtdl_python_only/scripts/goal697_optix_fixed_radius_phase_profiler.py`

## Required Interpretation

A valid report must state:

- exact cloud instance type and GPU model;
- driver/CUDA/OptiX versions;
- RTDL commit;
- focused test result;
- outlier row path versus fixed-radius summary path timing;
- DBSCAN row path versus core-flag summary path timing;
- whether oracle parity was preserved.

Do not claim general OptiX speedup from this run unless the measured RTX
results justify it. Do not claim KNN/Hausdorff/ANN/Barnes-Hut acceleration from
this fixed-radius test. Do not compare against previous GTX 1070 timings as
RT-core evidence.

## Stop Condition

After artifacts are copied back, stop or terminate the cloud VM. Keeping the VM
running after validation is unnecessary cost.
