# RTDL Programming Guide

This guide explains how to write RTDL kernels correctly for the current language
surface.

## 1. Start With The Kernel Header

Every RTDL kernel starts with:

```python
@rt.kernel(backend="rayjoin", precision="float_approx")
```

Do not vary these values in the current implementation.

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

## 5. Return Emit

The kernel must end with `return rt.emit(...)`.

```python
return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])
```

## Choosing Layouts

Use the default layouts unless you need to be explicit in docs or tests.

Built-in defaults:

- `rt.Segment2DLayout`
- `rt.Point2DLayout`
- `rt.Polygon2DLayout`

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

## Current Limitations

- only `rayjoin` backend
- only `float_approx` precision
- only `bvh`
- only three predicates
- overlay is a composition-level skeleton, not a finished geometric overlay runtime
- generated OptiX/CUDA output is still backend skeleton code

## Dataset Guidance

For RayJoin-style data:

- load CDB chain files with `rt.load_cdb(...)`
- derive segments with `rt.chains_to_segments(...)`
- derive probe points with `rt.chains_to_probe_points(...)`
- derive polygon refs with `rt.chains_to_polygon_refs(...)`

See [rayjoin_datasets.md](/Users/rl2025/rtdl_python_only/docs/rayjoin_datasets.md) for the data pipeline details.

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
