# RTDL Workload Cookbook

This cookbook provides **copyable workload patterns** for the current RTDL
surface.

Scope of this file:

- one compact example per workload
- required geometry roles
- emitted fields
- quick execution examples

This file is intentionally example-first. It should not duplicate the full
semantic explanations from the programming guide.

For feature-by-feature usage guidance, see:

- [Feature Homes](/Users/rl2025/rtdl_python_only/docs/features/README.md)

## LSI

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def road_boundary_crossings():
    roads = rt.input("roads", rt.Segments, role="probe")
    boundaries = rt.input("boundaries", rt.Segments, role="build")
    candidates = rt.traverse(roads, boundaries, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(
        hits,
        fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
    )
```

Rules:

- both sides are `rt.Segments`
- output is one row per accepted segment intersection

## PIP

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def station_in_districts():
    stations = rt.input("stations", rt.Points, role="probe")
    districts = rt.input("districts", rt.Polygons, role="build")
    candidates = rt.traverse(stations, districts, accel="bvh")
    hits = rt.refine(
        candidates,
        predicate=rt.point_in_polygon(exact=False, boundary_mode="inclusive"),
    )
    return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])
```

Rules:

- probe side must be points
- build side must be polygons
- current boundary mode is only `"inclusive"`

## Overlay

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def parcel_flood_overlay():
    parcels = rt.input("parcels", rt.Polygons, role="probe")
    floodzones = rt.input("floodzones", rt.Polygons, role="build")
    candidates = rt.traverse(parcels, floodzones, accel="bvh")
    seeds = rt.refine(candidates, predicate=rt.overlay_compose())
    return rt.emit(
        seeds,
        fields=["left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"],
    )
```

Rule:

- output is an overlay-seed schema, not final overlay polygons

## Ray/Triangle Hit Count

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def central_ray_triangle_stats():
    rays = rt.input("rays", rt.Rays, role="probe")
    triangles = rt.input("triangles", rt.Triangles, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])
```

## Segment/Polygon Hit Count

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def road_polygon_touch_counts():
    roads = rt.input("roads", rt.Segments, role="probe")
    parcels = rt.input("parcels", rt.Polygons, role="build")
    candidates = rt.traverse(roads, parcels, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_polygon_hitcount(exact=False))
    return rt.emit(hits, fields=["segment_id", "hit_count"])
```

Quick run:

```bash
cd /Users/rl2025/rtdl_python_only
python3 examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 16
```

Notes:

- the current example supports:
  - authored
  - fixture-backed
  - generic deterministic tiled county-derived cases via `--copies`
- the family also has a dedicated PostGIS validation driver:
  - `scripts/goal114_segment_polygon_postgis_validation.py`
- an app-style example now exists here:
  - [rtdl_road_hazard_screening.py](/Users/rl2025/rtdl_python_only/examples/rtdl_road_hazard_screening.py)

App-style run:

```bash
cd /Users/rl2025/rtdl_python_only
python3 examples/rtdl_road_hazard_screening.py --backend cpu_python_reference
```

That example treats the workload as a screening primitive:

- roads are probe segments
- hazard regions are build polygons
- output is one row per road segment with a polygon-hit count
- the example also highlights `priority_segments` with hit count `>= 2`

## Segment/Polygon Any-Hit Rows

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def road_polygon_hits():
    roads = rt.input("roads", rt.Segments, role="probe")
    parcels = rt.input("parcels", rt.Polygons, role="build")
    candidates = rt.traverse(roads, parcels, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_polygon_anyhit_rows(exact=False))
    return rt.emit(hits, fields=["segment_id", "polygon_id"])
```

Quick run:

```bash
cd /Users/rl2025/rtdl_python_only
python3 examples/rtdl_segment_polygon_anyhit_rows.py --backend cpu_python_reference --copies 16
```

Notes:

- this family shares the same geometric hit semantics as `segment_polygon_hitcount`
- the difference is emitted shape:
  - one `(segment_id, polygon_id)` row per true hit
  - no per-segment aggregation
- this is useful when downstream code wants:
  - exact touched polygon ids
  - its own aggregation
  - join-style auditing

## Polygon-Set Jaccard

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def polygon_set_similarity():
    left = rt.input("left", rt.Polygons, role="probe")
    right = rt.input("right", rt.Polygons, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    rows = rt.refine(candidates, predicate=rt.polygon_set_jaccard(exact=False))
    return rt.emit(
        rows,
        fields=["intersection_area", "left_area", "right_area", "union_area", "jaccard_similarity"],
    )
```

Quick run:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 examples/rtdl_polygon_set_jaccard.py
```

Notes:

- this is a narrow pathology-style aggregate workload
- it uses orthogonal integer-grid polygons with unit-cell area semantics
- it is not generic continuous polygon-set Jaccard
- its first public-data audit is based on real MoNuSeg XML converted into this narrower unit-cell contract

## Point/Nearest Segment

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def hydrant_nearest_road():
    hydrants = rt.input("hydrants", rt.Points, role="probe")
    roads = rt.input("roads", rt.Segments, role="build")
    candidates = rt.traverse(hydrants, roads, accel="bvh")
    nearest = rt.refine(candidates, predicate=rt.point_nearest_segment(exact=False))
    return rt.emit(nearest, fields=["point_id", "segment_id", "distance"])
```

## Planned v0.4: Fixed-Radius Neighbors

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def nearby_facilities():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    rows = rt.refine(
        candidates,
        predicate=rt.fixed_radius_neighbors(radius=0.5, k_max=16),
    )
    return rt.emit(rows, fields=["query_id", "neighbor_id", "distance"])
```

Current status:

- contract frozen for `v0.4`
- API surface added
- lowering support added
- runtime support not implemented yet

## Planned v0.4: KNN Rows

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def nearest_facilities():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    rows = rt.refine(
        candidates,
        predicate=rt.knn_rows(k=8),
    )
    return rt.emit(rows, fields=["query_id", "neighbor_id", "distance", "neighbor_rank"])
```

Current status:

- contract frozen for `v0.4`
- API surface added
- lowering support added
- runtime support not implemented yet

## Quick Execution Examples

Oracle:

```python
rows = rt.run_cpu(kernel_fn, **inputs)
```

Embree:

```python
rows = rt.run_embree(kernel_fn, **inputs)
```

OptiX:

```python
rows = rt.run_optix(kernel_fn, **inputs)
```

## Common Mistakes

- wrong geometry roles for `pip`
- unsupported precision modes
- expecting overlay to return final polygon fragments
- treating generated code skeletons as the trusted runtime path

For the precise contract behind these examples, see:

- [DSL Reference](dsl_reference.md)
- [Programming Guide](programming_guide.md)
