# Goal3951: Direct CUDA PTX Loader Debt Inventory

Date: 2026-06-08

## Purpose

Goals3933, 3942, and 3946 repaired driver-loaded CUDA module paths that were
better served by CUBIN loading on current RTX pods. Goal3951 records the
remaining direct `cuModuleLoadData(..., ptx.c_str())` sites so future hardening
can proceed from a checklist instead of rediscovering failures row by row.

This is an inventory only. It does not convert the remaining sites.

## Current Remaining Driver-Loaded PTX Sites

| File | Line | Module | Kernel file |
| --- | ---: | --- | --- |
| `src/native/optix/rtdl_optix_api.cpp` | 90 | `g_collect_k_cooperative_launch_smoke.module` | `collect_k_cooperative_launch_smoke_kernel.cu` |
| `src/native/optix/rtdl_optix_api.cpp` | 3500 | `g_collect_k_i64_row_width2_sort.module` | `collect_k_bounded_i64_row_width2_sort_kernel.cu` |
| `src/native/optix/rtdl_optix_api.cpp` | 3589 | `g_collect_k_i64_row_width2_sort.module` | `collect_k_bounded_i64_row_width2_sort_kernel.cu` |
| `src/native/optix/rtdl_optix_api.cpp` | 3600 | `g_collect_k_i64_row_width2_cub_sort.module` | `collect_k_bounded_i64_row_width2_cub_sort_kernel.cu` |
| `src/native/optix/rtdl_optix_api.cpp` | 3615 | `g_collect_k_i64_row_width2_merge_two.module` | `collect_k_bounded_i64_row_width2_merge_two_kernel.cu` |
| `src/native/optix/rtdl_optix_api.cpp` | 3625 | `g_collect_k_i64_row_width2_merge_level.module` | `collect_k_bounded_i64_row_width2_merge_level_kernel.cu` |
| `src/native/optix/rtdl_optix_api.cpp` | 3635 | `g_collect_k_i64_row_width2_final_materialize.module` | `collect_k_bounded_i64_row_width2_final_compact_kernel.cu` |
| `src/native/optix/rtdl_optix_api.cpp` | 4822 | `g_collect_k_i64.module` | `collect_k_bounded_i64_kernel.cu` |
| `src/native/optix/rtdl_optix_api.cpp` | 6664 | `g_collect_k_i64_row_width2_final_materialize.module` | `collect_k_bounded_i64_row_width2_final_compact_kernel.cu` |
| `src/native/optix/rtdl_optix_workloads.cpp` | 1334 | `g_device_column_grouped_i64.module` | `device_column_grouped_i64_kernel.cu` |
| `src/native/optix/rtdl_optix_workloads.cpp` | 4702 | `g_segment_pair_ambiguity_count.module` | `segment_pair_ambiguity_count_kernel.cu` |
| `src/native/optix/rtdl_optix_workloads.cpp` | 4858 | `g_segment_pair_device_refined_count.module` | `segment_pair_device_refined_count_kernel.cu` |
| `src/native/optix/rtdl_optix_workloads.cpp` | 12873 | `g_partner_triangle3d_pack.module` | `partner_triangle3d_device_columns_pack_kernel.cu` |
| `src/native/optix/rtdl_optix_workloads.cpp` | 12888 | `g_partner_ray3d_pack.module` | `partner_ray3d_device_columns_pack_kernel.cu` |
| `src/native/optix/rtdl_optix_workloads.cpp` | 14540 | `g_partner_triangle2d_pack.module` | `partner_triangle2d_device_columns_pack_kernel.cu` |
| `src/native/optix/rtdl_optix_workloads.cpp` | 14783 | `g_partner_ray2d_pack.module` | `partner_ray2d_device_columns_pack_kernel.cu` |
| `src/native/optix/rtdl_optix_workloads.cpp` | 20347 | `g_point_group_nearest_split_columns.module` | `point_group_nearest_split_columns_kernel.cu` |
| `src/native/optix/rtdl_optix_workloads.cpp` | 20446 | `g_point_group_nearest_reduce.module` | `point_group_nearest_max_reduce_kernel.cu` |
| `src/native/optix/rtdl_optix_workloads.cpp` | 20567 | `g_point_group_nearest_reduce.module` | `point_group_nearest_max_reduce_kernel.cu` |

## Recommended Migration Order

1. Convert the device-column grouped reduction and segment-pair count helpers,
   because they are close to the current RayDB/RayJoin performance-critical
   surfaces.
2. Convert partner triangle/ray pack helpers, because they are reusable
   bridge-building blocks for RTDL+partner workflows.
3. Convert point-group-nearest split/reduce helpers, because they sit near the
   Hausdorff and nearest-neighbor family.
4. Convert collect-k helpers last, because that older path has more historical
   tuning branches and should be tested as a cluster.

## Boundary

This goal records compatibility debt. It does not authorize release,
public-speedup wording, whole-app acceleration wording, broad RT-core wording,
true-zero-copy wording, automatic partner/backend selection, AMD performance
wording, paper reproduction, package-install wording, or app-specific
native-engine logic.
