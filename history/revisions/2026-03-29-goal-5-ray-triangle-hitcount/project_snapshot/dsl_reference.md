# RTDL DSL Reference

RTDL is a Python-hosted DSL for non-graphics ray tracing kernels. The current
language surface is intentionally small and explicit.

## Scope

This reference only describes the RTDL features that are implemented today:

- backend: `rayjoin`
- precision: `float_approx`
- accel: `bvh`
- workloads:
  - `lsi`
  - `pip`
  - `overlay`
  - `ray_tri_hitcount`

Anything outside this surface is not part of the current language.

## Kernel Grammar

RTDL kernels are written in Python, but the accepted authoring shape is fixed.

```text
KernelDef ::=
  @rt.kernel(backend="rayjoin", precision="float_approx")
  def <kernel_name>():
      <InputDef>+
      <TraverseDef>
      <RefineDef>
      return <EmitDef>

InputDef ::=
  <name> = rt.input(<input_name>, <GeometryType>,
                    layout=<LayoutExpr>?, role=<Role>?)

TraverseDef ::=
  <name> = rt.traverse(<left_input>, <right_input>, accel="bvh")

RefineDef ::=
  <name> = rt.refine(<candidate_set>, predicate=<PredicateExpr>)

EmitDef ::=
  rt.emit(<refine_op>, fields=[<EmitField>, ...])
```

Kernels do not accept Python function arguments.

## Required Kernel Rules

- Every RTDL kernel must be decorated with `@rt.kernel(...)`.
- `backend` must be `"rayjoin"`.
- `precision` must be `"float_approx"`.
- The kernel function must return `rt.emit(...)`.
- Input names inside one kernel must be unique.
- `role`, when present, must be `"build"` or `"probe"`.
- The current lowering only supports `accel="bvh"`.
- RTDL kernels do not support arbitrary Python control flow as part of the DSL surface.
- The accepted semantic shape is exactly `input -> traverse -> refine -> emit`.

## Public RTDL Operations

### `@rt.kernel(backend=..., precision=...)`

Defines one compilable RTDL kernel.

Current accepted values:

- `backend="rayjoin"`
- `precision="float_approx"`

### `rt.input(name, geometry, layout=None, role=None)`

Declares one geometry input.

Arguments:

- `name`: unique kernel-local string
- `geometry`: one of `rt.Segments`, `rt.Points`, `rt.Polygons`, `rt.Triangles`, `rt.Rays`
- `layout`: optional explicit layout
- `role`: optional `"build"` or `"probe"`

### `rt.traverse(left, right, accel="bvh")`

Declares candidate generation between two inputs.

Current accepted value:

- `accel="bvh"`

### `rt.refine(candidates, predicate=...)`

Declares the exact or approximate refinement stage for the candidate set.

### `rt.emit(source, fields=[...])`

Declares the output record schema.

## Geometry Types

### `rt.Segments`

Default layout: `Segment2D`

Required fields:

- `x0`
- `y0`
- `x1`
- `y1`
- `id`

### `rt.Points`

Default layout: `Point2D`

Required fields:

- `x`
- `y`
- `id`

### `rt.Polygons`

Default layout: `Polygon2DRef`

Required fields:

- `vertex_offset`
- `vertex_count`
- `id`

### `rt.Triangles`

Default layout: `Triangle2D`

Required fields:

- `x0`
- `y0`
- `x1`
- `y1`
- `x2`
- `y2`
- `id`

### `rt.Rays`

Default layout: `Ray2D`

Required fields:

- `ox`
- `oy`
- `dx`
- `dy`
- `tmax`
- `id`

## Layout Construction

Layouts are defined with:

```python
rt.layout(
    "LayoutName",
    rt.field("field_name", rt.f32_or_u32),
    ...
)
```

Current scalar types:

- `rt.f32`
- `rt.u32`

Current built-in default layouts:

- `rt.Segment2DLayout`
- `rt.Point2DLayout`
- `rt.Polygon2DLayout`
- `rt.Triangle2DLayout`
- `rt.Ray2DLayout`

## Predicates

### `rt.segment_intersection(exact=False)`

Meaning:

- line segment intersection under the current float-based implementation

Required option:

- `exact=False`

### `rt.point_in_polygon(exact=False, boundary_mode="inclusive")`

Meaning:

- point-in-polygon under the current float-based implementation

Required options:

- `exact=False`
- `boundary_mode="inclusive"`

### `rt.overlay_compose()`

Meaning:

- overlay seed generation over polygon inputs
- lowered as a composition-oriented overlay skeleton over LSI/PIP style logic

### `rt.ray_triangle_hit_count(exact=False)`

Meaning:

- finite 2D ray vs triangle hit counting under the current float-based implementation

Required option:

- `exact=False`

## Role Resolution

RTDL supports explicit and implicit roles.

Explicit:

- `role="build"`
- `role="probe"`

Implicit:

- for `points x polygons`, polygons become build and points become probe
- for `rays x triangles`, triangles become build and rays become probe
- otherwise, if no explicit role resolves the pair, the current lowering defaults
  to the right input as build and the left input as probe

For stable authoring, prefer explicit roles.

## Workload Contracts

### `lsi`

Required shape:

- build input: `segments`
- probe input: `segments`
- predicate: `segment_intersection(exact=False)`

Allowed emit fields:

- `left_id`
- `right_id`
- `intersection_point_x`
- `intersection_point_y`

### `pip`

Required shape:

- build input: `polygons`
- probe input: `points`
- predicate: `point_in_polygon(exact=False, boundary_mode="inclusive")`

Allowed emit fields:

- `point_id`
- `polygon_id`
- `contains`

### `overlay`

Required shape:

- build input: `polygons`
- probe input: `polygons`
- predicate: `overlay_compose()`

Allowed emit fields:

- `left_polygon_id`
- `right_polygon_id`
- `requires_lsi`
- `requires_pip`

### `ray_tri_hitcount`

Required shape:

- build input: `triangles`
- probe input: `rays`
- predicate: `ray_triangle_hit_count(exact=False)`

Allowed emit fields:

- `ray_id`
- `hit_count`

## Canonical Kernel Shapes

### LSI

```python
@rt.kernel(backend="rayjoin", precision="float_approx")
def county_zip_join():
    left = rt.input("left", rt.Segments, role="probe")
    right = rt.input("right", rt.Segments, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(
        hits,
        fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
    )
```

### PIP

```python
@rt.kernel(backend="rayjoin", precision="float_approx")
def point_in_counties():
    points = rt.input("points", rt.Points, role="probe")
    polygons = rt.input("polygons", rt.Polygons, role="build")
    candidates = rt.traverse(points, polygons, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.point_in_polygon(exact=False))
    return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])
```

### Overlay

```python
@rt.kernel(backend="rayjoin", precision="float_approx")
def county_soil_overlay():
    left = rt.input("left", rt.Polygons, role="probe")
    right = rt.input("right", rt.Polygons, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    seeds = rt.refine(candidates, predicate=rt.overlay_compose())
    return rt.emit(
        seeds,
        fields=["left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"],
    )
```

### Ray/Triangle Hit Count

```python
@rt.kernel(backend="rayjoin", precision="float_approx")
def central_ray_triangle_stats():
    rays = rt.input("rays", rt.Rays, role="probe")
    triangles = rt.input("triangles", rt.Triangles, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])
```

## Non-Goals Of The Current Language

- exact or robust precision
- multiple backends
- non-BVH acceleration structures
- arbitrary control flow inside kernels
- typed kernel parameters
- explicit user-written loops over geometry
- user-written intersection calls such as `rt.intersect(...)`
- custom user-defined predicates
- 3D geometry
- standalone runtime execution without the RTDL compiler pipeline
