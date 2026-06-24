# Goal3974: Current Scale Partner Toolchain Runbook Sync

Date: 2026-06-08

## Purpose

Goal3971 proved that the current ten-app scale-profile packet passes on an RTX
4000 Ada pod after the direct-loader closeout, but also exposed a setup trap:
driver-550 pods need a driver-compatible Numba CUDA compiler path in addition
to ordinary OptiX setup. Goal3974 updates the RTX cloud runbook so future pod
sessions do not rediscover that failure.

## Update

Updated `docs/audit/runbooks/rtx_cloud_single_session_runbook.md` with a
current v2.x partner-toolchain section:

- Numba is required for the current no-RawKernel partner rows.
- CuPy is required for the RayJoin prepared exact-refiner subpath.
- On driver `550.127.05`, latest Numba can emit PTX `.version 8.7`, while the
  driver-side linker reports support only up to PTX `8.4`.
- The Goal3971 working setup pins `numba==0.60.0`, installs
  `nvidia-cuda-nvcc-cu12==12.4.131`, points `CUDA_HOME` at the pip CUDA compiler
  package for Numba, and keeps RTDL OptiX build variables separate.
- The runbook now includes a small Numba CUDA + CuPy smoke test before a long
  all-app packet.

## Validation

Static validation is covered by
`tests.goal3974_current_scale_partner_toolchain_runbook_sync_test`.

## Boundary

This is a runbook synchronization goal. It does not authorize release,
public-speedup wording, whole-app acceleration wording, broad RT-core wording,
true-zero-copy wording, automatic partner/backend selection, AMD performance
wording, paper reproduction, package-install wording, or app-specific
native-engine logic.
