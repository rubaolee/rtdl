# Goal3978: Current Scale Repeatability Probe

Date: 2026-06-08

## Purpose

Goal3978 runs the current ten-app scale-profile packet three consecutive times
on the Goal3976 fresh checkout and toolchain. The purpose is to separate
toolchain correctness from timing stability before changing benchmark scales or
doing another optimization pass.

## Environment

- Pod GPU: NVIDIA RTX 4000 Ada Generation
- Driver: 550.127.05
- Source commit: `62f005d90caca8eeea0d40cbbab430fe890a4fa3`
- Artifact directory:
  `docs/reports/goal3978_current_scale_repeatability_probe_2026-06-08/`

## Result

All three runs passed all ten rows. `aggregate.json` records
`run_count: 3` and `all_runs_pass: true`.

| Row | Mean Sec | Relative Range |
| --- | ---: | ---: |
| `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | 10.506 | 0.009% |
| `rt_dbscan_optix_numba_scale_default_65536_no_validation` | 3.253 | 0.006% |
| `rtnn_prepared_optix_scale_default_65536` | 3.253 | 0.010% |
| `raydb_style_optix_count_scale_default_262k` | 2.169 | 11.517% |
| `librts_spatial_index_optix_scale_default_32768` | 2.002 | 0.007% |
| `barnes_hut_numba_scale_default_8192` | 1.502 | 0.014% |
| `robot_collision_optix_scale_default_1024_no_probe_reference` | 1.718 | 18.161% |
| `hausdorff_xhd_scale_default_optix_threshold` | 1.502 | 0.024% |
| `triangle_counting_optix_rt_graph_2a1_scale_default_2048` | 1.502 | 0.026% |
| `contact_manifold_optix_scale_default_grid64` | 0.752 | 0.008% |

## Interpretation

The core toolchain and runner are stable: every run passed, and eight of ten
rows have sub-0.03% relative range. The two noisier rows are short enough that
small absolute shifts become large relative shifts:

- `robot_collision_optix_scale_default_1024_no_probe_reference`: 1.515s to
  1.827s
- `raydb_style_optix_count_scale_default_262k`: 2.002s to 2.252s

This points to benchmark scale calibration rather than a native loader,
partner-toolchain, or correctness problem. If we need claim-grade timing later,
the next target should be longer-duration row calibration for the short rows,
not another direct CUDA loader change.

## Boundary

This is repeatability and planning evidence only. It does not authorize
release, public-speedup wording, whole-app acceleration wording, broad RT-core
wording, true-zero-copy wording, AMD performance wording, paper reproduction,
package-install wording, automatic partner/backend selection, or app-specific
native-engine logic.
