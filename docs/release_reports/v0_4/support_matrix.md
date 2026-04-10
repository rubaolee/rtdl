# RTDL v0.4 Support Matrix

Date: 2026-04-10
Status: prepared for release packaging, final Claude audit pending

## Reading Guide

Status wording used below:

- `accepted`: part of the prepared `v0.4` claim surface
- `accepted, bounded`: supported under a narrower or explicitly limited
  contract
- `supporting baseline`: useful for validation/comparison, not the primary RTDL
  execution path
- `not in v0.4 scope`: intentionally outside the accepted `v0.4` package

## Platform Roles

| Platform | Role | Current status |
| --- | --- | --- |
| Linux | primary validation platform for nearest-neighbor closure | accepted |
| local macOS | local development/doc/focused-test platform | accepted, bounded |
| Windows | preserved v0.3 visual-demo production host, not the v0.4 primary target | not in v0.4 scope |

## Backend Roles

| Backend | Role in v0.4 | Current status |
| --- | --- | --- |
| Python reference | correctness/truth path | accepted |
| native CPU / oracle | practical correctness backend | accepted |
| Embree | accelerated nearest-neighbor backend | accepted |
| SciPy `cKDTree` | external CPU comparison baseline | supporting baseline |
| PostGIS | bounded external comparison baseline | supporting baseline |
| OptiX | nearest-neighbor GPU path not closed in this line | not in v0.4 scope |
| Vulkan | nearest-neighbor GPU path not closed in this line | not in v0.4 scope |

## Workload Surface

| Surface | Boundary | Status |
| --- | --- | --- |
| `segment_polygon_hitcount` | stable earlier workload core | accepted |
| `segment_polygon_anyhit_rows` | stable earlier workload core | accepted |
| `polygon_pair_overlap_area_rows` | bounded earlier workload | accepted, bounded |
| `polygon_set_jaccard` | bounded earlier workload | accepted, bounded |
| `fixed_radius_neighbors` | new nearest-neighbor workload | accepted |
| `knn_rows` | new nearest-neighbor workload | accepted |

## Honest Summary

- `v0.4` is a non-graphical nearest-neighbor release line
- CPU/oracle and Embree are the RTDL execution backends closed in scope
- SciPy and bounded PostGIS are validation/comparison helpers
- GPU nearest-neighbor closure is not part of the accepted `v0.4` package
