# Goal2288: Packed-Input Learner Docs Update

Status: implemented locally.

## Purpose

Goal2284/2285 found a practical v2 programming-model lesson: repeated prepared
segment-pair calls should reuse packed left/query geometry instead of passing
large Python tuples every time. Goal2288 moves that lesson into learner-facing
docs.

## Updated Files

| File | Update |
| --- | --- |
| `docs/tutorials/v2_app_building.md` | Added `Reuse Prepared And Packed Inputs` with a minimal OptiX segment-pair code snippet and the narrow Goal2284/2285 boundary. |
| `docs/tutorials/segment_polygon_workloads.md` | Added `Repeated OptiX Calls` pointing segment/polygon learners to the prepared/packed pattern. |

## Boundary

The docs do not claim final v2.0 release readiness, broad RT-core speedup,
whole-RayJoin speedup, or that all workloads get a 20x gain. They teach the
current source-tree v2 pattern: prepare reusable build-side state and prepack
reusable probe/query geometry when repeated calls would otherwise repack Python
records.
