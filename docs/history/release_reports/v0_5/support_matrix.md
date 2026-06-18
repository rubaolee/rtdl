# RTDL v0.5 Support Matrix

Date: 2026-04-13
Status: release package prepared for `v0.5.0`

## Reading Guide

Status wording used below:

- `accepted`: part of the prepared `v0.5` claim surface
- `accepted, bounded`: supported under a narrower or explicitly limited
  contract
- `supporting baseline`: useful for validation/comparison, not the primary RTDL
  execution path
- `not in v0.5 scope`: intentionally outside the accepted `v0.5` package

## Platform Roles

| Platform | Role | Current status |
| --- | --- | --- |
| Linux | primary validation platform for the `v0.5` 3D nearest-neighbor line | accepted |
| local macOS | development, focused regression, bounded correctness checks | accepted, bounded |
| Windows | secondary portability/bring-up host; bounded correctness checks | accepted, bounded |

## Backend Roles

| Backend | Role in `v0.5` | Current status |
| --- | --- | --- |
| Python reference | correctness / truth path | accepted |
| native CPU / oracle | compiled correctness baseline | accepted |
| PostGIS | external correctness and timing anchor | supporting baseline |
| Embree | accelerated CPU backend | accepted |
| OptiX | accelerated GPU backend | accepted |
| Vulkan | accelerated GPU backend; Linux-primary validation story | accepted, bounded |
| cuNSearch | external research comparison path with explicit duplicate/large-set boundaries | accepted, bounded |

## Workload Surface

| Surface | Boundary | Status |
| --- | --- | --- |
| `segment_polygon_hitcount` | carried from stable earlier workload core | accepted |
| `segment_polygon_anyhit_rows` | carried from stable earlier workload core | accepted |
| `polygon_pair_overlap_area_rows` | bounded earlier workload | accepted, bounded |
| `polygon_set_jaccard` | bounded earlier workload | accepted, bounded |
| `fixed_radius_neighbors` 2D | carried from released NN line | accepted |
| `knn_rows` 2D | carried from released NN line | accepted |
| `bounded_knn_rows` 2D | RTNN-fidelity extension line | accepted |
| `fixed_radius_neighbors` 3D | closed on CPU/oracle, Embree, OptiX, Vulkan; Linux-validated | accepted |
| `bounded_knn_rows` 3D | closed on CPU/oracle, Embree, OptiX, Vulkan; Linux-validated | accepted |
| `knn_rows` 3D | closed on CPU/oracle, Embree, OptiX, Vulkan; Linux-validated | accepted |

## Honest Summary

- `v0.5` is the released 3D nearest-neighbor line for the repo
- Linux is the platform for the main large-scale nearest-neighbor performance
  story
- Windows and local macOS are part of the bounded correctness story, not the
  large-scale performance claim
- PostGIS and cuNSearch remain supporting comparison/baseline systems, not the
  target RTDL runtime surface
- Vulkan is part of the accepted `v0.5` line, but under a Linux-primary and
  cross-platform-bounded interpretation
