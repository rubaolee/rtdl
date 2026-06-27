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

### Unsupported Emit Schema

Bad:

```python
return rt.emit(hits, fields=["point_id", "bbox_min_x"])
```

Why it fails:

- emit fields are workload-specific and closed in the current language
