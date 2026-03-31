# RTDL Feature Guide

This document summarizes the RTDL feature surface that exists today, shows representative programs, and explains what those programs mean.

It is meant to answer a practical question:

"What can the current RTDL actually express and run?"

## 1. What RTDL is today

RTDL is a Python-hosted DSL for non-graphics ray tracing workloads.

Users stay in Python, but instead of writing low-level Embree, OptiX, or CUDA orchestration directly, they describe:

- geometry inputs
- traversal intent
- refinement predicates
- emitted result fields

The current system has three meaningful layers:

- Language layer: write kernels with `@rt.kernel(...)`, `rt.input(...)`, `rt.traverse(...)`, `rt.refine(...)`, and `rt.emit(...)`
- Compiler layer: compile the DSL into RTDL IR, lower it to a RayJoin-oriented plan, and generate OptiX/CUDA skeleton artifacts
- Runtime layer: execute supported workloads through either a Python reference executor or the local Embree backend

So the current project is no longer just a code generator. It already includes:

- a usable DSL surface
- an inspectable IR and lowering path
- a runnable CPU reference backend
- a runnable Embree backend on this Mac

For the current paper-reproduction phase, also see:

- [Preserved Goal 13 plan](/Users/rl2025/rtdl_python_only/docs/goal_13_rayjoin_paper_embree_plan.md)
- [RayJoin paper reproduction checklist](/Users/rl2025/rtdl_python_only/docs/rayjoin_paper_reproduction_checklist.md)
- [RayJoin paper dataset provenance](/Users/rl2025/rtdl_python_only/docs/rayjoin_paper_dataset_provenance.md)

## 2. Workloads supported today

The current RTDL supports six workload families:

1. `lsi`
   Segment-segment intersection

2. `pip`
   Point-in-polygon

3. `overlay`
   Compositional polygon overlay seed generation

4. `ray_tri_hitcount`
   Finite 2D ray vs triangle hit counting

5. `segment_polygon_hitcount`
   Per-segment polygon hit counting

6. `point_nearest_segment`
   Nearest-segment lookup per point

Geometry types currently supported include:

- `rt.Points`
- `rt.Segments`
- `rt.Polygons`
- `rt.Triangles`
- `rt.Rays`

Current predicate/refine operators include:

- `rt.segment_intersection(exact=False)`
- `rt.point_in_polygon(exact=False)`
- `rt.overlay_compose()`
- `rt.ray_triangle_hit_count(exact=False)`
- `rt.segment_polygon_hitcount(exact=False)`
- `rt.point_nearest_segment(exact=False)`

Current audited limits:

- PIP supports only `boundary_mode="inclusive"`.
- `segment_polygon_hitcount` and `point_nearest_segment` run end to end today, but the current local backend executes them through audited `native_loop` paths instead of BVH-backed traversal.
- Precision remains `float_approx`.

## 3. Basic RTDL kernel structure

Most RTDL kernels follow this pattern:

```python
import rtdsl as rt

@rt.kernel(backend="rayjoin", precision="float_approx")
def some_query():
    left = rt.input("left", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    right = rt.input("right", rt.Segments, layout=rt.Segment2DLayout, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(
        hits,
        fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
    )
```

The structure has five semantic steps:

1. `@rt.kernel(...)`
   Declares an RTDL kernel.

2. `rt.input(...)`
   Declares each input, its geometry kind, layout, and query role.

3. `rt.traverse(...)`
   Declares how candidate pairs are formed. Today the common mode is `accel="bvh"`.

4. `rt.refine(...)`
   Applies the actual geometric predicate or refinement logic to the candidate set.

5. `rt.emit(...)`
   Declares the output row schema.

## 4. Example: segment intersection (`lsi`)

```python
import rtdsl as rt

@rt.kernel(backend="rayjoin", precision="float_approx")
def county_zip_join():
    left = rt.input("left", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    right = rt.input("right", rt.Segments, layout=rt.Segment2DLayout, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(
        hits,
        fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
    )
```

### What this code means

`@rt.kernel(backend="rayjoin", precision="float_approx")`

- `backend="rayjoin"` means the current lowering path still targets a RayJoin-style backend model.
- `precision="float_approx"` means the implemented path is floating-point approximate, not exact arithmetic.

`left = rt.input(...)` and `right = rt.input(...)`

- These declare two segment sets.
- `role="probe"` and `role="build"` distinguish the probing side from the side that owns the acceleration structure.

`candidates = rt.traverse(left, right, accel="bvh")`

- This does not immediately compute intersections.
- It first defines candidate generation through BVH-style traversal.

`hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))`

- This is the actual segment-segment intersection test.

`rt.emit(...)`

- This emits both input ids plus the intersection point coordinates.

### How to run it

The same kernel can run on two currently supported execution paths:

```python
rows_cpu = rt.run_cpu(county_zip_join, left=left_segments, right=right_segments)
rows_embree = rt.run_embree(county_zip_join, left=left_segments, right=right_segments)
```

- `run_cpu(...)` is the Python reference semantics
- `run_embree(...)` is the native Embree backend

## 5. Example: point-in-polygon (`pip`)

```python
import rtdsl as rt

@rt.kernel(backend="rayjoin", precision="float_approx")
def point_in_counties():
    points = rt.input("points", rt.Points, layout=rt.Point2DLayout, role="probe")
    polygons = rt.input("polygons", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(points, polygons, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.point_in_polygon(exact=False))
    return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])
```

### What this code means

- The inputs are a point set and a polygon set.
- `traverse(...)` creates point-polygon candidate pairs.
- `point_in_polygon(...)` tests containment.
- The output row schema is:
  - `point_id`
  - `polygon_id`
  - `contains`

If `contains=1`, the point is inside the polygon. If `contains=0`, it is outside.

## 6. Example: rays from a center point against random triangles

This example is closer to a more general RT query language than the original RayJoin workloads.

```python
import rtdsl as rt

@rt.kernel(backend="rayjoin", precision="float_approx")
def central_ray_triangle_stats():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])
```

### What this code means

`rays = rt.input("rays", rt.Rays, ...)`

- The input is a set of finite 2D rays.
- Each ray usually carries:
  - origin
  - direction
  - a finite length via `tmax`
  - an id

`triangles = rt.input("triangles", rt.Triangles, ...)`

- The input is a set of triangles.

`rt.ray_triangle_hit_count(exact=False)`

- Counts how many triangles each finite ray hits.

`rt.emit(hits, fields=["ray_id", "hit_count"])`

- Emits one result row per ray:
  - `ray_id`
  - `hit_count`

### Intuition

If the user wants to ask:

"In a 2D space, place many random triangles, then shoot rays from the center with random angles and finite lengths, and count how many triangles each ray hits."

The current RTDL can already express and execute that query.

## 7. Example: Goal 10 workload extensions

### `segment_polygon_hitcount`

```python
import rtdsl as rt

@rt.kernel(backend="rayjoin", precision="float_approx")
def segment_polygon_hitcount_reference():
    segments = rt.input("segments", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    polygons = rt.input("polygons", rt.Polygons, layout=rt.Polygon2DLayout, role="build")
    candidates = rt.traverse(segments, polygons, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_polygon_hitcount(exact=False))
    return rt.emit(hits, fields=["segment_id", "hit_count"])
```

This program means:

- input a segment set and a polygon set
- for each segment, count how many polygons it hits
- output:
  - `segment_id`
  - `hit_count`

### `point_nearest_segment`

```python
import rtdsl as rt

@rt.kernel(backend="rayjoin", precision="float_approx")
def point_nearest_segment_reference():
    points = rt.input("points", rt.Points, layout=rt.Point2DLayout, role="probe")
    segments = rt.input("segments", rt.Segments, layout=rt.Segment2DLayout, role="build")
    candidates = rt.traverse(points, segments, accel="bvh")
    nearest = rt.refine(candidates, predicate=rt.point_nearest_segment(exact=False))
    return rt.emit(nearest, fields=["point_id", "segment_id", "distance"])
```

This program means:

- input a point set and a segment set
- for each point, find the nearest segment
- output:
  - `point_id`
  - `segment_id`
  - `distance`

Here `distance` is the point-to-segment distance.

## 8. How RTDL programs run today

RTDL currently has three distinct paths:

### Compiler path

```python
compiled = rt.compile_kernel(kernel_fn)
plan = rt.lower_to_rayjoin(compiled)
generated = rt.generate_optix_project(plan, output_dir)
```

This path:

- compiles the DSL to IR
- lowers the IR to a RayJoin-style backend plan
- generates OptiX/CUDA skeleton files

This mainly serves the future NVIDIA/OptiX backend.

### CPU path

```python
rows = rt.run_cpu(kernel_fn, **inputs)
```

This path:

- executes the current workload through Python reference semantics
- provides the semantic baseline for correctness checks

### Embree path

```python
rows = rt.run_embree(kernel_fn, **inputs)
```

This path:

- uses the same DSL kernel
- lowers the logical workload into the local Embree-backed runtime
- returns real execution results on this Mac

So the current system is no longer "codegen only." It already has a real executable backend on macOS.

## 9. Current boundaries

The current RTDL can express and run several non-graphics RT workloads, but it still has clear limits:

- precision is still `float_approx`
- exact or robust geometric arithmetic is not yet implemented
- workload growth is still explicit and enumerated rather than fully open-ended
- the NVIDIA/OptiX backend is not yet a real runnable execution path
- generated OptiX/CUDA files are still primarily for backend planning and skeleton validation

So the most accurate current statement is:

- RTDL is already a writable, compilable, locally executable DSL prototype
- the Embree backend is real
- the NVIDIA RT-core backend remains the next major stage

## 10. Recommended reading order

For a developer new to the current RTDL, this is a good reading order:

1. [README.md](/Users/rl2025/rtdl_python_only/README.md)
2. [rtdsl_python_demo.py](/Users/rl2025/rtdl_python_only/apps/rtdsl_python_demo.py)
3. [programming_guide.md](/Users/rl2025/rtdl_python_only/docs/rtdl/programming_guide.md)
4. [rtdl_goal10_reference.py](/Users/rl2025/rtdl_python_only/examples/rtdl_goal10_reference.py)
5. [api.py](/Users/rl2025/rtdl_python_only/src/rtdsl/api.py)
6. [runtime.py](/Users/rl2025/rtdl_python_only/src/rtdsl/runtime.py)
7. [embree_runtime.py](/Users/rl2025/rtdl_python_only/src/rtdsl/embree_runtime.py)

## 11. Summary

At the current stage, RTDL already supports:

- six workload families
- Python DSL authoring
- IR, lowering, and code generation
- CPU reference execution
- Embree native execution
- benchmarking, tables, and figure generation

The best way to understand the project now is:

RTDL has moved from "research idea" to "executable language prototype." It has not yet reached the final NVIDIA RT-core goal, but it has already established a working Embree baseline and a DSL surface that can continue to grow.
