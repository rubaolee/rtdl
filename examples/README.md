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
| app-level outlier detection | `rtdl_outlier_detection_app.py` | points become fixed-radius neighbor rows and density-threshold outlier labels |
| app-level DBSCAN clustering | `rtdl_dbscan_clustering_app.py` | points become fixed-radius neighbor rows and density-cluster labels |
| app-level robot collision screening | `rtdl_robot_collision_screening_app.py` | link edge rays become pose collision flags |
| app-level Barnes-Hut force approximation | `rtdl_barnes_hut_force_app.py` | bodies and quadtree nodes become force-candidate rows |
| graph traversal | `rtdl_graph_bfs.py` | frontier vertices become discovered vertices |
| graph intersection | `rtdl_graph_triangle_count.py` | graph edges become triangle rows |
| DB-style filtering | `rtdl_db_conjunctive_scan.py` | rows plus predicates become matching row IDs |
| DB-style aggregation | `rtdl_db_grouped_count.py` / `rtdl_db_grouped_sum.py` | rows plus predicates become grouped aggregates |
| app-level use | `rtdl_v0_7_db_app_demo.py` | a Python app delegates the query core to RTDL |
| HIPRT example | `rtdl_hiprt_ray_triangle_hitcount.py` | 3D rays and 3D triangles become per-ray hit-count rows through the prepared HIPRT path |
| Apple RT example | `rtdl_apple_rt_closest_hit.py` | 3D rays and 3D triangles become nearest-hit rows through the Apple Metal/MPS path |

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
- `rtdl_barnes_hut_force_app.py`
- `rtdl_graph_bfs.py`
- `rtdl_graph_triangle_count.py`
- `rtdl_db_conjunctive_scan.py`
- `rtdl_db_grouped_count.py`
- `rtdl_db_grouped_sum.py`
- `rtdl_v0_7_db_app_demo.py`
- `rtdl_v0_7_db_kernel_app_demo.py`
- `rtdl_hiprt_ray_triangle_hitcount.py`
- `rtdl_apple_rt_closest_hit.py`
- `rtdl_sales_risk_screening.py`
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
- `rtdl_v0_7_db_app_demo.py` is the app-level demo: it shows one
  denormalized order table becoming matched row IDs, grouped counts, and
  grouped sums through the v0.7 bounded DB workload surface
- `rtdl_v0_7_db_kernel_app_demo.py` is the kernel-form companion demo: it
  shows `rt.input(..., role="probe")`, `rt.input(..., role="build")`,
  `rt.traverse(..., accel="bvh")`, `rt.refine(...)`, and `rt.emit(...)` around
  the same bounded DB workload surface
- PostgreSQL remains a Linux correctness/performance anchor, not a public
  example backend flag

Current v0.8 app example boundary:

- `rtdl_hausdorff_distance_app.py` runs on `cpu_python_reference`, `cpu`,
  `embree`, `optix`, and `vulkan`; Goal507 records bounded Linux performance
  evidence against RTDL and mature nearest-neighbor baselines
- `rtdl_ann_candidate_app.py` runs on `cpu_python_reference`, `cpu`, `embree`,
  `optix`, `vulkan`, and optional `scipy`; RTDL emits nearest-neighbor rows
  over a Python-selected approximate candidate set and Python evaluates recall.
  Goal524 records bounded Linux CPU/oracle, Embree, OptiX, and Vulkan timing
  characterization for this app; it is not an external ANN-baseline speedup
  claim
- `rtdl_outlier_detection_app.py` runs on `cpu_python_reference`, `cpu`,
  `embree`, `optix`, `vulkan`, and optional `scipy`; RTDL emits fixed-radius
  neighbor rows and Python applies a density threshold. Goal524 records bounded
  Linux CPU/oracle, Embree, OptiX, and Vulkan timing characterization for this
  app; it is not a claim against SciPy, scikit-learn, or production anomaly
  detection systems
- `rtdl_dbscan_clustering_app.py` runs on `cpu_python_reference`, `cpu`,
  `embree`, `optix`, `vulkan`, and optional `scipy`; RTDL emits fixed-radius
  neighbor rows and Python expands core, border, and noise labels. Goal524
  records bounded Linux CPU/oracle, Embree, OptiX, and Vulkan timing
  characterization for this app; it is not a claim against scikit-learn DBSCAN
  or production clustering systems
- `rtdl_robot_collision_screening_app.py` runs on `cpu_python_reference`,
  `cpu`, `embree`, and `optix`; `vulkan` is intentionally not exposed because
  Goal509 found a per-edge hit-count parity mismatch for this app
- `rtdl_barnes_hut_force_app.py` runs on `cpu_python_reference`, `cpu`,
  `embree`, `optix`, and `vulkan`; Goal509 records candidate-generation timing
  separately from Python force-reduction timing

Current HIPRT boundary:

- `rtdl_hiprt_ray_triangle_hitcount.py` runs a 3D ray/triangle hit-count kernel
  through CPU Python reference first, then attempts HIPRT if the Linux HIPRT SDK
  runtime and `build/librtdl_hiprt.so` are available
- the example covers both one-shot `run_hiprt` and repeated-query
  `prepare_hiprt`
- the broader v0.9.0 matrix is larger than this one example: `run_hiprt` has
  Linux parity coverage for 18 workloads; prepared HIPRT reuse is currently
  limited to the paths documented in the v0.9 support matrix
- this is not an AMD GPU validation, RT-core speedup claim, CPU fallback, or
  OptiX/Vulkan/HIPRT closest-hit support claim

Current Apple RT boundary:

- `rtdl_apple_rt_closest_hit.py` runs a 3D ray/triangle closest-hit kernel
  through CPU Python reference first, then attempts Apple RT if the macOS
  `build/librtdl_apple_rt.dylib` library is available
- build it on Apple Silicon macOS with `make build-apple-rt`
- this is the v0.9.1 released native slice: `run_apple_rt` uses Apple Metal/MPS
  RT for `ray_triangle_closest_hit` over 3D rays and 3D triangles
- current v0.9.4 target work makes all 18 current predicates callable through
  `run_apple_rt` with explicit native or native-assisted Apple modes
- native Apple execution currently uses MPS RT for supported geometry and
  nearest-neighbor slices, plus Metal compute for bounded DB and graph slices
- prepared closest-hit reuse and masked traversal reduce setup overhead for the
  current Apple ray-intersection slices
- this is not a broad measured Apple speedup claim; Embree remains the mature
  performance baseline
