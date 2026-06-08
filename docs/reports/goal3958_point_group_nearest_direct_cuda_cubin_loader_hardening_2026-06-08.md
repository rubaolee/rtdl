# Goal3958: Point-Group-Nearest Direct CUDA CUBIN Loader Hardening

Date: 2026-06-08

## Purpose

Goal3958 migrates the point-group-nearest split/reduce helper CUDA modules from
driver-loaded PTX to CUBIN. These helpers sit beside OptiX nearest/grouped
continuations, but they are ordinary CUDA helper modules, not OptiX pipeline
program modules.

## Scope

This goal changes three direct CUDA module load sites in
`src/native/optix/rtdl_optix_workloads.cpp`:

- `point_group_nearest_split_columns_kernel.cu`
- `point_group_nearest_max_reduce_kernel.cu`
- the active-frontier reuse of `point_group_nearest_max_reduce_kernel.cu`

Each now uses `compile_to_cubin(...)` plus `cuModuleLoadData(..., cubin.data())`.

The point-group OptiX RT probe pipelines still use `compile_to_ptx(...)` because
they feed `build_pipeline(...)`.

## Validation

Static validation is covered by
`tests.goal3958_point_group_nearest_direct_cuda_cubin_loader_hardening_test`.
The updated Goal3951 inventory confirms these three kernels are no longer in the
remaining driver-loaded PTX debt list.

Pod API validation was run on the RTX 4000 Ada pod from clean commit
`d9c736c5` plus only the Goal3958 native patch:

- artifact: `docs/reports/goal3958_point_group_nearest_direct_cuda_cubin_loader_hardening_2026-06-08/goal3958_point_group_nearest_api_smoke.json`
- split-column helper: `point_group_nearest_split_columns_kernel.cu`
- reduce helper: `point_group_nearest_max_reduce_kernel.cu`
- result: all 7 API checks pass
- checked paths:
  - device-column query, neighbor, and distance outputs match raw witness rows
  - max-distance reduction matches the raw-row argmax
  - active-frontier max-distance reduction reports the device-side native
    reduction path
- claim boundary: release, public speedup, broad RT-core, true-zero-copy, and
  paper-reproduction claims remain unauthorized.

A clean all-app current-scale packet should be rerun after this commit is
pushed.

## Boundary

This is internal compatibility hardening. It does not authorize release,
public-speedup wording, whole-app acceleration wording, broad RT-core wording,
true-zero-copy wording, automatic partner/backend selection, AMD performance
wording, paper reproduction, package-install wording, or app-specific
native-engine logic.
