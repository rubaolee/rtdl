# Goal3966: Native Direct CUDA Module Load Scan After Collect-K Hardening

Date: 2026-06-08

## Purpose

Goal3966 records a broader scan after Goal3962. Goal3951 tracked direct
`cuModuleLoadData(..., ptx.c_str())` debt in the OptiX API/workloads files.
After the collect-k conversion, this goal checks the whole `src/native` tree for
direct CUDA module loads and confirms they all load CUBIN payloads.

## Result

- direct `cuModuleLoadData` sites in `src/native`: `28`
- direct `cuModuleLoadData(..., cubin.data())` sites: `28`
- direct `cuModuleLoadData(..., ptx.c_str())` sites: `0`
- direct `cuModuleLoadData(..., ptx.data())` sites: `0`

OptiX pipeline PTX compilation remains intentionally out of scope: PTX strings
that feed `build_pipeline(...)` are OptiX program-module inputs, not CUDA driver
module payloads.

## Validation

Static validation is covered by
`tests.goal3966_native_direct_cuda_module_load_scan_after_collect_k_test`.

## Boundary

This is an internal compatibility audit. It does not authorize release,
public-speedup wording, whole-app acceleration wording, broad RT-core wording,
true-zero-copy wording, automatic partner/backend selection, AMD performance
wording, paper reproduction, package-install wording, or app-specific
native-engine logic.
