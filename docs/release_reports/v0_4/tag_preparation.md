# RTDL v0.4 Tag Preparation

Date: 2026-04-10
Published tag: `v0.4.0`
Status: published

## Tag Meaning

`v0.4.0` marks the first released RTDL version that adds the
nearest-neighbor workload family to the public non-graphical RTDL surface.

It marks:

- the stable earlier workload core already preserved in the repo
- the completed `fixed_radius_neighbors` line
- the completed `knn_rows` line
- the correctness-first CPU/oracle + Embree + OptiX + Vulkan nearest-neighbor
  closure

## Public Entry Points

- root front door:
  - [README.md](../../../README.md)
- docs index:
  - [docs/README.md](../../README.md)
- public nearest-neighbor examples:
  - [rtdl_fixed_radius_neighbors.py](../../../examples/rtdl_fixed_radius_neighbors.py)
  - [rtdl_knn_rows.py](../../../examples/rtdl_knn_rows.py)
- foundations page:
  - [workloads_and_research_foundations.md](../../workloads_and_research_foundations.md)

## Tag Record

The final technical release gate was satisfied before publication:

- the whole-line Gemini and Claude audits completed
- the later heavy Linux benchmark is preserved
- the accelerated boundary fix restored heavy-case parity
- the focused post-fix verification slices remained green

The published tag points to the released `v0.4.0` commit on `main`.
