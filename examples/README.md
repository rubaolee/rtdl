# Examples

This directory contains two kinds of material:

- release-facing examples you can run first
- reference kernels and helper generators used by examples and tests
- preserved generated bundles and generated example output
- internal or historical development artifacts that are kept for auditability

## Start Here

If you are new to RTDL, use these files first:

| If you want to see... | Start with | What data becomes |
| --- | --- | --- |
| the smallest runnable program | `rtdl_hello_world.py` | one script becomes a known output |
| one kernel across backends | `rtdl_hello_world_backends.py` | one query becomes backend-comparable rows |
| one recipe for every feature | `rtdl_feature_quickstart_cookbook.py` | each feature input becomes its expected output rows |
| nearest-neighbor search | `rtdl_fixed_radius_neighbors.py` | points/queries become neighbor rows |
| app-level Hausdorff distance | `rtdl_hausdorff_distance_app.py` | two point sets become directed nearest-neighbor rows and one distance |
| app-level ANN candidate search | `rtdl_ann_candidate_app.py` | queries plus a Python-selected candidate subset become approximate nearest rows |
| app-level outlier detection | `rtdl_outlier_detection_app.py` | points become fixed-radius neighbor rows, reduced density counts, and outlier labels |
| app-level DBSCAN clustering | `rtdl_dbscan_clustering_app.py` | points become fixed-radius neighbor rows, reduced core counts, and density-cluster labels |
| app-level robot collision screening | `rtdl_robot_collision_screening_app.py` | link edge rays become any-hit rows and reduced pose collision flags |
| bounded any-hit ray queries | `rtdl_ray_triangle_any_hit.py` | rays and triangles become per-ray `any_hit` rows |
| visibility / line-of-sight rows | `rtdl_visibility_rows.py` | observers, targets, and blockers become visibility rows |
| emitted-row reductions | `rtdl_reduce_rows.py` | emitted rows become grouped app summary rows |
| app-level Barnes-Hut force approximation | `rtdl_barnes_hut_force_app.py` | bodies and quadtree nodes become force-candidate rows |
| graph traversal | `rtdl_graph_bfs.py` | frontier vertices become discovered vertices |
| graph intersection | `rtdl_graph_triangle_count.py` | graph edges become triangle rows |
| unified graph app | `rtdl_graph_analytics_app.py` | graph inputs become BFS discovery rows and triangle rows |
| DB-style filtering | `rtdl_db_conjunctive_scan.py` | rows plus predicates become matching row IDs |
| DB-style aggregation | `rtdl_db_grouped_count.py` / `rtdl_db_grouped_sum.py` | rows plus predicates become grouped aggregates |
| unified database app | `rtdl_database_analytics_app.py` | order rows become regional dashboard rows and sales-risk summaries |
| app-level road/polygon screening | `rtdl_road_hazard_screening.py` | road segments plus hazard polygons become per-road hit counts |
| spatial join apps | `rtdl_service_coverage_gaps.py`, `rtdl_event_hotspot_screening.py`, `rtdl_facility_knn_assignment.py` | locations become coverage gaps, event hotspots, or nearest facility assignments |
| HIPRT example | `rtdl_hiprt_ray_triangle_hitcount.py` | 3D rays and 3D triangles become per-ray hit-count rows through the prepared HIPRT path |
| unified Apple RT demo | `rtdl_apple_rt_demo_app.py` | Apple closest-hit and visibility-count scenarios become one app JSON result |

- `rtdl_hello_world.py`
- `rtdl_hello_world_backends.py`
- `rtdl_feature_quickstart_cookbook.py`
- `rtdl_fixed_radius_neighbors.py`
- `rtdl_knn_rows.py`
- `rtdl_hausdorff_distance_app.py`
- `rtdl_ann_candidate_app.py`
- `rtdl_outlier_detection_app.py`
- `rtdl_dbscan_clustering_app.py`
- `rtdl_robot_collision_screening_app.py`
- `rtdl_ray_triangle_any_hit.py`
- `rtdl_visibility_rows.py`
- `rtdl_reduce_rows.py`
- `rtdl_barnes_hut_force_app.py`
- `rtdl_graph_bfs.py`
- `rtdl_graph_triangle_count.py`
- `rtdl_graph_analytics_app.py`
- `rtdl_db_conjunctive_scan.py`
- `rtdl_db_grouped_count.py`
- `rtdl_db_grouped_sum.py`
- `rtdl_database_analytics_app.py`
- `rtdl_hiprt_ray_triangle_hitcount.py`
- `rtdl_apple_rt_demo_app.py`
- `rtdl_service_coverage_gaps.py`
- `rtdl_event_hotspot_screening.py`
- `rtdl_facility_knn_assignment.py`
- `rtdl_segment_polygon_hitcount.py`
- `rtdl_segment_polygon_anyhit_rows.py`
- `rtdl_polygon_pair_overlap_area_rows.py`
- `rtdl_polygon_set_jaccard.py`
- `rtdl_road_hazard_screening.py`
- `visual_demo/rtdl_lit_ball_demo.py`
- `visual_demo/rtdl_hidden_star_stable_ball_demo.py`
- `visual_demo/render_hidden_star_chunked_video.py`

## Reference Material

Files under `reference/` contain canonical kernels and helper generators used
by examples, tests, and bounded evaluation paths.

## Generated Material

Files under `generated/` are preserved generated output artifacts. They are
useful for inspection and handoff workflows, but they are not the primary
release-facing start points for new users.

## Internal And Historical Artifacts

Files under `internal/` are preserved for development history, evaluation, or
LLM-authoring experiments. They are not the primary release-facing entry
points for external users.

For release-facing examples and commands, prefer the docs entry points:

- `../README.md`
- `../docs/current_main_support_matrix.md`
- `../docs/application_catalog.md`
- `../docs/app_engine_support_matrix.md`
- `../docs/quick_tutorial.md`
- `../docs/tutorials/README.md`
- `../docs/release_facing_examples.md`

Current DB example boundary:

- examples expose:
  - `cpu_python_reference`
  - `cpu`
  - `embree`
  - `optix`
  - `vulkan`
- `rtdl_database_analytics_app.py` is the single public DB app entry point:
  it unifies the regional dashboard and sales-risk scenarios over the v0.7
  bounded DB workload surface
- `rtdl_v0_7_db_app_demo.py`, `rtdl_v0_7_db_kernel_app_demo.py`, and
  `rtdl_sales_risk_screening.py` remain runnable compatibility helpers, but
  they are retired from the public start-here app list
- PostgreSQL remains a Linux correctness/performance anchor, not a public
  example backend flag

Current v0.8 app example boundary:

- `rtdl_hausdorff_distance_app.py` runs on `cpu_python_reference`, `cpu`,
  `embree`, `optix`, and `vulkan`; Goal507 records bounded Linux performance
  evidence against RTDL and mature nearest-neighbor baselines. The optional
  Embree `--embree-result-mode directed_summary` path computes the directed
  Hausdorff summary in the native Embree traversal path and avoids returning
  all KNN rows when the app only needs distance/witness output. The optional
  OptiX `--optix-summary-mode directed_threshold_prepared` path answers the
  Hausdorff <= radius decision with prepared fixed-radius traversal; it is not
  an exact-distance KNN speedup claim
- `rtdl_ann_candidate_app.py` runs on `cpu_python_reference`, `cpu`, `embree`,
  `optix`, `vulkan`, and optional `scipy`; RTDL emits nearest-neighbor rows
  over a Python-selected approximate candidate set and Python evaluates recall.
  `--output-mode rerank_summary` measures the RTDL candidate-subset reranking
  slice without exact full-set quality comparison or heavy row output;
  `quality_summary` preserves compact recall/distance metrics but remains
  Python exact-comparison dominated. The optional OptiX
  `--optix-summary-mode candidate_threshold_prepared` path answers whether
  every query has at least one Python-selected candidate within a radius using
  prepared fixed-radius traversal; it is not a ranking speedup. This is not a
  full ANN index and it is not an external ANN-baseline speedup
  claim
- `rtdl_outlier_detection_app.py` runs on `cpu_python_reference`, `cpu`,
  `embree`, `optix`, `vulkan`, and optional `scipy`; RTDL emits fixed-radius
  neighbor rows and Python applies a density threshold. Goal524 records bounded Linux CPU/oracle, Embree, OptiX, and Vulkan
  timing characterization for this
  app; it is not a claim against SciPy, scikit-learn, or production anomaly
  detection systems. The optional OptiX `--optix-summary-mode
  rt_count_threshold_prepared` and Embree `--embree-summary-mode
  rt_count_threshold_prepared` paths emit one native fixed-radius threshold
  summary row per query and avoid neighbor-row materialization; Goal715 shows
  this is correctness-useful but not yet a broad Embree performance win for the
  sparse fixture
- `rtdl_dbscan_clustering_app.py` runs on `cpu_python_reference`, `cpu`,
  `embree`, `optix`, `vulkan`, and optional `scipy`; RTDL emits fixed-radius
  neighbor rows and Python expands core, border, and noise labels. Goal524
  records bounded Linux CPU/oracle, Embree, OptiX, and Vulkan timing
  characterization for this app; it is not a claim against scikit-learn DBSCAN
  or production clustering systems. The optional OptiX `--optix-summary-mode
  rt_core_flags_prepared` and Embree `--embree-summary-mode
  rt_core_flags_prepared` paths emit native core flags only; full DBSCAN
  cluster expansion still needs neighbor connectivity and remains Python-owned
- `rtdl_service_coverage_gaps.py` exposes optional Embree
  `--embree-summary-mode gap_summary` for covered/uncovered household
  detection. This mode intentionally omits clinic ids, distances, and
  `clinic_loads`; use row mode for full service-analysis output
- `rtdl_event_hotspot_screening.py` exposes optional Embree
  `--embree-summary-mode count_summary` for per-event neighbor counts and
  hotspot flags without returning all neighbor-pair rows
- `rtdl_facility_knn_assignment.py` keeps full K=3 nearest-depot fallback
  choices in `--output-mode rows`. Its compact `primary_assignments` and
  `summary` modes run a K=1 RTDL KNN kernel when the app only needs primary
  depot assignments or depot-load summaries. The optional OptiX
  `--optix-summary-mode coverage_threshold_prepared` path answers whether
  every customer has at least one depot within a service radius using prepared
  fixed-radius traversal; it is not a ranked-assignment speedup
- `rtdl_robot_collision_screening_app.py` runs on `cpu_python_reference`,
  `cpu`, `embree`, and `optix`; the current app uses `ray_triangle_any_hit`
  plus `rt.reduce_rows(any)` for pose collision flags. `vulkan` is not exposed
  in this app until the app has a dedicated Vulkan parity/performance gate on
  the any-hit formulation. Goal748 supersedes the old Goal509 OptiX robot
  evidence after fixing a short-ray OptiX correctness bug; use Goal748
  post-fix parity/timing for current OptiX robot discussion. Use
  `--output-mode pose_flags` or `--output-mode hit_count` when the app only
  needs compact summaries instead of full per-edge witness rows. On OptiX,
  `--optix-summary-mode prepared_count` returns a native scalar hit-edge
  count, and `--optix-summary-mode prepared_pose_flags` returns native
  pose-level collision flags without edge witnesses.
  `--pose-count` and `--obstacle-count` generate deterministic scaled
  fixtures; Embree scaled `hit_count` is about 2x faster than the CPU Python
  reference on the measured macOS/Linux fixtures, but it still uses the native
  any-hit row path internally rather than a prepared scalar-count ABI
- `rtdl_barnes_hut_force_app.py` runs on `cpu_python_reference`, `cpu`,
  `embree`, `optix`, and `vulkan`; `--body-count` selects a deterministic
  scalable fixture and `--output-mode candidate_summary|force_summary|full`
  separates RTDL candidate-generation timing from Python opening-rule and
  force-reduction timing. Goal734 shows Embree candidate summary is reasonable
  at larger local/Linux scales, but the full force path is still Python
  dominated and is not a fully native Barnes-Hut force engine. The optional
  OptiX `--optix-summary-mode node_coverage_prepared` path answers whether
  every body has at least one quadtree node candidate within the discovery
  radius using prepared fixed-radius traversal; it is not an opening-rule or
  force-vector speedup
- `rtdl_segment_polygon_anyhit_rows.py` keeps full pair-row output in
  `--output-mode rows`. Its compact `segment_flags` and `segment_counts` modes
  use the RTDL `segment_polygon_hitcount` primitive to avoid materializing full
  segment/polygon pair rows when polygon ids are not needed. Explicit
  `--backend optix --output-mode rows --optix-mode native` uses the bounded
  native OptiX pair-row emitter; overflow fails instead of truncating rows, and
  speedup claims still require Goal873 RTX artifact review
- `rtdl_road_hazard_screening.py` keeps full per-road hit-count rows in
  `--output-mode rows`. Its compact `priority_segments` and `summary` modes
  omit full rows from the app JSON payload when only priority road ids or
  aggregate counts are needed
- `rtdl_polygon_pair_overlap_area_rows.py` keeps full per-pair overlap rows in
  `--output-mode rows`. Its compact `summary` mode returns aggregate
  overlap-pair and area totals and omits full per-pair rows from the app JSON
  payload; Embree and OptiX use positive-only LSI/PIP candidate discovery,
  while exact area refinement remains CPU/Python-owned
- `rtdl_polygon_set_jaccard.py` supports `--copies` for scalable Jaccard
  characterization. Embree and OptiX use positive-only LSI/PIP candidate
  discovery and CPU/Python exact set-area refinement; this is native-assisted
  candidate discovery, not a fully native Jaccard kernel

Current HIPRT boundary:

- `rtdl_hiprt_ray_triangle_hitcount.py` runs a 3D ray/triangle hit-count kernel
  through CPU Python reference first, then attempts HIPRT if the Linux HIPRT SDK
  runtime and `build/librtdl_hiprt.so` are available
- the example covers both one-shot `run_hiprt` and repeated-query
  `prepare_hiprt`
- the broader v0.9.0 matrix is larger than this one example: `run_hiprt` has
  Linux parity coverage for 18 workloads; prepared HIPRT reuse is currently
  limited to the paths documented in the v0.9 support matrix
- current `main` additionally exposes
  `prepare_hiprt_ray_triangle_any_hit_2d(...)` for repeated 2D visibility
  apps; current evidence is HIPRT/Orochi CUDA on the Linux NVIDIA host, not
  AMD GPU evidence
- this is not an AMD GPU validation, RT-core speedup claim, CPU fallback, or
  OptiX/Vulkan/HIPRT closest-hit support claim

Current Apple RT boundary:

- `rtdl_apple_rt_demo_app.py` is the single public Apple RT app entry point:
  it runs the closest-hit and visibility-count scenarios through one JSON
  app result
- build it on Apple Silicon macOS with `make build-apple-rt`
- this is the v0.9.1 released native slice: `run_apple_rt` uses Apple Metal/MPS
  RT for `ray_triangle_closest_hit` over 3D rays and 3D triangles
- released v0.9.4 work makes all 18 current predicates callable through
  `run_apple_rt` with explicit native or native-assisted Apple modes
- native Apple execution currently uses MPS RT for supported geometry and
  nearest-neighbor slices, plus Metal compute for bounded DB and graph slices
- Apple DB and graph paths are therefore Apple GPU compute/native-assisted
  paths, not Apple ray-tracing-hardware traversal paths
- prepared closest-hit reuse and masked traversal reduce setup overhead for the
  current Apple ray-intersection slices
- this is not a broad measured Apple speedup claim; Embree remains the mature
  performance baseline
- `rtdl_apple_rt_closest_hit.py` and `rtdl_apple_rt_visibility_count.py`
  remain runnable compatibility helpers, but they are retired from the public
  start-here app list

Current v0.9.6 example boundary:

- `rtdl_ray_triangle_any_hit.py` shows bounded yes/no blocker rows. Native
  early-exit is available on OptiX, Embree, HIPRT, and Vulkan at the released
  `v0.9.6` tag boundary when the backend library exports the relevant symbol.
- `v0.9.6` also has Apple RT native/native-assisted any-hit after rebuilding
  `librtdl_apple_rt` from current source.
- Apple RT 3D uses MPS RT nearest-intersection existence; Apple RT 2D uses
  MPS-prism traversal with per-ray early exit plus exact 2D acceptance. This is
  not programmable shader-level Apple any-hit.
- `rtdl_apple_rt_demo_app.py` demonstrates the released Apple RT closest-hit
  and prepared/prepacked visibility-count app paths. The visibility-count
  scenario is an app-level count contract, not full emitted-row output.
- `v0.9.6` also includes prepared repeated-query 2D any-hit helpers for
  OptiX, HIPRT, and Vulkan. These are performance-oriented backend helpers for
  stable triangle sets and repeated ray batches, not separate beginner example
  files yet and not broad DB/graph/full-row speedup claims.
- `rtdl_visibility_rows.py` shows observer-target line-of-sight rows built on
  any-hit.
- `rtdl_reduce_rows.py` shows deterministic Python standard-library reductions
  over already-emitted RTDL rows; it is not a native backend reduction.
