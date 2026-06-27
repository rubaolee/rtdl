# Goal1271 Pod Environment Diversity Hardening

Date: 2026-05-05

## Summary

RTDL v1.2 pod work must tolerate different Linux images, CUDA layouts, OptiX
header locations, and Embree package versions. Goal1268 already made Embree 3
and Embree 4 acceptable at runtime. Goal1271 adds a reusable pod environment
probe so NVIDIA pod executors do not assume one Ubuntu/CUDA layout.

This is internal execution hardening. It does not authorize public speedup
wording.

## Changes

- Added `scripts/rtdl_pod_env_probe.sh`.
- The probe records OS/package-manager shape, CUDA prefix, `nvcc`, OptiX
  prefix, CUDA library directory, `nvidia-smi`, and version tails.
- The probe can install common build dependencies through `apt-get`, `dnf`,
  `yum`, or `apk` when available, but it also accepts preconfigured images.
- `scripts/goal1267_v1_2_optix_targeted_pod_executor.sh` now sources the probe
  output instead of hard-coding `/usr/local/cuda`, `/root/vendor/optix-dev`, or
  a single CUDA package set.
- `Makefile` now detects common versioned CUDA prefixes such as
  `/usr/local/cuda-12.8` when `CUDA_PREFIX` is not provided.

## Boundary

The probe is not a benchmark. It exists to make pod artifacts easier to compare
and debug across OS/CUDA/driver diversity. Missing CUDA/OptiX/Embree pieces
should be reported as environment blockers with probe artifacts, not as vague
benchmark failures.
