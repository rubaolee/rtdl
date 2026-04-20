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
and one stable row-emission model for CPU/oracle, Embree, OptiX, Vulkan,
HIPRT, and Apple RT where the workload/backend pair is supported.

This is a developer-productivity promise, not an automatic speedup promise.
Use release reports and [Backend Maturity](backend_maturity.md) for measured
performance claims.

## What RTDL Is Today

RTDL is a Python-hosted DSL for non-graphical ray-tracing-style workloads.
The current released state is `v0.9.5`: the bounded `v0.7.0` DB package, the
released `v0.8.0` app-building layer that uses existing RTDL features with
Python application logic, the released `v0.9.0` HIPRT / closest-hit expansion,
the released `v0.9.1` Apple RT closest-hit slice, the released `v0.9.4`
Apple RT consolidation, and the released `v0.9.5` any-hit / visibility-row /
emitted-row reduction layer.

The released `v0.9.1` line adds an Apple RT slice:
`run_apple_rt` for 3D `ray_triangle_closest_hit` through Apple Metal/MPS on the
local Apple M4 host.

The untagged `v0.9.2` Apple RT candidate and `v0.9.3` native-coverage
milestone are internal evidence lines absorbed into `v0.9.4`, not separate
public releases. The released `v0.9.4` line combines full-surface
`run_apple_rt` compatibility,
prepared closest-hit reuse, masked traversal work, expanded Apple MPS RT
geometry/native-assisted slices, and Apple Metal compute DB/graph slices.

Today it includes:

- a kernel authoring surface
- compiler IR and lowering
- a native C/C++ oracle
- a controlled Embree backend
- a controlled OptiX backend
- a Vulkan backend for supported workload families, with the current performance
  story depending on workload and host configuration
- a released `v0.9.0` HIPRT backend with Linux `run_hiprt` parity coverage for
  the current 18-workload HIPRT matrix
- a released `v0.9.1` Apple RT backend slice for 3D closest-hit ray/triangle
  traversal on macOS Apple Silicon
- a released `v0.9.4` Apple RT line with all 18 current predicates callable
  through explicit native or native-assisted Apple modes
- native Apple MPS RT coverage for supported geometry and nearest-neighbor
  slices
- Apple Metal compute/native-assisted coverage for bounded DB and graph slices
- Apple RT prepared/masked performance improvements for the current ray
  intersection slices after Goals596-598
- bounded `ray_triangle_any_hit` rows, with native early-exit implementations
  on OptiX, Embree, and HIPRT and compatibility projection on Vulkan and Apple
  RT
- `visibility_rows_cpu` and `visibility_rows` helpers that turn
  observer-target pairs into finite any-hit rays and emit line-of-sight rows
- `reduce_rows` as a deterministic Python standard-library helper for
  reducing emitted RTDL rows by `any`, `count`, `sum`, `min`, or `max`

Backend maturity note: Embree is currently the only backend RTDL should call
optimized or mature in public performance-facing claims. OptiX, Vulkan, HIPRT,
and Apple Metal/MPS RT are real backend integrations with bounded correctness
evidence, but they are not broad optimized-backend claims. Apple Metal/MPS RT
now has local overhead reductions for prepared closest-hit, hit-count, and
segment-intersection, plus v0.9.4 Metal compute DB/graph coverage, but still is
not a broad Apple speedup claim.

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
- `v0.8.0`: released app-building work on `main` over the released `v0.7.0`
  surface
- `v0.9.0`: released HIPRT backend and exact bounded closest-hit expansion
- `v0.9.1`: released Apple Metal/MPS RT backend slice for closest-hit
- `v0.9.4`: full-surface Apple RT dispatch with
  native/native-assisted geometry, nearest-neighbor, DB, and graph slices,
  absorbing the internal v0.9.2/v0.9.3 evidence lines
- `v0.9.5`: bounded any-hit / visibility-row / emitted-row reduction surface;
  native any-hit early-exit is implemented for OptiX, Embree, and HIPRT, while
  Vulkan and Apple RT remain compatibility paths for this feature

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
  - [rtdl_ann_candidate_app.py](../examples/rtdl_ann_candidate_app.py)
  - [rtdl_outlier_detection_app.py](../examples/rtdl_outlier_detection_app.py)
  - [rtdl_dbscan_clustering_app.py](../examples/rtdl_dbscan_clustering_app.py)
  - [rtdl_robot_collision_screening_app.py](../examples/rtdl_robot_collision_screening_app.py)
  - [rtdl_barnes_hut_force_app.py](../examples/rtdl_barnes_hut_force_app.py)
- the released `v0.9.0` line also includes an exact bounded RTXRMQ-style
  range-minimum-query gate using `ray_triangle_closest_hit` on CPU reference,
  `run_cpu`, and Embree; the released `v0.9.1` Apple RT slice exposes
  the same primitive for 3D rays/triangles through `run_apple_rt`; OptiX,
  Vulkan, and HIPRT do not yet expose this closest-hit primitive
- released `v0.9.4` Goals582-620 let users call the current 18-predicate
  workload surface through `run_apple_rt` with explicit native or
  native-assisted modes; geometry/nearest-neighbor slices use Apple MPS RT,
  while bounded DB and graph slices use Apple Metal compute with disclosed CPU
  refinement/aggregation/materialization where needed
- RTDL provides the query core there, while Python handles application logic and
  output
- the released `v0.9.5` line adds reusable app-building pieces:
  `ray_triangle_any_hit`, `visibility_rows`, and `reduce_rows`; `reduce_rows`
  improves app ergonomics but is not a backend-native reduction or speedup
  claim

Current app-building performance note:

- Hausdorff distance has bounded Linux Embree/OptiX/Vulkan performance evidence
  against RTDL and mature nearest-neighbor baselines.
- ANN candidate search, outlier detection, and DBSCAN clustering are current
  Goal519 Stage-1 proximity apps over existing `knn_rows` and
  `fixed_radius_neighbors`; Goal524 now gives bounded Linux CPU/oracle,
  Embree, OptiX, and Vulkan timing characterization for them.
  This is not an external-baseline speedup claim; SciPy was not installed in
  that validation checkout, and no claim is made against SciPy, scikit-learn,
  FAISS, or production ANN/clustering systems.
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
- [Goal524 Stage-1 Proximity Linux Performance Report](reports/goal524_v0_8_stage1_proximity_linux_perf_2026-04-17.md)

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
- run accepted `v0.8` app-building examples for Hausdorff distance, ANN
  candidate search, outlier detection, DBSCAN clustering, robot collision
  screening, and Barnes-Hut force approximation, with the app-specific backend
  boundaries documented in the Goal507, Goal509, and Goal524 reports
- run the current narrow Jaccard line on Python/native CPU with PostGIS-backed
  checking on accepted packages
- run the current narrow Jaccard line through the public `embree`, `optix`,
  and `vulkan` surfaces on Linux under documented native CPU/oracle fallback
- run the accepted long exact-source Vulkan surface with exact parity, while
  keeping Vulkan as the slower portable backend
- support user-authored RTDL-plus-Python applications where RTDL handles the
  geometry-query core and Python handles surrounding application logic
- run the released HIPRT matrix through `run_hiprt` when the Linux HIPRT SDK
  runtime is available; `prepare_hiprt` currently covers prepared 3D
  ray/triangle hit-count, prepared 3D fixed-radius nearest-neighbor, and
  prepared graph CSR paths, plus prepared bounded DB table reuse
- run the v0.9.1 Apple RT closest-hit path on macOS Apple Silicon
  after `make build-apple-rt`
- run the released v0.9.4 Apple RT surface on macOS Apple Silicon, while
  using `native_only=True` when an app must reject unsupported shape/backend
  combinations; current Apple modes include MPS RT geometry/nearest-neighbor
  slices and Metal compute/native-assisted DB/graph slices
- run the released v0.9.5 bounded any-hit and visibility helpers; OptiX,
  Embree, and HIPRT use native early-exit traversal, while Vulkan and Apple RT
  expose compatibility dispatch without a native early-exit performance claim
- reduce already-emitted RTDL rows in Python with `rt.reduce_rows(...)`
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
- AMD GPU HIPRT validation, HIPRT CPU fallback, HIPRT RT-core speedup evidence,
  or OptiX/Vulkan/HIPRT native support for `ray_triangle_closest_hit`
- broad Apple hardware speedup evidence or Apple backend maturity beyond the
  current bounded native/native-assisted support matrix
