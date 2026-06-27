# RTDL Programming Guide

This guide explains how to write RTDL kernels correctly for the current language
surface.

## 1. Start With The Kernel Header

Every RTDL kernel starts with:

```python
@rt.kernel(backend="rayjoin", precision="float_approx")
```

Do not vary these values in the current implementation.

Also:

- the kernel function takes no Python arguments
- the body should only use RTDL operations

## 2. Declare Inputs First

Inputs come first and should be given clear domain names:

```python
roads = rt.input("roads", rt.Segments, role="probe")
boundaries = rt.input("boundaries", rt.Segments, role="build")
```

Recommendations:

- use explicit roles
- keep the Python variable name aligned with the input name string
- use built-in geometry types unless a custom layout is necessary

## 3. Add Traversal

Current RTDL only supports BVH traversal:

```python
candidates = rt.traverse(roads, boundaries, accel="bvh")
```

## 4. Add Refinement

Choose one supported predicate.

### For LSI

```python
hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
```

### For PIP

```python
hits = rt.refine(
    candidates,
    predicate=rt.point_in_polygon(exact=False, boundary_mode="inclusive"),
)
```

### For Overlay

```python
seeds = rt.refine(candidates, predicate=rt.overlay_compose())
```

### For Ray/Triangle Hit Count

```python
hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
```

## 5. Return Emit

The kernel must end with `return rt.emit(...)`.

```python
return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])
```

## What RTDL Is Not

RTDL is not currently an imperative per-element kernel language.

Do not write:

- `for` loops over inputs
- mutable local accumulators as part of the DSL
- typed kernel arguments like `ray: rt.Ray2D`
- user-written calls like `rt.intersect(...)`
- output objects like `rt.Output[...]`

## Choosing Layouts

Use the default layouts unless you need to be explicit in docs or tests.

Built-in defaults:

- `rt.Segment2DLayout`
- `rt.Point2DLayout`
- `rt.Polygon2DLayout`
- `rt.Triangle2DLayout`
- `rt.Ray2DLayout`

If you write a custom layout, it must still include the required fields for the
chosen geometry type.

## Choosing Roles

Prefer explicit roles.

Good:

```python
points = rt.input("points", rt.Points, role="probe")
polygons = rt.input("polygons", rt.Polygons, role="build")
```

Avoid relying on implicit role assignment unless you are intentionally using the
default behavior.

## Workload Recipes

### Segment Intersection

Use when both inputs are segment sets and you want intersection pairs plus the
intersection point.

### Point In Polygon

Use when probe data are points and build data are polygon references.

### Overlay

Use when both inputs are polygon references and you want overlay seed records
instead of final overlay polygons.

### Ray/Triangle Hit Count

Use when probe data are finite 2D rays and build data are triangles, and you
want one count record per ray.

Recommended ray layout:

- origin: `ox`, `oy`
- direction: `dx`, `dy`
- finite extent: `tmax`
- identifier: `id`

Typical use:

- many random triangles in 2D
- many rays from a center point with random angle and random length
- one emitted result per ray with total hit count

## Current Limitations

- only `rayjoin` backend
- only `float_approx` precision
- only `bvh`
- only four predicates
- ray/triangle hit count remains 2D-only
- overlay is a composition-level skeleton, not a finished geometric overlay runtime
- generated OptiX/CUDA output is still backend skeleton code

## Dataset Guidance

For RayJoin-style data:

- load CDB chain files with `rt.load_cdb(...)`
- derive segments with `rt.chains_to_segments(...)`
- derive probe points with `rt.chains_to_probe_points(...)`
- derive polygon refs with `rt.chains_to_polygon_refs(...)`

For synthetic ray-query examples:

- use `examples/rtdl_ray_tri_hitcount.py`
- generate triangles with `make_random_triangles(...)`
- generate rays with `make_center_rays(...)`

## Validation Workflow

To validate a kernel:

1. compile it with `rt.compile_kernel(...)`
2. lower it with `rt.lower_to_rayjoin(...)`
3. generate backend artifacts with `rt.generate_optix_project(...)`

For repository-level validation:

- run `make test`
- run `make run-rtdsl-py`

## Authoring Checklist

- kernel uses `backend="rayjoin"` and `precision="float_approx"`
- every input has a unique name
- `accel="bvh"`
- predicate matches the geometry pair
- emit fields match the workload
- kernel returns `rt.emit(...)`
