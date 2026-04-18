# RTDL Feature Guide

This is the **high-level orientation guide** for RTDL.

Audience:

- readers who want a fast overview of what RTDL currently is
- people deciding whether the current system fits their use case
- reviewers who need the feature surface without reading the full language docs

This guide is intentionally lighter than the documents in `docs/rtdl/`.

## Practical Promise

RTDL is useful when a workload can be expressed as accelerated search plus exact
refinement. The public authoring target is a 10x reduction in workload-writing
burden: fewer backend-specific files, less duplicated BVH/RT traversal code,
and one stable row-emission model for CPU/oracle, Embree, OptiX, and Vulkan
where the workload/backend pair is supported.

This is a developer-productivity promise, not an automatic speedup promise.
Use release reports for measured performance claims.

## What RTDL Is Today

RTDL is a Python-hosted DSL for non-graphical ray-tracing-style workloads.
The current released state is the bounded `v0.7.0` package. The current `main`
branch also carries accepted `v0.8` app-building work that uses existing RTDL
features plus Python application logic without claiming a new released
language/backend line.

Today it includes:

- a kernel authoring surface
- compiler IR and lowering
- a native C/C++ oracle
- a controlled Embree backend
- a controlled OptiX backend
- a Vulkan backend for supported workload families, with the current performance
  story depending on workload and host configuration

Current supported workload families:

- `lsi`
- `pip`
- `overlay`
- `ray_tri_hitcount`
- `point_nearest_segment`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`
- `bfs`
- `triangle_count`
- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

Current release layers:

- `v0.2.0`: segment/polygon and overlap workload family
- `v0.4.0`: nearest-neighbor workload line
- `v0.5.0`: 3D nearest-neighbor and multi-backend expansion
- `v0.6.1`: corrected RT graph line
- `v0.7.0`: bounded database-style analytical kernel line
- `v0.8`: accepted app-building work on `main` over the released `v0.7.0`
  surface, not a released support-matrix line yet

Plus:

- feature-home docs
- Linux-backed evidence, including PostgreSQL-backed DB correctness and
  repeated-query performance baselines for `v0.7.0`
- Linux-primary validation, with bounded macOS and Windows support depending on
  backend availability
- explicit fallback-vs-native backend boundaries

Current user-programming note:

- RTDL should not be understood only as a fixed workload catalog
- users can already combine RTDL kernels with Python application logic
- current examples of that pattern include:
  - [rtdl_lit_ball_demo.py](../examples/visual_demo/rtdl_lit_ball_demo.py)
  - [rtdl_v0_7_db_app_demo.py](../examples/rtdl_v0_7_db_app_demo.py)
  - [rtdl_hausdorff_distance_app.py](../examples/rtdl_hausdorff_distance_app.py)
  - [rtdl_robot_collision_screening_app.py](../examples/rtdl_robot_collision_screening_app.py)
  - [rtdl_barnes_hut_force_app.py](../examples/rtdl_barnes_hut_force_app.py)
- RTDL provides the query core there, while Python handles application logic and
  output

Current app-building performance note:

- Hausdorff distance has bounded Linux Embree/OptiX/Vulkan performance evidence
  against RTDL and mature nearest-neighbor baselines.
- Robot collision screening has bounded Linux CPU/Embree/OptiX evidence; Vulkan
  is not exposed for that app until the per-edge hit-count mismatch found in
  Goal509 is fixed.
- Barnes-Hut force approximation has bounded Linux CPU/Embree/OptiX/Vulkan
  candidate-generation evidence, but Python still owns the opening rule and
  force reduction. This is not a full N-body acceleration claim.

Canonical app-building docs:

- [v0.8 App Building](tutorials/v0_8_app_building.md)
- [Goal507 Hausdorff Linux Performance Report](reports/goal507_hausdorff_linux_perf_report_2026-04-17.md)
- [Goal509 Robot/Barnes-Hut Linux Performance Report](reports/goal509_robot_barnes_linux_perf_report_2026-04-17.md)

Current workload-maturity note:

- `segment_polygon_hitcount` is the first v0.2 workload-family expansion now
  closed beyond the v0.1 RayJoin-heavy slice
- its current accepted closure target is semantic/backend closure across:
  - `cpu_python_reference`
  - `cpu`
  - `embree`
  - `optix`
  on deterministic authored / fixture / derived cases
- this family must still be described honestly under the current audited local
  `native_loop` boundary rather than as proof of BVH- or RT-core-matured
  traversal
- the family now also has:
  - prepared-path performance characterization
  - large deterministic PostGIS-backed correctness validation on:
    - `cpu`
    - `embree`
    - `optix`
  through the accepted `derived/br_county_subset_segment_polygon_tiled_x256`
  case
- `segment_polygon_anyhit_rows` is the second closed v0.2 segment/polygon family
- the Jaccard line is now real, but only under the narrow pathology/unit-cell
  contract:
  - `polygon_pair_overlap_area_rows`
  - `polygon_set_jaccard`

Canonical workload homes:

- [Release-Facing Examples](release_facing_examples.md)
- [Feature Homes](features/README.md)

## What RTDL Can Currently Do

The current repo can:

- author kernels in a constrained Python DSL
- compile and lower them
- run them through the native CPU/oracle path
- run supported workloads on Embree
- run supported graph and bounded DB workloads on OptiX and Vulkan where the
  host GPU stack and backend libraries are available
- run the released graph workloads `bfs` and `triangle_count`
- run the released bounded DB workloads `conjunctive_scan`, `grouped_count`,
  and `grouped_sum`
- run accepted `v0.8` app-building examples for Hausdorff distance, robot
  collision screening, and Barnes-Hut force approximation, with the app-specific
  backend boundaries documented in the Goal507 and Goal509 reports
- run the current narrow Jaccard line on Python/native CPU with PostGIS-backed
  checking on accepted packages
- run the current narrow Jaccard line through the public `embree`, `optix`,
  and `vulkan` surfaces on Linux under documented native CPU/oracle fallback
- run the accepted long exact-source Vulkan surface with exact parity, while
  keeping Vulkan as the slower portable backend
- support user-authored RTDL-plus-Python applications where RTDL handles the
  geometry-query core and Python handles surrounding application logic
- compare accepted workloads against indexed PostGIS/PostgreSQL ground-truth
  queries on the Linux host
- close bounded four-system checks across PostGIS, native oracle, Embree, and OptiX on accepted packages
- support a RayJoin-oriented experiment/reporting workflow
- preserve bounded older release packages and reports as historical evidence

## What RTDL Cannot Yet Claim

RTDL does not yet claim:

- exact computational geometry
- a finished generalized multi-backend optimizer
- full paper-identical reproduction of every RayJoin dataset family
- high-precision native GPU geometry on Vulkan (the accepted bounded path still
  relies on float32 traversal plus exact host-side final truth)
- that every backend/workload/boundary combination is equally mature
- full polygon overlay materialization (`overlay` is still a seed analogue)
- generic continuous polygon Jaccard or generic continuous overlap-area closure
- native Embree/OptiX/Vulkan Jaccard maturity
- arbitrary SQL execution or DBMS behavior in the `v0.7.0` DB line
- faithful full Barnes-Hut or full N-body solver acceleration
- robot Vulkan support before the Goal509 hit-count parity defect is fixed
- RT-core hardware speedup from the GTX 1070 Linux app evidence
