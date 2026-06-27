# Goal3955: Clean Current-Scale Refresh After Partner-Pack CUBIN Hardening

Date: 2026-06-08

## Purpose

Goal3954 moved the partner triangle/ray device-column pack direct CUDA helpers
from PTX module loading to CUBIN module loading. Goal3955 reruns the full
current-scale registry from a clean pushed commit after that native change.

## Environment

- source commit: `d9c736c5`
- clean working tree: `true`
- GPU: `NVIDIA RTX 4000 Ada Generation`
- driver: `550.127.05`
- GPU memory: `20475 MiB`

## Result

- `all_pass`: `true`
- `json_pass_count`: `10`
- row count: `10`
- validation status: `accept`
- claim flag violations: none in every row

| Row | Status | Wrapper elapsed sec |
| --- | --- | ---: |
| `hausdorff_xhd_scale_default_optix_threshold` | pass | 1.502 |
| `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | pass | 10.006 |
| `rt_dbscan_optix_numba_scale_default_65536_no_validation` | pass | 3.503 |
| `robot_collision_optix_scale_default_1024_no_probe_reference` | pass | 1.252 |
| `contact_manifold_optix_scale_default_grid64` | pass | 0.752 |
| `raydb_style_optix_count_scale_default_262k` | pass | 1.752 |
| `barnes_hut_numba_scale_default_8192` | pass | 1.752 |
| `librts_spatial_index_optix_scale_default_32768` | pass | 1.752 |
| `rtnn_prepared_optix_scale_default_65536` | pass | 3.253 |
| `triangle_counting_optix_rt_graph_2a1_scale_default_2048` | pass | 1.251 |

## Artifacts

- `docs/reports/goal3955_current_scale_clean_after_partner_pack_cubin_hardening_2026-06-08/goal3955_current_scale_clean_after_partner_pack_cubin.json`
- `docs/reports/goal3955_current_scale_clean_after_partner_pack_cubin_hardening_2026-06-08/goal3955_current_scale_clean_after_partner_pack_cubin.stdout.log`

## Boundary

This is internal current-scale evidence. It does not authorize release,
public-speedup wording, whole-app acceleration wording, broad RT-core wording,
paper-reproduction wording, true-zero-copy wording, automatic partner/backend
selection, AMD performance wording, package-install wording, or app-specific
native-engine logic.
