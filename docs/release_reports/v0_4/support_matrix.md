# RTDL v0.4 Support Matrix

Date: 2026-04-10
Status: reopened for GPU completion, tag not created

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
| Windows | secondary validation host for portability and pre-release reruns | accepted, bounded |

## Backend Roles

| Backend | Role in v0.4 | Current status |
| --- | --- | --- |
| Python reference | correctness/truth path | accepted |
| native CPU / oracle | practical correctness backend | accepted |
| Embree | accelerated nearest-neighbor backend | accepted |
| SciPy `cKDTree` | external CPU comparison baseline | supporting baseline |
| PostGIS | bounded external comparison baseline | supporting baseline |
| OptiX | primary GPU RT-core backend for the reopened nearest-neighbor line | accepted |
| Vulkan | correctness-first GPU RT backend for the reopened nearest-neighbor line | accepted, bounded |

## Workload Surface

| Surface | Boundary | Status |
| --- | --- | --- |
| `segment_polygon_hitcount` | stable earlier workload core | accepted |
| `segment_polygon_anyhit_rows` | stable earlier workload core | accepted |
| `polygon_pair_overlap_area_rows` | bounded earlier workload | accepted, bounded |
| `polygon_set_jaccard` | bounded earlier workload | accepted, bounded |
| `fixed_radius_neighbors` | new nearest-neighbor workload, now running across CPU, Embree, OptiX, and Vulkan | accepted |
| `knn_rows` | new nearest-neighbor workload, now running across CPU, Embree, OptiX, and Vulkan | accepted |

## Honest Summary

- `v0.4` is a non-graphical nearest-neighbor release line reopened under a GPU-required bar
- CPU/oracle, Embree, and OptiX are part of the intended execution closure surface
- Vulkan is part of the intended execution closure surface, but under a correctness-first and performance-bounded interpretation
- SciPy and bounded PostGIS remain validation/comparison helpers
- final release readiness still depends on the post-GPU benchmark/support-matrix refresh and final re-audit
