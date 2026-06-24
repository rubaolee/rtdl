# Goal3975: Current Scale Partner Pod Setup Helper

Date: 2026-06-08

## Purpose

Goal3975 turns the Goal3971/3974 driver-550 partner setup lesson into a reusable
pod helper script:

`scripts/goal3975_current_scale_partner_pod_setup.sh`

The helper prepares an already-running Linux RTX pod for the current ten-app
scale-profile packet. It does not create cloud resources and does not authorize
release or performance claims.

## Behavior

The helper:

- installs/pins `numba==0.60.0`, `numpy==2.0.2`,
  `nvidia-cuda-nvcc-cu12==12.4.131`, and `cupy-cuda12x==14.1.1`;
- locates the pip CUDA compiler package root containing `nvidia/cuda_nvcc`;
- points `CUDA_HOME` at that package so Numba emits driver-550-compatible PTX;
- keeps `RTDL_CUDA_PREFIX` separate for the RTDL OptiX build;
- smoke-tests a tiny Numba CUDA kernel and a tiny CuPy reduction;
- prints the environment exports needed before running
  `scripts/goal3828_current_benchmark_scale_profile_runner.py`.

## Validation

Static validation is covered by
`tests.goal3975_current_scale_partner_pod_setup_helper_test`.

The helper was also copied to the Goal3971 RTX 4000 Ada pod and validated with:

```bash
bash -n /root/goal3975_current_scale_partner_pod_setup.sh
cd /root/goal3971_current_head_scale.71XR3W/repo
bash /root/goal3975_current_scale_partner_pod_setup.sh --skip-install
```

The pod smoke printed `partner_smoke_ok`. A follow-up `--skip-install
--no-smoke` run printed clean copy-paste exports containing literal `$PATH`,
`${LD_LIBRARY_PATH:-}`, and `$PWD` references rather than over-escaped paths.

## Boundary

This is a pod setup helper. It does not authorize release, public-speedup
wording, whole-app acceleration wording, broad RT-core wording, true-zero-copy
wording, automatic partner/backend selection, AMD performance wording, paper
reproduction, package-install wording, or app-specific native-engine logic.
