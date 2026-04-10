# RTDL v0.4 Tag Preparation

Date: 2026-04-10
Prepared tag: `v0.4.0`
Status: prepared, not created yet

## Tag Meaning

`v0.4.0` will mark the first released RTDL version that adds the
nearest-neighbor workload family to the public non-graphical RTDL surface.

It is intended to mark:

- the stable earlier workload core already preserved in the repo
- the completed `fixed_radius_neighbors` line
- the completed `knn_rows` line
- the correctness-first CPU/oracle + Embree nearest-neighbor closure

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

## Final Tag Gate

Do not create the `v0.4.0` tag until:

- the post-`4am` Claude whole-line audit is complete
- any real findings from that audit are fixed
- the repo remains green on the bounded `v0.4` audit test slice
