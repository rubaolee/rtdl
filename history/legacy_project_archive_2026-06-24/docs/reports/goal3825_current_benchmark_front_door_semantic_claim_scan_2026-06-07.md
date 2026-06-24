# Goal3825 Current Benchmark Front-Door Semantic Claim Scan

Date: 2026-06-07

Status: implemented locally.

## Purpose

Goal3825 strengthens the Goal3823 front-door runner. A row no longer passes
only because the app process exits with code 0. The runner now also parses the
row stdout as JSON and recursively scans for forbidden claim flags that are
`true`.

The semantic scan checks for release, public-speedup, broad-RT-core,
paper-reproduction, true-zero-copy, automatic-partner-selection, AMD
performance, and app-specific native-engine claim flags.

## Implementation

File updated:

`scripts/goal3823_current_benchmark_front_door_runner.py`

The runner records a `semantic_stdout_check` object for each row:

- `stdout_json_parseable`
- `stdout_json_error`
- `claim_flag_violations`

If stdout is not JSON or any forbidden flag is true, the row status becomes
`fail`.

## A5000 Evidence

Artifact:

`docs/reports/goal3825_current_benchmark_front_door_semantic_a5000/summary.json`

Result at commit `a6691b48`: all ten registered rows passed, all ten stdout payloads parsed as JSON, and the recursive claim-flag scan found zero violations.

| Row | JSON parsed | Claim violations |
| --- | --- | ---: |
| `hausdorff_xhd_current_optix_threshold` | yes | 0 |
| `spatial_rayjoin_pip_count_current_prepared_optix` | yes | 0 |
| `rt_dbscan_optix_numba_prepared_grid` | yes | 0 |
| `robot_collision_optix_prepared_device_count` | yes | 0 |
| `contact_manifold_optix_native_collect_k` | yes | 0 |
| `raydb_style_optix_count_primitive_first` | yes | 0 |
| `barnes_hut_numba_exact_force` | yes | 0 |
| `librts_spatial_index_optix_aabb_index` | yes | 0 |
| `rtnn_prepared_optix_ranked_summary` | yes | 0 |
| `triangle_counting_optix_native_summary` | yes | 0 |

## Boundary

Goal3825 does not authorize release action, package-install wording, public
speedup wording, whole-app acceleration wording, broad RT-core wording,
paper-reproduction wording, true-zero-copy wording, AMD performance wording,
automatic partner selection, or app-specific native-engine logic.

It is a semantic smoke guard for current benchmark front doors, not a performance result.
