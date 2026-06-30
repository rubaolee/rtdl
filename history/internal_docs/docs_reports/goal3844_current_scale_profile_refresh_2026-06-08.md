# Goal3844 Current Scale-Profile Refresh

Date: 2026-06-08

Status: internal evidence packet, not release authorization

## Purpose

Goal3844 refreshes the current ten-app scale-profile packet on the A5000 after
Goal3842's RayJoin PIP batch-executor update. The purpose is simple: prove that
the current promoted benchmark front doors still run together, at calibrated
default scale, with file-backed stdout and with all claim-boundary flags blocked.

This is not a new public speedup table. It is a health and readiness evidence
packet for the current benchmark-app surface.

## Pod Evidence

Artifact directory:

- `docs/reports/goal3844_current_scale_profiles_refresh_a5000/summary.json`
- `docs/reports/goal3844_current_scale_profiles_refresh_a5000/outputs/`

Execution context recorded in the pod stdout log:

- GPU: NVIDIA RTX A5000
- commit: `ad4bea28960f`
- runner: `scripts/goal3828_current_benchmark_scale_profile_runner.py`
- runner mode: file-backed stdout, heartbeat enabled, `timeout-scale=1.25`

The pod initially had an untracked old Goal3842 artifact that blocked
`git pull --ff-only`. The artifact was moved into a timestamped pod backup, then
the same fast-forward and runner were restarted. Nothing was deleted.

## Result Summary

All ten promoted benchmark apps passed:

| App | Row | Status | Process elapsed |
| --- | --- | --- | ---: |
| `hausdorff_xhd` | `hausdorff_xhd_scale_default_optix_threshold` | pass | 1.752s |
| `spatial_rayjoin` | `spatial_rayjoin_pip_count_scale_default_prepared_optix` | pass | 1.502s |
| `rt_dbscan` | `rt_dbscan_optix_numba_scale_default_65536_no_validation` | pass | 4.004s |
| `robot_collision` | `robot_collision_optix_scale_default_1024_no_probe_reference` | pass | 1.546s |
| `contact_manifold` | `contact_manifold_optix_scale_default_grid64` | pass | 1.002s |
| `raydb_style` | `raydb_style_optix_count_scale_default_262k` | pass | 2.253s |
| `barnes_hut` | `barnes_hut_numba_scale_default_8192` | pass | 1.753s |
| `librts_spatial_index` | `librts_spatial_index_optix_scale_default_32768` | pass | 1.752s |
| `rtnn` | `rtnn_prepared_optix_scale_default_65536` | pass | 2.753s |
| `triangle_counting` | `triangle_counting_optix_scale_default_native_2048` | pass | 1.502s |

Machine-readable summary:

- `all_pass=true`
- `json_pass_count=10`
- `row_count=10`
- every row reports `status=pass`
- every row's stdout is valid JSON
- every row has zero claim-flag violations
- top-level release, public speedup, broad RT-core, and paper-reproduction flags
  remain `false`

## Notable Row Checks

- `rt_dbscan` uses the expected OptiX threshold plus Numba prepared-grid
  continuation path at 65,536 points, with `raw_cuda_kernel_required=false`.
- `barnes_hut` uses the no-RawKernel Numba exact-force reference path in summary
  output mode, keeping stdout compact.
- `spatial_rayjoin` uses the prepared OptiX PIP count scale row. This is still
  the current scale-profile health row, not the Goal3842 repeated-request batch
  executor packet and not a one-shot public speedup claim.
- `triangle_counting` uses the explicit native summary row and still states that
  it is not an authorized RT-core graph-acceleration claim.

## Boundary

Goal3844 does not authorize:

- release action,
- public speedup wording,
- broad RT-core speedup wording,
- paper reproduction wording,
- true zero-copy wording,
- package-install readiness wording,
- automatic partner/backend selection,
- app-specific native-engine logic.

The packet is useful because it says the current benchmark surface is still
coherent after recent RayJoin and Numba work. It does not settle the next major
performance direction; that remains the separate v2.x benchmark-performance
workstream.
