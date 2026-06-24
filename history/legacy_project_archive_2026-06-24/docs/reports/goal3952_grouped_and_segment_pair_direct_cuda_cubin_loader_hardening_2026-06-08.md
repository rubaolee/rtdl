# Goal3952: Grouped Reduction and Segment-Pair Direct CUDA CUBIN Hardening

Date: 2026-06-08

## Purpose

Goal3951 identified the remaining driver-loaded PTX debt after the FRN3D and
nearest-neighbor CUBIN repairs. Goal3952 migrates the first recommended group:
RayDB/RayJoin-adjacent direct CUDA helpers for grouped integer reductions and
segment-pair count postprocessing.

## Scope

This goal changes three direct CUDA module loaders in
`src/native/optix/rtdl_optix_workloads.cpp`:

- `kDeviceColumnGroupedI64KernelSrc` / `device_column_grouped_i64_kernel.cu`
- `kSegmentPairAmbiguityCountKernelSrc` / `segment_pair_ambiguity_count_kernel.cu`
- `kSegmentPairDeviceRefinedCountKernelSrc` / `segment_pair_device_refined_count_kernel.cu`

Each now uses `compile_to_cubin(...)` plus `cuModuleLoadData(..., cubin.data())`.

The change does not touch OptiX pipeline PTX creation.

## Validation

Static validation is covered by
`tests.goal3952_grouped_and_segment_pair_direct_cuda_cubin_loader_hardening_test`.
The updated Goal3951 inventory confirms these three kernels are no longer in
the remaining driver-loaded PTX debt list.

Pod smoke was run on the active RTX pod after applying the patch and rebuilding
`librtdl_optix.so`:

| Row | Status | Claim violations |
| --- | --- | --- |
| `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | pass | none |
| `raydb_style_optix_count_scale_default_262k` | pass | none |

Artifacts:

- `docs/reports/goal3952_grouped_and_segment_pair_direct_cuda_cubin_loader_hardening_2026-06-08/goal3952_raydb_rayjoin_smoke.json`
- `docs/reports/goal3952_grouped_and_segment_pair_direct_cuda_cubin_loader_hardening_2026-06-08/outputs/`

A clean all-row current-scale packet should still be rerun after this commit is
pushed.

## Boundary

This is internal compatibility hardening. It does not authorize release,
public-speedup wording, whole-app acceleration wording, broad RT-core wording,
true-zero-copy wording, automatic partner/backend selection, AMD performance
wording, paper reproduction, package-install wording, or app-specific
native-engine logic.
