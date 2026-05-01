# Visibility Rows

## Purpose

`visibility_rows_cpu` is the CPU/oracle standard-library workload helper built
on bounded any-hit traversal. `visibility_rows(..., backend="embree" | "optix" |
"vulkan" | "hiprt" | "apple_rt")` exposes the same row contract through backend
any-hit compatibility dispatch.

`visibility_pair_rows(...)` is the sparse candidate-edge variant. It uses the
same backend any-hit dispatch, but it emits exactly one row per caller-provided
observer-target pair instead of evaluating the full observer-target matrix.

Use `visibility_rows(...)` when you have observer points, target points, and
triangle blockers, and you want one boolean visibility row for every
observer-target pair. Use `visibility_pair_rows(...)` when the application has
already selected candidate pairs, such as graph edges or sparse line-of-sight
queries.

## Data Shape

```text
observers + targets + blockers -> {observer_id, target_id, visible}
observer-target candidate pairs + blockers -> {observer_id, target_id, visible}
```

`visible` is `1` when no blocker triangle intersects the finite segment from
the observer to the target. It is `0` when at least one blocker triangle is hit.

## Example

Run:

```bash
PYTHONPATH=src:. python examples/rtdl_visibility_rows.py
```

## What It Uses Internally

The helper turns each observer-target pair into a finite ray and calls the
same any-hit reference primitive used by `rt.ray_triangle_any_hit`:

```python
rows = rt.visibility_rows_cpu(observers, targets, blockers)
```

Or select a backend:

```python
rows = rt.visibility_rows(observers, targets, blockers, backend="embree")
```

For explicit candidate edges:

```python
pairs = ((observer_a, target_a), (observer_b, target_b))
rows = rt.visibility_pair_rows(pairs, blockers, backend="optix")
```

It supports 2D `Point`/`Triangle` records and 3D `Point3D`/`Triangle3D`
records, but all observers, targets, and blockers in one call must share the
same dimensionality.

## Current Boundary

- `visibility_rows_cpu` is the CPU standard-library helper in `v0.9.5`.
- `visibility_rows(..., backend=...)` can use real backend dispatch through
  `ray_triangle_any_hit`.
- `visibility_pair_rows(..., backend=...)` uses the same backend dispatch but
  preserves explicit pair cardinality. It was added after the graph RTX gate
  exposed that candidate-edge graph workloads must not use Cartesian
  observer-target expansion.
- Backend visibility dispatch currently inherits the any-hit boundary:
  OptiX, Embree, HIPRT, current-main Vulkan, current-main Apple RT 3D, and
  current-main Apple RT 2D use native/native-assisted any-hit when the loaded
  libraries export it. Apple RT 2D uses MPS prism traversal with per-ray
  early-exit plus exact 2D acceptance, not programmable shader-level any-hit.
- It is intended for line-of-sight, visibility, blocker, and simple shadow-test
  application logic.
- It is not a full renderer, scene graph, dynamic occlusion system, or path
  tracer.
- Native backend-specific early-exit visibility kernels beyond the current
  OptiX, Embree, and HIPRT any-hit paths remain future backend performance
  work.
