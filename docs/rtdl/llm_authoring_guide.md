# RTDL LLM Authoring Guide

This document is for LLMs and automated agents that need to write RTDL kernels.

## Authoring Contract

When writing RTDL in this repository:

- use only the public `rtdsl` API
- stay inside the implemented language surface
- do not invent new predicates, emit fields, or backends
- do not claim exact precision
- prefer explicit roles

## Required Template

Use this kernel pattern:

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def kernel_name():
    left = rt.input("left", rt.SomeGeometry, role="probe_or_build")
    right = rt.input("right", rt.SomeGeometry, role="probe_or_build")
    candidates = rt.traverse(left, right, accel="bvh")
    result = rt.refine(candidates, predicate=rt.some_supported_predicate(...))
    return rt.emit(result, fields=[...])
```

The kernel function must take no Python arguments.

## Supported Geometry / Predicate Pairs

- `Segments x Segments` with `segment_intersection(exact=False)`
- `Points x Polygons` with `point_in_polygon(exact=False, boundary_mode="inclusive")`
- `Polygons x Polygons` with `overlay_compose()`
- `Rays x Triangles` with `ray_triangle_hit_count(exact=False)`
- `Segments x Polygons` with `segment_polygon_hitcount(exact=False)`
- `Points x Segments` with `point_nearest_segment(exact=False)`

Current `v0.4` surface under active closure:

- `Points x Points` with `fixed_radius_neighbors(radius=..., k_max=...)`

## Supported Emit Fields

For LSI:

- `left_id`
- `right_id`
- `intersection_point_x`
- `intersection_point_y`

For PIP:

- `point_id`
- `polygon_id`
- `contains`

For Overlay:

- `left_polygon_id`
- `right_polygon_id`
- `requires_lsi`
- `requires_pip`

For Ray/Triangle Hit Count:

- `ray_id`
- `hit_count`

For Segment/Polygon Hit Count:

- `segment_id`
- `hit_count`

For Point/Nearest Segment:

- `point_id`
- `segment_id`
- `distance`

For `Fixed-Radius Neighbors`:

- `query_id`
- `neighbor_id`
- `distance`

## Do Not Do These Things

- `precision="exact"`
- `accel="grid"`
- `point_in_polygon(boundary_mode="exclusive")`
- `ray_triangle_hit_count(exact=True)`
- typed kernel arguments
- `for` loops inside the RTDL kernel body
- `rt.intersect(...)`
- `rt.Output[...]`
- `rt.KernelRole.*`
- custom predicates
- emit fields outside the approved lists
- polygon PIP with points on the build side

## Success Criterion For LLM-Authored Code

An RTDL program is acceptable only if:

- `rt.compile_kernel(...)` succeeds
- `rt.lower_to_execution_plan(...)` succeeds
- the resulting plan matches one of the supported workload kinds

Current boundary:

- `fixed_radius_neighbors(...)` now supports:
  - public DSL authoring
  - lowering
  - Python truth-path execution
  - native CPU/oracle execution
- accelerated backend closure is still pending

## Recommended Prompting Pattern

If another system asks for RTDL code, answer with:

- one import block
- one or more RTDL kernels
- only public `rtdsl` API calls
- no speculative APIs

If uncertain, choose the narrower currently implemented surface.
