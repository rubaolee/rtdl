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

## Recommended Migration Order

1. Convert collect-k helpers last, because that older path has more historical
   tuning branches and should be tested as a cluster.

## Follow-Up

Goal3952 migrated the device-column grouped reduction and segment-pair count
helpers out of this debt list. The current remaining driver-loaded PTX count is
`16`.

Goal3954 migrated the partner triangle/ray device-column pack helpers out of
this debt list. The current remaining driver-loaded PTX count is `12`.

Goal3958 migrated the point-group-nearest split/reduce helpers out of this debt
list. The current remaining driver-loaded PTX count is `9`.

## Boundary

This goal records compatibility debt. It does not authorize release,
public-speedup wording, whole-app acceleration wording, broad RT-core wording,
true-zero-copy wording, automatic partner/backend selection, AMD performance
wording, paper reproduction, package-install wording, or app-specific
native-engine logic.
