# Feature Quickstart Cookbook

This cookbook is the shortest path from "what feature should I use?" to "what
data becomes what output?"

It complements the longer tutorials:

- [Quick Tutorial](../quick_tutorial.md) teaches the kernel shape.
- [Tutorials](README.md) teach major workload families.
- This cookbook gives one compact recipe per current public feature.

Run the companion example first:

```bash
PYTHONPATH=src:. python examples/rtdl_feature_quickstart_cookbook.py
```

The command uses `cpu_python_reference` so it is portable and easy to inspect.
Use feature homes and support matrices before making backend or performance
claims.

## Choosing A Feature

| If your data is... | And you want... | Use |
| --- | --- | --- |
| segments and segments | crossing/intersection rows | `lsi` |
| points and polygons | containment rows | `pip` |
| polygons and polygons | overlap seed rows for later exact work | `overlay` |
| rays and triangles | per-ray hit counts | `ray_tri_hitcount` |
| robot link edge rays and obstacle triangles | any-hit rows reduced to bounded pose collision flags | `robot_collision_screening_app` |
| bodies and Python-built quadtree nodes | approximate force vectors | `barnes_hut_force_app` |
| points and segments | nearest segment and distance rows | `point_nearest_segment` |
| segments and polygons | per-segment hit counts | `segment_polygon_hitcount` |
| segments and polygons | segment/polygon hit rows | `segment_polygon_anyhit_rows` |
| polygon pairs | bounded overlap-area rows | `polygon_pair_overlap_area_rows` |
| two polygon sets | bounded set-level Jaccard row | `polygon_set_jaccard` |
| query points and search points | neighbors within a radius | `fixed_radius_neighbors` |
| query points and search points | ranked nearest-neighbor rows | `knn_rows` |
| two point sets | directed nearest-neighbor rows reduced to a Hausdorff scalar | `hausdorff_distance_app` |
| graph frontier and graph CSR | one BFS expansion step | `bfs` |
| graph seed edges and graph CSR | triangle rows | `triangle_count` |
| rows and predicates | matching row IDs | `conjunctive_scan` |
| rows, predicates, group key | grouped counts | `grouped_count` |
| rows, predicates, group key, value field | grouped sums | `grouped_sum` |

## Recipes

### `lsi`

- Input: two segment sets.
- Output: rows with `left_id`, `right_id`, and intersection point fields.
- Kernel predicate: `rt.segment_intersection(exact=False)`.
- Learn from:
  - [LSI feature home](../features/lsi/README.md)
  - `examples/rtdl_feature_quickstart_cookbook.py`

### `pip`

- Input: points as probe data and polygons as build data.
- Output: containment rows with `point_id`, `polygon_id`, and `contains`.
- Kernel predicate: `rt.point_in_polygon(exact=False, boundary_mode="inclusive")`.
- Learn from:
  - [PIP feature home](../features/pip/README.md)
  - `examples/rtdl_feature_quickstart_cookbook.py`

### `overlay`

- Input: two polygon sets.
- Output: overlap seed rows with `requires_lsi` and `requires_pip` flags.
- Kernel predicate: `rt.overlay_compose()`.
- Boundary: this is not full polygon overlay materialization.
- Learn from:
  - [Overlay feature home](../features/overlay/README.md)
  - `examples/rtdl_feature_quickstart_cookbook.py`

### `ray_tri_hitcount`

- Input: rays and triangles.
- Output: one `hit_count` per ray.
- Kernel predicate: `rt.ray_triangle_hit_count(exact=False)`.
- Learn from:
  - [Ray/Triangle Hit Count feature home](../features/ray_tri_hitcount/README.md)
  - `examples/rtdl_feature_quickstart_cookbook.py`
  - [RTDL Plus Python Rendering](rendering_and_visual_demos.md)

### `ray_tri_anyhit`

- Input: rays and triangles.
- Output: one `any_hit` boolean row per ray.
- Kernel predicate: `rt.ray_triangle_any_hit(exact=False)`.
- Best fit: blocker, shadow, line-of-sight, and collision yes/no queries where
  counting every hit is unnecessary.
- Learn from:
  - [Ray/Triangle Any Hit feature home](../features/ray_tri_anyhit/README.md)
  - `examples/rtdl_ray_triangle_any_hit.py`

### `visibility_rows`

- Input: observer points, target points, and blocker triangles.
- Output: `{observer_id, target_id, visible}` rows.
- Standard-library helpers: `rt.visibility_rows_cpu(observers, targets, blockers)`
  for the CPU oracle, or `rt.visibility_rows(..., backend="embree" | "optix" |
  "vulkan" | "hiprt" | "apple_rt")` for backend dispatch.
- Boundary: OptiX, Embree, and HIPRT use native any-hit when available; Vulkan
  and Apple RT currently use compatibility dispatch and should not be described
  as native early-exit speedup paths.
- Learn from:
  - [Visibility Rows feature home](../features/visibility_rows/README.md)
  - `examples/rtdl_visibility_rows.py`

### `reduce_rows`

- Input: rows already emitted by RTDL kernels or standard-library helpers.
- Output: deterministic grouped app summary rows.
- Standard-library helper: `rt.reduce_rows(rows, group_by=..., op=..., value=...)`.
- Supported operations: `any`, `count`, `sum`, `min`, and `max`.
- Boundary: this is a Python helper over emitted rows, not a native RT backend
  reduction or speedup claim.
- Run:

```bash
PYTHONPATH=src:. python examples/rtdl_reduce_rows.py
```

- Learn from:
  - [Reduce Rows feature home](../features/reduce_rows/README.md)
  - `examples/rtdl_reduce_rows.py`

### `robot_collision_screening_app`

- Input: a small discrete pose batch represented as robot link edge rays plus obstacle triangles.
- RTDL output: per-edge `ray_id`, `any_hit` rows.
- Standard-library helper: `rt.reduce_rows(any)` converts per-edge rows into pose-level collision flags.
- Python output: colliding pose IDs plus witness edge/ray summaries.
- Boundary: this is bounded 2D discrete-pose screening, not continuous collision detection, full robot kinematics, or a full mesh collision engine.
- Linux performance evidence: Goal509 accepts CPU, Embree, and OptiX for this
  app on the earlier hit-count formulation; v0.9.5 rewrites the app to any-hit
  plus `reduce_rows` without making a new Vulkan or Apple native early-exit
  speedup claim.
- Run:

```bash
PYTHONPATH=src:. python examples/rtdl_robot_collision_screening_app.py --backend cpu_python_reference
```

- Learn from:
  - `examples/rtdl_robot_collision_screening_app.py`
  - [Ray/Triangle Any Hit feature home](../features/ray_tri_anyhit/README.md)
  - [Reduce Rows feature home](../features/reduce_rows/README.md)
  - [Goal509 Robot/Barnes-Hut Linux Performance Report](../reports/goal509_robot_barnes_linux_perf_report_2026-04-17.md)

### `barnes_hut_force_app`

- Input: body points with masses plus one-level quadtree nodes built in Python.
- RTDL output: body-to-node candidate rows using `fixed_radius_neighbors`.
- Python output: accepted node IDs, exact fallback body IDs, approximate force vectors, and error against a brute-force oracle.
- Boundary: this is a bounded one-level 2D approximation. RTDL does not yet expose hierarchical tree-node primitives, Barnes-Hut opening predicates, or vector force reductions.
- Linux performance evidence: Goal509 accepts CPU, Embree, OptiX, and Vulkan
  for candidate generation, but full-app timing remains dominated by Python
  opening-rule and force-reduction work.
- Run:

```bash
PYTHONPATH=src:. python examples/rtdl_barnes_hut_force_app.py --backend cpu_python_reference
```

- Learn from:
  - `examples/rtdl_barnes_hut_force_app.py`
  - [Nearest-Neighbor Workloads](nearest_neighbor_workloads.md)
  - [Goal509 Robot/Barnes-Hut Linux Performance Report](../reports/goal509_robot_barnes_linux_perf_report_2026-04-17.md)

### `point_nearest_segment`

- Input: points and segments.
- Output: `point_id`, nearest `segment_id`, and `distance`.
- Kernel predicate: `rt.point_nearest_segment(exact=False)`.
- Learn from:
  - [Point/Nearest Segment feature home](../features/point_nearest_segment/README.md)
  - `examples/rtdl_feature_quickstart_cookbook.py`

### `segment_polygon_hitcount`

- Input: segments and polygons.
- Output: one hit-count row per segment.
- Run:

```bash
PYTHONPATH=src:. python examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 16
```

- Learn from:
  - [Segment/Polygon Workloads](segment_polygon_workloads.md)
  - [Segment/Polygon Hit Count feature home](../features/segment_polygon_hitcount/README.md)

### `segment_polygon_anyhit_rows`

- Input: segments and polygons.
- Output: one row per accepted segment/polygon hit.
- Run:

```bash
PYTHONPATH=src:. python examples/rtdl_segment_polygon_anyhit_rows.py --backend cpu_python_reference
```

- Learn from:
  - [Segment/Polygon Workloads](segment_polygon_workloads.md)
  - [Segment/Polygon Any-Hit Rows feature home](../features/segment_polygon_anyhit_rows/README.md)

### `polygon_pair_overlap_area_rows`

- Input: left and right polygon sets.
- Output: pairwise rows with intersection, union, and input-area fields.
- Run:

```bash
PYTHONPATH=src:. python examples/rtdl_polygon_pair_overlap_area_rows.py
```

- Learn from:
  - [Polygon-Pair Overlap Area Rows feature home](../features/polygon_pair_overlap_area_rows/README.md)

### `polygon_set_jaccard`

- Input: two polygon sets.
- Output: one bounded set-level Jaccard row.
- Run:

```bash
PYTHONPATH=src:. python examples/rtdl_polygon_set_jaccard.py
```

- Learn from:
  - [Polygon-Set Jaccard feature home](../features/polygon_set_jaccard/README.md)

### `fixed_radius_neighbors`

- Input: query points, search points, radius, and `k_max`.
- Output: neighbor rows within the radius.
- Run:

```bash
PYTHONPATH=src:. python examples/rtdl_fixed_radius_neighbors.py --backend cpu_python_reference
```

- Learn from:
  - [Nearest-Neighbor Workloads](nearest_neighbor_workloads.md)
  - [Fixed-Radius Neighbors feature home](../features/fixed_radius_neighbors/README.md)

### `knn_rows`

- Input: query points, search points, and `k`.
- Output: ranked nearest-neighbor rows.
- Run:

```bash
PYTHONPATH=src:. python examples/rtdl_knn_rows.py --backend cpu_python_reference
```

- Learn from:
  - [Nearest-Neighbor Workloads](nearest_neighbor_workloads.md)
  - [KNN Rows feature home](../features/knn_rows/README.md)

### `hausdorff_distance_app`

- Input: two point sets.
- RTDL output: k=1 nearest-neighbor rows in both directions.
- Standard-library helper: `rt.reduce_rows(max)` computes directed Hausdorff distance scalars.
- Python output: undirected distance selection plus witness IDs.
- Boundary: this is an app pattern over `knn_rows`, not a new built-in RTDL primitive.
- Linux performance evidence: Goal507 covers Embree, OptiX, Vulkan, SciPy
  `cKDTree`, scikit-learn `NearestNeighbors`, and FAISS `IndexFlatL2`; the
  honest result is that RTDL GPU backends beat RTDL Embree, but do not beat the
  strongest mature nearest-neighbor library baselines on the measured exact 2D
  task.
- Run:

```bash
PYTHONPATH=src:. python examples/rtdl_hausdorff_distance_app.py --backend cpu_python_reference
```

- Learn from:
  - [Nearest-Neighbor Workloads](nearest_neighbor_workloads.md)
  - [Goal507 Hausdorff Linux Performance Report](../reports/goal507_hausdorff_linux_perf_report_2026-04-17.md)
  - `examples/rtdl_hausdorff_distance_app.py`

### `bfs`

- Input: frontier vertices, graph CSR, and visited set.
- Output: newly discovered vertex rows for one bounded expansion step.
- Run:

```bash
PYTHONPATH=src:. python examples/rtdl_graph_bfs.py --backend cpu_python_reference
```

- Learn from:
  - [Graph Workloads](graph_workloads.md)

### `triangle_count`

- Input: seed edges and graph CSR.
- Output: triangle rows.
- Run:

```bash
PYTHONPATH=src:. python examples/rtdl_graph_triangle_count.py --backend cpu_python_reference
```

- Learn from:
  - [Graph Workloads](graph_workloads.md)

### `conjunctive_scan`

- Input: denormalized rows plus predicates.
- Output: matching `row_id` rows.
- Run:

```bash
PYTHONPATH=src:. python examples/rtdl_db_conjunctive_scan.py --backend cpu_python_reference
```

- Learn from:
  - [Database Workloads](db_workloads.md)
  - [Database Workloads feature home](../features/db_workloads/README.md)

### `grouped_count`

- Input: denormalized rows, predicates, and one group key.
- Output: grouped count rows.
- Run:

```bash
PYTHONPATH=src:. python examples/rtdl_db_grouped_count.py --backend cpu_python_reference
```

- Learn from:
  - [Database Workloads](db_workloads.md)
  - [Database Workloads feature home](../features/db_workloads/README.md)

### `grouped_sum`

- Input: denormalized rows, predicates, one group key, and one value field.
- Output: grouped sum rows.
- Run:

```bash
PYTHONPATH=src:. python examples/rtdl_db_grouped_sum.py --backend cpu_python_reference
```

- Learn from:
  - [Database Workloads](db_workloads.md)
  - [Database Workloads feature home](../features/db_workloads/README.md)

## Backend Boundary

The cookbook teaches feature shape through `cpu_python_reference`. That path is
for learning and row-shape inspection, not performance claims.

For backend status, use:

- [Current Architecture](../current_architecture.md)
- [v0.7 Support Matrix](../release_reports/v0_7/support_matrix.md)
- [Release-Facing Examples](../release_facing_examples.md)
