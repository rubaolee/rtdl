# Goal3858: Full Scale Refresh After Triangle Route Correction

Date: 2026-06-08

## Purpose

Goal3856 corrected the `triangle_counting` scale-profile row so it uses the
RT-Graph 2A1 prepared generic ray/triangle summary route instead of the older
`mode=run` host-indexed fallback. Goal3858 reruns the full 10-app scale-profile
packet on the A5000 pod after that correction.

Artifact:

`docs/reports/goal3858_full_scale_after_triangle_route_a5000/summary.json`

Command:

```text
PYTHONPATH=.pydeps_goal3788_numba:src:.
RTDL_OPTIX_LIBRARY=/root/rtdl_goal3788_clean_1780857956/build/librtdl_optix.so
RTDL_OPTIX_LIB=/root/rtdl_goal3788_clean_1780857956/build/librtdl_optix.so
RTDL_EMBREE_LIBRARY=/root/rtdl_goal3788_clean_1780857956/build/librtdl_embree.so
python scripts/goal3828_current_benchmark_scale_profile_runner.py \
  --output-json docs/reports/goal3858_full_scale_after_triangle_route_a5000/summary.json \
  --output-dir docs/reports/goal3858_full_scale_after_triangle_route_a5000/outputs \
  --heartbeat-sec 20
```

## Result

All 10 calibrated default rows passed. Every row emitted parseable JSON, stderr
was empty for every row, and the forbidden claim-flag scan found zero
violations.

| App | Row | Status | Process sec |
| --- | --- | --- | ---: |
| `hausdorff_xhd` | `hausdorff_xhd_scale_default_optix_threshold` | pass | `1.752` |
| `spatial_rayjoin` | `spatial_rayjoin_pip_count_scale_default_prepared_optix` | pass | `1.502` |
| `rt_dbscan` | `rt_dbscan_optix_numba_scale_default_65536_no_validation` | pass | `4.003` |
| `robot_collision` | `robot_collision_optix_scale_default_1024_no_probe_reference` | pass | `1.502` |
| `contact_manifold` | `contact_manifold_optix_scale_default_grid64` | pass | `0.751` |
| `raydb_style` | `raydb_style_optix_count_scale_default_262k` | pass | `2.002` |
| `barnes_hut` | `barnes_hut_numba_scale_default_8192` | pass | `1.753` |
| `librts_spatial_index` | `librts_spatial_index_optix_scale_default_32768` | pass | `1.752` |
| `rtnn` | `rtnn_prepared_optix_scale_default_65536` | pass | `3.003` |
| `triangle_counting` | `triangle_counting_optix_rt_graph_2a1_scale_default_2048` | pass | `1.502` |

## Triangle Row Check

The corrected triangle row now records:

- mode: `rt_graph_2a1_generic_rt`
- native symbol: `rtdl_optix_static_triangle_scene_3d_ray_any_hit_weighted_sum`
- RT-core path label: `generic_prepared_triangle_scene_3d_any_hit_weighted_sum`
- fixture copies: `2048`
- primitive / ray count: `10240 / 4096`
- oracle / RTDL weighted triangle count: `4096 / 4096`
- hot query median: `0.176 ms`
- rows materialized: `false`

This is still an internal scale-profile packet, not release authorization and
not public speedup wording. It proves the registry is coherent after the
triangle route correction and gives the next performance work a clean baseline.

## Boundary

No release, package-install, public speedup, broad RT-core, paper reproduction,
true-zero-copy, automatic partner-selection, or app-specific native-engine
claims are authorized by this packet.

