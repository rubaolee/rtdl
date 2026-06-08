# Goal3976: Fresh Helper-Driven Current Scale Validation

Date: 2026-06-08

## Purpose

Goal3976 validates that the Goal3975 partner setup helper is usable as a
fresh-checkout pod runbook step, not only as a static script or one-off manual
lesson.

The run used the same RTX 4000 Ada pod as Goal3971, cloned current `main`,
executed `scripts/goal3975_current_scale_partner_pod_setup.sh`, built OptiX,
and ran the current ten-app scale-profile packet.

## Environment

- Pod GPU: NVIDIA RTX 4000 Ada Generation
- Driver: 550.127.05
- Fresh checkout source commit: `62f005d90caca8eeea0d40cbbab430fe890a4fa3`
- Fresh checkout status before execution: clean
- Artifact directory:
  `docs/reports/goal3976_fresh_helper_current_scale_validation_2026-06-08/`

## Helper Validation

The helper ran with full install enabled. The pod already had the requested
packages installed, so `pip` reported them as satisfied:

- `numba==0.60.0`
- `numpy==2.0.2`
- `nvidia-cuda-nvcc-cu12==12.4.131`
- `cupy-cuda12x==14.1.1`

The helper smoke printed `partner_smoke_ok` and emitted clean copy-paste
exports for the current scale-profile runner.

The important environment split remains:

- RTDL OptiX build uses `RTDL_CUDA_PREFIX=/usr/local/cuda-12`.
- Numba uses `CUDA_HOME=/usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvcc`.

That split keeps the native RTDL build on the system CUDA toolkit while keeping
Numba on the CUDA 12.4 compiler package that emits driver-550-compatible PTX.

## Result

The fresh-helper run passed all ten current scale-profile rows:

| Row | Status | Elapsed Sec |
| --- | --- | ---: |
| `hausdorff_xhd_scale_default_optix_threshold` | pass | 1.502 |
| `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | pass | 10.506 |
| `rt_dbscan_optix_numba_scale_default_65536_no_validation` | pass | 3.252 |
| `robot_collision_optix_scale_default_1024_no_probe_reference` | pass | 1.514 |
| `contact_manifold_optix_scale_default_grid64` | pass | 0.752 |
| `raydb_style_optix_count_scale_default_262k` | pass | 2.002 |
| `barnes_hut_numba_scale_default_8192` | pass | 1.752 |
| `librts_spatial_index_optix_scale_default_32768` | pass | 2.002 |
| `rtnn_prepared_optix_scale_default_65536` | pass | 3.252 |
| `triangle_counting_optix_rt_graph_2a1_scale_default_2048` | pass | 1.502 |

`summary.json` records `all_pass: true` and `json_pass_count: 10`.
The scale runner stderr log is empty.

## Boundary

This is reproducibility evidence for the current internal scale-profile packet.
It does not authorize release, public-speedup wording, whole-app acceleration
wording, broad RT-core wording, true-zero-copy wording, AMD performance wording,
paper reproduction, package-install wording, automatic partner/backend
selection, or app-specific native-engine logic.
