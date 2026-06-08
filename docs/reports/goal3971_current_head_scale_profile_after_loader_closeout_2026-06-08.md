# Goal3971: Current-Head Scale Profile After Loader Closeout

Date: 2026-06-08

## Purpose

Goal3971 reruns the ten-app current benchmark scale-profile packet on the RTX
4000 Ada pod after the direct CUDA driver-loader hardening lane closed. This is
a current evidence refresh, not a release authorization and not a new speedup
claim.

## Pod And Source

- Pod SSH command used by the user: `ssh root@213.173.108.27 -p 15138 -i ~/.ssh/id_ed25519`
- Codex key used locally: `id_ed25519_rtdl_codex`
- GPU: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.05`
- Fresh checkout directory: `/root/goal3971_current_head_scale.71XR3W/repo`
- Source commit tested: `e383c4e4`
- Working tree in pod artifact: clean

Commit `e383c4e4` is the runtime-code head after Goal3968. Later commit
`f6f5c187` adds only the Goal3969/3970 external review documents, so this packet
is runtime-equivalent to the current pushed head.

## Partner Toolchain Setup Lesson

The first clean checkout run passed the seven primitive-only or OptiX-only rows
but failed the three partner rows because Numba was not installed. Installing the
latest Numba on Python 3.12 was not enough: Numba emitted PTX `.version 8.7`,
while the pod's driver-side linker reported support only up to PTX `8.4`.

The working partner setup for this driver-550 pod was:

- RTDL OptiX build: CUDA `/usr/local/cuda-12` plus OptiX SDK `v8.0.0`.
- Numba stack: `numba==0.60.0`, `numpy==2.0.2`.
- Numba CUDA compiler bits: `nvidia-cuda-nvcc-cu12==12.4.131`.
- Numba environment: `CUDA_HOME=/usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvcc`.
- RayJoin CuPy refiner: `cupy-cuda12x==14.1.1`.

This distinction matters: RTDL/OptiX can build with the installed CUDA 12.8
toolkit, while Numba must be pointed at a CUDA 12.4 compiler package on this
driver to avoid unsupported-PTX-version failures.

## Result

| App | Row | Status | Elapsed seconds |
| --- | --- | --- | ---: |
| `hausdorff_xhd` | `hausdorff_xhd_scale_default_optix_threshold` | pass | 1.502 |
| `spatial_rayjoin` | `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | pass | 11.506 |
| `rt_dbscan` | `rt_dbscan_optix_numba_scale_default_65536_no_validation` | pass | 3.252 |
| `robot_collision` | `robot_collision_optix_scale_default_1024_no_probe_reference` | pass | 1.752 |
| `contact_manifold` | `contact_manifold_optix_scale_default_grid64` | pass | 0.752 |
| `raydb_style` | `raydb_style_optix_count_scale_default_262k` | pass | 2.002 |
| `barnes_hut` | `barnes_hut_numba_scale_default_8192` | pass | 1.502 |
| `librts_spatial_index` | `librts_spatial_index_optix_scale_default_32768` | pass | 2.002 |
| `rtnn` | `rtnn_prepared_optix_scale_default_65536` | pass | 3.253 |
| `triangle_counting` | `triangle_counting_optix_rt_graph_2a1_scale_default_2048` | pass | 1.502 |

Machine-readable evidence is saved in:

- `docs/reports/goal3971_current_head_scale_profile_after_loader_closeout_2026-06-08/summary.json`
- `docs/reports/goal3971_current_head_scale_profile_after_loader_closeout_2026-06-08/outputs/`
- `docs/reports/goal3971_current_head_scale_profile_after_loader_closeout_2026-06-08/run.stdout.log`
- `docs/reports/goal3971_current_head_scale_profile_after_loader_closeout_2026-06-08/final_partner_complete_rerun.log`

The intermediate setup/debug logs are also preserved in the same directory to
document why the final Numba/CuPy toolchain was required.

## Boundary

This is an internal scale-profile evidence refresh. It does not authorize
release, public-speedup wording, whole-app acceleration wording, broad RT-core
wording, true-zero-copy wording, automatic partner/backend selection, AMD
performance wording, paper reproduction, package-install wording, or
app-specific native-engine logic.
