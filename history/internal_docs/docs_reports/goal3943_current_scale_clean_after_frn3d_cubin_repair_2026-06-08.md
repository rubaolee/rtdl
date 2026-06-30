# Goal3943: Clean Current-Scale Refresh After Fixed-Radius CUBIN Repair

Date: 2026-06-08

## Purpose

Goal3942 repaired the RTNN fixed-radius 3D direct CUDA module path by switching
its two direct CUDA loaders from PTX JIT to CUBIN loading. Goal3943 reruns the
full current-scale benchmark registry from a clean pushed commit to confirm the
repair did not only work in a dirty pod checkout.

## Environment

- source commit: `d792b037`
- clean working tree: `true`
- GPU: `NVIDIA RTX 4000 Ada Generation`
- driver: `550.127.05`
- GPU memory: `20475 MiB`
- OptiX library: repo-local `build/librtdl_optix.so`

## Result

The full current-scale runner passed all 10 benchmark rows:

| Row | Status | Wrapper elapsed sec | Claim violations |
| --- | --- | ---: | --- |
| `hausdorff_xhd_scale_default_optix_threshold` | pass | 1.502 | none |
| `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | pass | 10.006 | none |
| `rt_dbscan_optix_numba_scale_default_65536_no_validation` | pass | 3.503 | none |
| `robot_collision_optix_scale_default_1024_no_probe_reference` | pass | 1.316 | none |
| `contact_manifold_optix_scale_default_grid64` | pass | 0.752 | none |
| `raydb_style_optix_count_scale_default_262k` | pass | 1.752 | none |
| `barnes_hut_numba_scale_default_8192` | pass | 1.752 | none |
| `librts_spatial_index_optix_scale_default_32768` | pass | 1.752 | none |
| `rtnn_prepared_optix_scale_default_65536` | pass | 3.503 | none |
| `triangle_counting_optix_rt_graph_2a1_scale_default_2048` | pass | 1.252 | none |

Summary fields:

- `all_pass`: `true`
- `json_pass_count`: `10`
- runtime working tree clean: `true`
- selected prepared-session profile count: `4`
- validation status: `accept`

## RTNN Regression Closure

Goal3941's full-scale attempt failed only at
`rtnn_prepared_optix_scale_default_65536` with the CUDA unsupported-toolchain PTX
JIT error. In this clean rerun, the same row passed at commit `d792b037` with
zero stderr bytes and parseable JSON output.

That closes the immediate fixed-radius 3D toolchain regression found by the
current route scale refresh.

## Artifacts

- `docs/reports/goal3943_current_scale_clean_after_frn3d_cubin_repair_2026-06-08/goal3943_current_scale_clean_d792b037.json`
- `docs/reports/goal3943_current_scale_clean_after_frn3d_cubin_repair_2026-06-08/goal3943_current_scale_clean_d792b037.stdout.log`
- `docs/reports/goal3943_current_scale_clean_after_frn3d_cubin_repair_2026-06-08/outputs/`

## Boundary

This is internal current-scale evidence. It does not authorize release,
public-speedup wording, whole-app acceleration wording, broad RT-core wording,
paper-reproduction wording, true-zero-copy wording, automatic partner/backend
selection, AMD performance wording, package-install wording, or app-specific
native-engine logic.
