# RTDL v0.2 Feature Status

Date: 2026-04-06
Status: current

This note answers one narrow question:

- what is actually new in v0.2 compared with the archived v0.1 baseline?

## New In v0.2

### 1. One additional workload family is now closed

The first closed v0.2 workload-family expansion is:

- `segment_polygon_hitcount`

In practical terms, RTDL can now present this workload as a real feature rather
than just an internal capability.

Current user-facing entry points:

- [rtdl_segment_polygon_hitcount.py](/Users/rl2025/rtdl_python_only/examples/rtdl_segment_polygon_hitcount.py)
- [rtdl_road_hazard_screening.py](/Users/rl2025/rtdl_python_only/examples/rtdl_road_hazard_screening.py)

### 2. Generate-only mode now exists as a narrow kept feature

The v0.2 line now includes a constrained generate-only path:

- [rtdl_generate_only.py](/Users/rl2025/rtdl_python_only/scripts/rtdl_generate_only.py)

That path is still intentionally narrow. It should be described as a kept MVP,
not as broad general code generation.

### 3. The feature has stronger backend and correctness evidence

Compared with the v0.1 baseline, the current `segment_polygon_hitcount` feature
now has:

- workload-family closure
- deterministic authored / fixture / derived cases
- prepared-path characterization for Embree and OptiX
- large deterministic PostGIS validation
- full backend audit across:
  - Python oracle
  - native CPU oracle
  - Embree
  - OptiX
  - Vulkan

## Important Honesty Note

The new feature should still be described carefully.

It is correct and productized, but it should not yet be described as a mature
RT-core-native traversal story across all backends.

The clearest current example is Vulkan:

- accepted for correctness on this feature
- not accepted yet as a native optimized/parallel traversal story for this
  workload family
