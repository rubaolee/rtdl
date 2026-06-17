# Goal4518 / V3 M122 Barnes-Hut Device-Column RT-Core Boundary

## Conclusion

M122 repairs Barnes-Hut wording: the current prepared aggregate-frontier device-column route is useful device-resident work inside the OptiX backend, implemented with CUDA driver kernels, but it is not current RT-core traversal evidence. Barnes-Hut RT-core wording now requires the future fused aggregate-tree primitive plus an OptiX launch/trace proof.

## Source Audit

| Check | Value |
| --- | --- |
| Source | `src/native/optix/rtdl_optix_api.cpp` |
| Runtime CUDA kernel source | `True` |
| `cuModuleLoadData` | `True` |
| `cuLaunchKernel` | `True` |
| `optixLaunch` | `False` |
| `optixTrace` | `False` |
| RT-core traversal claim authorized | `False` |

## Live Guidance Check

| Check | Value |
| --- | --- |
| `route_guidance_uses_cuda_device_column_wording` | `True` |
| `adequacy_uses_cuda_device_column_wording` | `True` |
| `route_guidance_stale_rtcore_device_column_wording` | `False` |
| `adequacy_stale_rtcore_device_column_wording` | `False` |

## Future Gate

- A CUDA-only fused implementation can be useful device evidence.
- A Barnes-Hut RT-core claim requires an OptiX pipeline launch and device traversal proof.
- Timing must separate build, traversal, continuation, and copy phases.
- Current public wording remains blocked.
