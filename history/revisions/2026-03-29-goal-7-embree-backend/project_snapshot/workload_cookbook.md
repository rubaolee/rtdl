# RTDL Workload Cookbook

This cookbook gives copyable RTDL examples for the currently supported workload
families.

## LSI Example

```python
import rtdsl as rt

@rt.kernel(backend="rayjoin", precision="float_approx")
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

Notes:

- both inputs must be `rt.Segments`
- current lowering requires `exact=False`

## PIP Example

```python
import rtdsl as rt

@rt.kernel(backend="rayjoin", precision="float_approx")
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

Notes:

- probe must be points
- build must be polygons
- boundary mode must currently stay `"inclusive"`

## Overlay Example

```python
import rtdsl as rt

@rt.kernel(backend="rayjoin", precision="float_approx")
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

Notes:

- both inputs must be polygons
- current result is an overlay seed schema, not a final polygon overlay mesh

## Ray/Triangle Hit Count Example

```python
import rtdsl as rt

@rt.kernel(backend="rayjoin", precision="float_approx")
def central_ray_triangle_stats():
    rays = rt.input("rays", rt.Rays, role="probe")
    triangles = rt.input("triangles", rt.Triangles, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])
```

Notes:

- rays are finite, not infinite
- triangles are explicit 2D primitives in the current surface
- current result is one record per ray with its total triangle hit count

Typical use:

- generate many random triangles
- generate many rays from a center point with random angles and lengths
- compile the RTDL kernel and collect per-ray counts

## Local Simulator Example

RTDL now has a CPU simulator for the currently supported workloads:

```python
rows = rt.run_cpu(
    central_ray_triangle_stats,
    rays=(
        {"id": 1, "ox": 0.0, "oy": 0.0, "dx": 1.0, "dy": 0.0, "tmax": 10.0},
    ),
    triangles=(
        {"id": 10, "x0": 2.0, "y0": -1.0, "x1": 3.0, "y1": 1.0, "x2": 4.0, "y2": -1.0},
    ),
)
```

Notes:

- this is for correctness/debugging, not performance
- results come from the Python CPU reference semantics
- polygon inputs in simulator mode should use inline `vertices`

## Embree Backend Example

```python
rows = rt.run_embree(
    central_ray_triangle_stats,
    rays=(
        {"id": 1, "ox": 0.0, "oy": 0.0, "dx": 1.0, "dy": 0.0, "tmax": 10.0},
    ),
    triangles=(
        {"id": 10, "x0": 2.0, "y0": -1.0, "x1": 3.0, "y1": 1.0, "x2": 4.0, "y2": -1.0},
    ),
)
```

Notes:

- install Embree first with `brew install embree`
- current local setup expects Homebrew Embree in `/opt/homebrew/opt/embree`
- on non-default installs, set `RTDL_EMBREE_PREFIX` and optionally `RTDL_TBB_PREFIX`
- `run_embree(...)` supports the same current workload surface as `run_cpu(...)`
- use `run_cpu(...)` as the baseline when validating new kernels or backend changes

## Common Errors

### Wrong Precision

Bad:

```python
@rt.kernel(backend="rayjoin", precision="exact")
```

Why it fails:

- the current lowering rejects anything except `float_approx`

### Wrong PIP Geometry Order

Bad:

```python
left = rt.input("left", rt.Segments)
right = rt.input("right", rt.Polygons)
hits = rt.refine(candidates, predicate=rt.point_in_polygon(exact=False))
```

Why it fails:

- PIP requires polygon build plus point probe

### Wrong Ray/Triangle Geometry Pair

Bad:

```python
rays = rt.input("rays", rt.Rays, role="build")
triangles = rt.input("triangles", rt.Triangles, role="probe")
hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
```

Why it fails:

- current lowering requires triangle build plus ray probe

### Unsupported Emit Schema

Bad:

```python
return rt.emit(hits, fields=["point_id", "bbox_min_x"])
```

Why it fails:

- emit fields are workload-specific and closed in the current language
