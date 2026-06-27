# Goal 71: Embree Beats PostGIS on Long Positive-Hit PIP

Priority:
- after Goal 70
- before Vulkan performance work

Problem:
- Goal 69 established parity-correct positive-hit `pip` for Embree, but Embree
  was still slower than PostGIS on the accepted measured packages
- the next target is the long `county_zipcode` case under the same prepared
  execution boundary that made Goal 70 meaningful for OptiX

Goal:
- make Embree beat PostGIS on an accepted long positive-hit `pip` workload
- preserve exact parity
- keep the full-matrix Goal 50 / Goal 59 contract unchanged

Accepted timing boundary:
- execution-ready / prepacked Embree timing
- the timed region may exclude one-time preparation:
  - `prepare_embree(...)`
  - `pack_points(...)`
  - `pack_polygons(...)`
  - `prepared.bind(...)`
- the report must keep that boundary explicit

Non-goals:
- claiming that Embree beats PostGIS on all workloads
- claiming end-to-end wall-clock superiority under the Goal 69 timing boundary
- broad Vulkan optimization in this goal
