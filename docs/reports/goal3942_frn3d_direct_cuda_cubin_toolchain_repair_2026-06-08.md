# Goal3942: Fixed-Radius 3D Direct CUDA CUBIN Toolchain Repair

Date: 2026-06-08

## Purpose

Goal3936 proved the shape-pair direct CUDA module path should use CUBIN rather
than PTX JIT on current RTX pods. Goal3941 then found the same toolchain class
in the RTNN fixed-radius 3D path: the current-scale RTNN row failed with
`CUDA driver error: the provided PTX was compiled with an unsupported toolchain`.

Goal3942 repairs that fixed-radius 3D direct CUDA loader only. It does not
broaden the repair to every remaining direct CUDA module path.

## Change

`src/native/optix/rtdl_optix_workloads.cpp` now loads the two fixed-radius 3D
CUDA module sources through `compile_to_cubin(...)`:

- `kFixedRadiusNeighbors3DKernelSrc` / `frn3d_kernel.cu`
- `kFixedRadiusNeighbors3DGridKernelSrc` / `frn3d_grid_kernel.cu`

Both module loads now pass `cubin.data()` to `cuModuleLoadData(...)` instead of
passing PTX text through `ptx.c_str()`.

This matches the Goal3933 repair pattern while keeping the edit narrow.

## Pod Evidence

After applying the repair on the active RTX pod and rebuilding
`librtdl_optix.so`, the previously failing RTNN current-scale row completed:

- app: `rtnn_neighbor_search`
- mode: `prepared_optix_ranked_summary`
- point count: `65536`
- radius: `0.02`
- k: `50`
- repeat: `3`
- stderr bytes: `0`
- runner payload `ok`: `true`
- hot query timings: `0.000475`, `0.000214`, `0.000188` seconds

Artifacts:

- `docs/reports/goal3942_frn3d_direct_cuda_cubin_toolchain_repair_2026-06-08/rtnn_frn3d_cubin.json`
- `docs/reports/goal3942_frn3d_direct_cuda_cubin_toolchain_repair_2026-06-08/rtnn_frn3d_cubin.stderr.txt`

## Boundary

This is toolchain compatibility evidence for one direct CUDA module family. It
does not authorize release, public speedup wording, broad RT-core wording, true
zero-copy wording, automatic partner/backend selection, AMD performance wording,
paper reproduction, or app-specific native-engine logic.

The next evidence step is a clean all-app current-scale rerun from a pushed
commit containing this repair.
