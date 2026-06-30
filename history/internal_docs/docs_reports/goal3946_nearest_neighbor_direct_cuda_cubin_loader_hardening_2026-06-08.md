# Goal3946: Nearest-Neighbor Direct CUDA CUBIN Loader Hardening

Date: 2026-06-08

## Purpose

Goals3933 and 3942 showed the same compatibility class twice: CUDA driver
module loads that consume freshly generated PTX can fail on current pods with an
unsupported-toolchain error. Goal3946 applies the same CUBIN-loading pattern to
the nearest-neighbor direct CUDA loader cluster adjacent to the RTNN and
Hausdorff benchmark surfaces.

## Scope

This goal changes only five direct CUDA module loaders in
`src/native/optix/rtdl_optix_workloads.cpp`:

- `kPointNearestKernelSrc` / `pns_kernel.cu`
- `kFixedRadiusNeighborsKernelSrc` / `frn_kernel.cu`
- `kPackPoint2DDeviceAabbsKernelSrc` / `partner_point2d_fixed_radius_aabb_pack_kernel.cu`
- `kKnnRowsKernelSrc` / `k_closest_hits_kernel.cu`
- `kKnnRows3DKernelSrc` / `knn3d_kernel.cu`

Each now uses `compile_to_cubin(...)` plus `cuModuleLoadData(..., cubin.data())`
instead of loading PTX text with `ptx.c_str()`.

This is not a global conversion of every remaining OptiX direct CUDA helper.
OptiX pipeline creation still correctly consumes PTX, and broader direct-loader
policy remains future work.

## Pod Smoke

The repair was applied to the clean pod checkout, `librtdl_optix.so` was rebuilt,
and three user-facing OptiX neighbor paths were run:

| Smoke | Status | Stderr bytes | Rows |
| --- | --- | ---: | ---: |
| `fixed_radius_neighbors_optix` | pass | 0 | 4 |
| `knn_rows_optix` | pass | 0 | 6 |
| `point_nearest_segment_optix` | pass | 0 | 2 |

Artifacts:

- `docs/reports/goal3946_nearest_neighbor_direct_cuda_cubin_loader_hardening_2026-06-08/fixed_radius_neighbors_optix.json`
- `docs/reports/goal3946_nearest_neighbor_direct_cuda_cubin_loader_hardening_2026-06-08/knn_rows_optix.json`
- `docs/reports/goal3946_nearest_neighbor_direct_cuda_cubin_loader_hardening_2026-06-08/point_nearest_segment_optix.json`

## Boundary

This is a compatibility hardening step for a narrow direct CUDA loader family.
It does not authorize release, public speedup, whole-app acceleration, broad
RT-core, true-zero-copy, automatic partner/backend selection, AMD performance,
paper reproduction, package-install, or app-specific native-engine logic claims.
