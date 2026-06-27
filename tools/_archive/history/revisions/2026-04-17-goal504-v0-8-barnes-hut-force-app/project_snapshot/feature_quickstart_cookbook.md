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
| robot link edge rays and obstacle triangles | bounded pose collision flags | `robot_collision_screening_app` |
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

### `robot_collision_screening_app`

- Input: a small discrete pose batch represented as robot link edge rays plus obstacle triangles.
- RTDL output: per-edge `ray_id`, `hit_count` rows.
- Python output: pose-level collision flags and colliding pose IDs.
- Boundary: this is bounded 2D discrete-pose screening, not continuous collision detection, full robot kinematics, or a full mesh collision engine.
- Run:

```bash
PYTHONPATH=src:. python examples/rtdl_robot_collision_screening_app.py --backend cpu_python_reference
```

- Learn from:
  - `examples/rtdl_robot_collision_screening_app.py`
  - [Ray/Triangle Hit Count feature home](../features/ray_tri_hitcount/README.md)

### `barnes_hut_force_app`

- Input: body points with masses plus one-level quadtree nodes built in Python.
- RTDL output: body-to-node candidate rows using `fixed_radius_neighbors`.
- Python output: accepted node IDs, exact fallback body IDs, approximate force vectors, and error against a brute-force oracle.
- Boundary: this is a bounded one-level 2D approximation. RTDL does not yet expose hierarchical tree-node primitives, Barnes-Hut opening predicates, or vector force reductions.
- Run:

```bash
PYTHONPATH=src:. python examples/rtdl_barnes_hut_force_app.py --backend cpu_python_reference
```

- Learn from:
  - `examples/rtdl_barnes_hut_force_app.py`
  - [Nearest-Neighbor Workloads](nearest_neighbor_workloads.md)

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
- Python output: directed and undirected Hausdorff distance scalars plus witness IDs.
- Boundary: this is an app pattern over `knn_rows`, not a new built-in RTDL primitive.
- Run:

```bash
PYTHONPATH=src:. python examples/rtdl_hausdorff_distance_app.py --backend cpu_python_reference
```

- Learn from:
  - [Nearest-Neighbor Workloads](nearest_neighbor_workloads.md)
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
