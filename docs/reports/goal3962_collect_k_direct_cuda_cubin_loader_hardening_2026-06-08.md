# Goal3962: Collect-K Direct CUDA CUBIN Loader Hardening

Date: 2026-06-08

## Purpose

Goal3962 migrates the remaining collect-k direct CUDA module loaders from
driver-loaded PTX to CUBIN. This closes the direct
`cuModuleLoadData(..., ptx.c_str())` debt tracked by Goal3951 while preserving
OptiX pipeline PTX paths elsewhere.

## Scope

This goal changes the collect-k CUDA helper module loaders in
`src/native/optix/rtdl_optix_api.cpp`:

- `collect_k_cooperative_launch_smoke_kernel.cu`
- `collect_k_bounded_i64_row_width2_sort_kernel.cu`
- `collect_k_bounded_i64_row_width2_cub_sort_kernel.cu`
- `collect_k_bounded_i64_row_width2_merge_two_kernel.cu`
- `collect_k_bounded_i64_row_width2_merge_level_kernel.cu`
- `collect_k_bounded_i64_row_width2_final_compact_kernel.cu`
- `collect_k_bounded_i64_kernel.cu`

Each direct CUDA module load now uses `compile_to_cubin(...)` plus
`cuModuleLoadData(..., cubin.data())`. The cooperative-launch smoke intentionally
drops the old PTX-only `--relocatable-device-code=true` option on the CUBIN path:
the pod retry showed CUBIN plus that option produced an invalid driver image,
while the non-RDC CUBIN image is the appropriate direct module payload.

## Validation

Static validation is covered by
`tests.goal3962_collect_k_direct_cuda_cubin_loader_hardening_test`.
The updated Goal3951 inventory confirms there are no remaining direct
driver-loaded PTX sites under the tracked scanner.

Pod validation should exercise collect-k row-width-2 small, row-width-2 tiled,
dynamic row-width fallback, and cooperative-launch smoke paths, followed by a
clean all-app current-scale packet after this commit is pushed.

Pod API validation was run on the RTX 4000 Ada pod from clean commit
`e704d1d8` plus only the Goal3962 native patch:

- artifact: `docs/reports/goal3962_collect_k_direct_cuda_cubin_loader_hardening_2026-06-08/goal3962_collect_k_api_smoke.json`
- `row_width2_small_bitonic`: pass, 1024 unique rows
- `row_width2_tiled_cub_merge_final`: pass, 8192 unique rows
- `dynamic_row_width3_fallback`: pass, 257 unique rows
- cooperative-launch smoke: pass, 2 observed blocks and 2 synchronized blocks
- claim boundary: release, public speedup, broad RT-core, true-zero-copy, and
  paper-reproduction claims remain unauthorized.

## Boundary

This is internal compatibility hardening. It does not authorize release,
public-speedup wording, whole-app acceleration wording, broad RT-core wording,
true-zero-copy wording, automatic partner/backend selection, AMD performance
wording, paper reproduction, package-install wording, or app-specific
native-engine logic.
