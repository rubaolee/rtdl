# RTDL v0.4 Preview Support Matrix

Date: 2026-04-10
Status: preview only, not released

## Reading Guide

Status wording used below:

- `implemented`: present in the current preview line
- `implemented, bounded`: present under an explicit narrower contract
- `planned`: named in the preview package, but not yet closed
- `not in v0.4 preview`: outside the current preview scope

## Platform Roles

| Platform | Role | Current status |
| --- | --- | --- |
| Linux | primary validation platform for stronger backend evidence | planned / ongoing |
| This Mac | local development, bounded correctness, docs, and focused testing | implemented, bounded |

## Nearest-Neighbor Backend Status

| Backend / path | `fixed_radius_neighbors` | `knn_rows` | Status note |
| --- | --- | --- | --- |
| Python truth path | implemented | implemented | correctness reference |
| native CPU / oracle | implemented | implemented | first native execution path |
| Embree | implemented | implemented | current accelerated backend |
| SciPy `cKDTree` baseline | implemented, bounded | implemented, bounded | optional external baseline |
| PostGIS baseline | implemented, bounded | implemented, bounded | optional comparison helper |
| OptiX | not in v0.4 preview | not in v0.4 preview | no current acceptance requirement |
| Vulkan | not in v0.4 preview | not in v0.4 preview | no current acceptance requirement |

## Public Surface Status

| Surface | Current status | Note |
| --- | --- | --- |
| workload contracts | implemented | frozen for both workloads |
| DSL surface | implemented | public authoring exists |
| truth-path examples | implemented | reference examples exist |
| top-level public examples | implemented | `examples/rtdl_fixed_radius_neighbors.py`, `examples/rtdl_knn_rows.py` |
| bounded scaling note | implemented | local macOS note preserved in repo |
| final release audit | planned | required before tagging |
| final `v0.4` package | planned | preview only right now |

## Honest Summary

- the nearest-neighbor family is now real and runnable on the current preview
  line
- Embree is the strongest current accelerated backend in the preview package
- external baselines are optional helpers, not package prerequisites
- `v0.4` should still be read as an active preview, not a released surface
