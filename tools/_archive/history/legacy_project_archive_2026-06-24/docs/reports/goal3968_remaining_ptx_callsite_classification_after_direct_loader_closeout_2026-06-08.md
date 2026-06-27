# Goal3968: Remaining PTX Callsite Classification After Direct Loader Closeout

Date: 2026-06-08

## Purpose

Goal3967 closed the direct CUDA driver-module PTX lane. Goal3968 classifies the
remaining `compile_to_ptx(...)` call sites so the project does not confuse two
different mechanisms:

- direct CUDA driver module loads through `cuModuleLoadData(...)`, which now use
  CUBIN payloads only;
- OptiX program-module PTX, which intentionally feeds OptiX pipeline creation.

## Classification

| Category | Count | Files | Status |
| --- | ---: | --- | --- |
| `compile_to_ptx(...)` helper definition | 1 | `src/native/optix/rtdl_optix_core.cpp` | expected |
| workload PTX call followed by `build_pipeline(...)` | 57 | `src/native/optix/rtdl_optix_workloads.cpp` | intentional OptiX pipeline PTX |
| direct CUDA driver load using PTX payload | 0 | `src/native/**` | closed |

Every workload `compile_to_ptx(...)` call found in `rtdl_optix_workloads.cpp` is
paired with a nearby `build_pipeline(...)` call. These are OptiX program-module
inputs, not CUDA driver module payloads.

## Interpretation

This goal does not recommend converting OptiX pipeline PTX to CUBIN. OptiX
pipeline construction expects program-module input in this path; the
compatibility debt that broke on RTX pods was the separate CUDA driver module
path loading PTX through `cuModuleLoadData(...)`.

The useful invariant after this goal is:

1. `cuModuleLoadData(...)` in `src/native` must load `cubin.data()`.
2. Remaining `compile_to_ptx(...)` workload call sites must be pipeline-building
   sites, not hidden CUDA driver module loads.

## Validation

Static validation is covered by
`tests.goal3968_remaining_ptx_callsite_classification_after_direct_loader_closeout_test`.

## Boundary

This is an internal compatibility classification. It does not authorize release,
public-speedup wording, whole-app acceleration wording, broad RT-core wording,
true-zero-copy wording, automatic partner/backend selection, AMD performance
wording, paper reproduction, package-install wording, or app-specific
native-engine logic.
