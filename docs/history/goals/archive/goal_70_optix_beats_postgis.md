# Goal 70: OptiX Beats PostGIS on Long Positive-Hit PIP

Priority:
- higher than Embree and Vulkan performance work

Problem:
- after Goal 69, RTDL positive-hit `pip` was parity-correct against PostGIS
  but still slower on the accepted measured packages
- the next target is the long `county_zipcode` case

Goal:
- make OptiX beat PostGIS on an accepted long positive-hit `pip` workload
- preserve exact parity
- keep the full-matrix Goal 50 / Goal 59 contract unchanged

Accepted timing boundary:
- execution-ready / prepacked OptiX timing
- the timed region may exclude one-time Python/runtime preparation:
  - `prepare_optix(...)`
  - `pack_points(...)`
  - `pack_polygons(...)`
- the report must state that boundary explicitly

Non-goals:
- claiming that OptiX beats PostGIS on all workloads
- claiming end-to-end wall-clock superiority under the original Goal 69 timing
  boundary
- broad Embree or Vulkan optimization in this goal
