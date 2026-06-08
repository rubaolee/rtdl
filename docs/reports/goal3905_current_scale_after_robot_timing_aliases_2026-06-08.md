# Goal3905 Current Scale After Robot Timing Aliases

## Purpose

Goal3905 reruns the full ten-app A5000 scale packet after Goal3904 added
standard `benchmark_timing_sec` aliases to the robot-collision benchmark app.

Goal3902 showed that the robot payload was valid but timing-blind to the generic
scale-runner extractor. Goal3905 verifies that the same full packet now exposes
robot hot-path timing without changing the benchmark contract.

## Environment

- Pod: `ssh root@69.30.85.203 -p 22057 -i id_ed25519_rtdl_codex`
- Fresh pod clone: `/root/goal3905_robot_timing_scale_1780902518`
- Artifact root on pod:
  `/root/goal3905_robot_timing_scale_1780902518_artifacts/goal3905_current_scale_after_robot_timing_aliases_a5000`
- Source commit: `fb94b687`
- GPU: `NVIDIA RTX A5000, 580.126.09, 24564 MiB`
- Local artifact:
  `docs/reports/goal3905_current_scale_after_robot_timing_aliases_a5000/summary.json`

Runtime provenance stayed clean:

- `runtime_environment.working_tree_clean`: `true`
- `runtime_environment.git_status_short`: `[]`

## Result

- `exit_code`: `0`
- `all_pass`: `true`
- `json_pass_count`: `10`
- selected row count: `10`

| Row | Status | Process elapsed sec | Timing scalar count |
| --- | --- | ---: | ---: |
| `hausdorff_xhd_scale_default_optix_threshold` | pass | `1.752` | `14` |
| `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | pass | `10.256` | `19` |
| `rt_dbscan_optix_numba_scale_default_65536_no_validation` | pass | `3.503` | `14` |
| `robot_collision_optix_scale_default_1024_no_probe_reference` | pass | `1.752` | `7` |
| `contact_manifold_optix_scale_default_grid64` | pass | `0.752` | `2` |
| `raydb_style_optix_count_scale_default_262k` | pass | `1.752` | `7` |
| `barnes_hut_numba_scale_default_8192` | pass | `1.752` | `2` |
| `librts_spatial_index_optix_scale_default_32768` | pass | `2.002` | `6` |
| `rtnn_prepared_optix_scale_default_65536` | pass | `3.003` | `10` |
| `triangle_counting_optix_rt_graph_2a1_scale_default_2048` | pass | `1.252` | `4` |

## Robot-Collision Timing Repair

The robot row moved from `timing_scalar_count = 0` in Goal3902 to
`timing_scalar_count = 7` in Goal3905.

The packet now exposes these robot timing scalars:

- `$.benchmark_timing_sec.app_lowering_sec`: `0.586015`
- `$.benchmark_timing_sec.tail_phase_output_postprocess_sec`: `0.000000735`
- `$.benchmark_timing_sec.tail_phase_prepare_build_sec`: `0.124967`
- `$.benchmark_timing_sec.tail_phase_prepared_query_build_sec`: `0.211392`
- `$.benchmark_timing_sec.tail_phase_query_pack_sec`: `0.000000`
- `$.benchmark_timing_sec.tail_phase_traversal_sec`: `0.000042`
- `$.benchmark_timing_sec.tail_total_run_sec`: `0.000071`

This makes the robot row consistent with the rest of the scale packet: process elapsed remains pod-budget evidence, while app payload timing is visible for engineering interpretation.

## Boundary

Goal3905 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, paper-reproduction wording,
true-zero-copy wording, AMD performance wording, automatic partner/backend
selection, or app-specific native-engine logic.

This is an internal current-scale packet with repaired robot instrumentation,
not a public performance comparison and not a release packet.
