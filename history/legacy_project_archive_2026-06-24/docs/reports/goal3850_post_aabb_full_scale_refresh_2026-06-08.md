# Goal3850: Post-AABB Full Scale-Profile Refresh

Date: 2026-06-08

Status: internal A5000 health packet, not release authorization

## Purpose

Goal3850 refreshes the ten promoted benchmark scale-profile rows after
Goal3848's generic `AABB_INDEX_QUERY_2D` count-only per-ray device-counter
optimization. The goal is to confirm that the benchmark surface still runs
together and to measure the LibRTS row after the AABB primitive change.

This is not a public speedup table and not a release packet.

## Pod Evidence

Artifact directory:

- `docs/reports/goal3850_post_aabb_full_scale_refresh_a5000/summary.json`
- `docs/reports/goal3850_post_aabb_full_scale_refresh_a5000/outputs/`

Execution context:

- GPU: NVIDIA RTX A5000
- pod checkout commit: `36ed5346`
- runner: `scripts/goal3828_current_benchmark_scale_profile_runner.py`
- runner mode: file-backed stdout, `timeout-scale=1.25`

## Result Summary

All ten promoted benchmark apps passed:

| App | Row | Status | Process elapsed |
| --- | --- | --- | ---: |
| `hausdorff_xhd` | `hausdorff_xhd_scale_default_optix_threshold` | pass | 1.752s |
| `spatial_rayjoin` | `spatial_rayjoin_pip_count_scale_default_prepared_optix` | pass | 1.502s |
| `rt_dbscan` | `rt_dbscan_optix_numba_scale_default_65536_no_validation` | pass | 3.503s |
| `robot_collision` | `robot_collision_optix_scale_default_1024_no_probe_reference` | pass | 1.502s |
| `contact_manifold` | `contact_manifold_optix_scale_default_grid64` | pass | 0.751s |
| `raydb_style` | `raydb_style_optix_count_scale_default_262k` | pass | 2.002s |
| `barnes_hut` | `barnes_hut_numba_scale_default_8192` | pass | 1.752s |
| `librts_spatial_index` | `librts_spatial_index_optix_scale_default_32768` | pass | 2.002s |
| `rtnn` | `rtnn_prepared_optix_scale_default_65536` | pass | 2.753s |
| `triangle_counting` | `triangle_counting_optix_scale_default_native_2048` | pass | 1.752s |

Machine-readable summary:

- `all_pass=true`
- `json_pass_count=10`
- every row reports `status=pass`
- every stdout is valid JSON
- every row has zero claim-flag violations
- top-level release, public speedup, broad RT-core, and paper-reproduction flags
  remain `false`

## LibRTS Delta

The default-scale LibRTS row is still dominated by scene/query preparation and
process overhead, but the hot query metric improved:

| Metric | Goal3844 baseline | Goal3850 after Goal3848 | Ratio |
| --- | ---: | ---: | ---: |
| `repeat_protocol.query_sec_median` | 0.036598378 | 0.030948336 | 1.1826x |
| `repeat_protocol.query_sec_total` | 0.109869503 | 0.092865800 | 1.1831x |
| `point_contains` median | 0.009043010 | 0.007464319 | 1.2115x |
| `range_contains` median | 0.009098040 | 0.007682609 | 1.1842x |
| `range_intersects` median | 0.018457328 | 0.015801408 | 1.1681x |

Process elapsed did not improve in the same way (`1.752s -> 2.002s`) because
the scale-profile runner measures full process startup, scene preparation,
file-backed stdout, and normal pod noise. The meaningful Goal3848 metric is the
in-app hot query repeat metric.

## Boundary

Goal3850 does not authorize:

- release action,
- public speedup wording,
- broad RT-core speedup wording,
- paper reproduction wording,
- true zero-copy wording,
- automatic partner/backend selection,
- app-specific native-engine logic.

The packet says the benchmark surface remains healthy after Goal3848 and that
the LibRTS hot count-only primitive improved modestly. It does not settle the
next major performance direction.

