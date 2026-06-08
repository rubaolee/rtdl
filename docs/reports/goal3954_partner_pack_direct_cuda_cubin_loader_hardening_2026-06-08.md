# Goal3954: Partner Pack Direct CUDA CUBIN Loader Hardening

Date: 2026-06-08

## Purpose

Goal3954 migrates the reusable partner triangle/ray device-column pack helpers
from driver-loaded PTX to CUBIN. These helpers sit at the RTDL+partner boundary
and are reusable bridge infrastructure rather than app-specific native logic.

## Scope

This goal changes four direct CUDA module loaders in
`src/native/optix/rtdl_optix_workloads.cpp`:

- `kPackTriangle3DDeviceColumnsKernelSrc` / `partner_triangle3d_device_columns_pack_kernel.cu`
- `kPackRay3DDeviceColumnsKernelSrc` / `partner_ray3d_device_columns_pack_kernel.cu`
- `kPackTriangle2DDeviceColumnsKernelSrc` / `partner_triangle2d_device_columns_pack_kernel.cu`
- `kPackRay2DDeviceColumnsKernelSrc` / `partner_ray2d_device_columns_pack_kernel.cu`

Each now uses `compile_to_cubin(...)` plus `cuModuleLoadData(..., cubin.data())`.

The change does not touch OptiX pipeline PTX creation.

## Validation

Static validation is covered by
`tests.goal3954_partner_pack_direct_cuda_cubin_loader_hardening_test`.
The updated Goal3951 inventory confirms these four kernels are no longer in the
remaining driver-loaded PTX debt list.

Pod smoke validation was also run on the RTX 4000 Ada pod from clean commit
`9c13d1c6` plus only the Goal3954 native patch:

- artifact: `docs/reports/goal3954_partner_pack_direct_cuda_cubin_loader_hardening_2026-06-08/goal3954_partner_pack_smoke.json`
- rows: `spatial_rayjoin`, `robot_collision`, `contact_manifold`,
  `triangle_counting`
- result: 4 / 4 pass
- claim boundary: release, public speedup, whole-app acceleration, broad
  RT-core, paper reproduction, true-zero-copy, automatic partner selection, AMD
  performance, and app-specific native-engine claims all remain unauthorized.

A clean all-app current-scale packet should be rerun after this commit is
pushed.

## Boundary

This is internal compatibility hardening. It does not authorize release,
public-speedup wording, whole-app acceleration wording, broad RT-core wording,
true-zero-copy wording, automatic partner/backend selection, AMD performance
wording, paper reproduction, package-install wording, or app-specific
native-engine logic.
