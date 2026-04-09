# RTDL v0.3 Support Matrix

Date: 2026-04-09
Status: released as `v0.3.0`

## Reading Guide

Status wording used below:

- `accepted`: part of the released `v0.3.0` claim surface
- `accepted, bounded`: supported under an explicit narrower contract
- `supporting artifact`: preserved as backend/application evidence, not equal-polish public surface
- `limited local`: usable on local macOS as a support path, not the primary release-validation host

## Platform Roles

| Platform | Role | Current status |
| --- | --- | --- |
| Linux | primary validation platform for bounded backend closure | accepted |
| Windows | primary polished visual-demo production host | accepted |
| local macOS | local development/doc/focused-test platform | limited local |

## Backend Roles

| Backend | Role in v0.3.0 | Current status |
| --- | --- | --- |
| Python reference | correctness/trust reference | accepted |
| native CPU / oracle | practical correctness and fallback backend | accepted |
| Embree | strongest polished visual-demo backend | accepted |
| OptiX | supporting Linux GPU backend for bounded 3D demo closure | accepted, bounded |
| Vulkan | supporting Linux GPU backend for bounded 3D demo closure | accepted, bounded |
| PostGIS | external indexed comparison baseline for workload-family evidence | accepted |

## Workload And Demo Surface

| Surface | Boundary | Status |
| --- | --- | --- |
| `segment_polygon_hitcount` | released workload surface | accepted |
| `segment_polygon_anyhit_rows` | released workload surface | accepted |
| `polygon_pair_overlap_area_rows` | narrow pathology/unit-cell contract | accepted, bounded |
| `polygon_set_jaccard` | narrow pathology/unit-cell contract | accepted, bounded |
| bounded 3D ray/triangle demo line | RTDL-plus-Python application proof | accepted, bounded |

## Visual-Demo Artifact Roles

| Artifact path | Role | Status |
| --- | --- | --- |
| Windows Embree hidden-star public video | main public-facing visual artifact | accepted |
| hidden-star source in `examples/visual_demo/` | main demo source | accepted |
| Linux OptiX hidden-star 256 video | supporting backend artifact | supporting artifact |
| Linux Vulkan hidden-star 256 video | supporting backend artifact | supporting artifact |

## Honest Summary

- `v0.3.0` keeps the `v0.2.0` workload core intact
- `v0.3.0` adds a bounded application/demo proof layer
- Windows Embree is the strongest polished movie path
- Linux OptiX/Vulkan artifacts are real and preserved, but supporting rather than equal-polish headline artifacts
