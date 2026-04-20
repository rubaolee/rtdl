# Visibility Rows

## Purpose

`visibility_rows_cpu` is the CPU/oracle standard-library workload helper built
on bounded any-hit traversal. `visibility_rows(..., backend="embree" | "optix" |
"vulkan" | "hiprt" | "apple_rt")` exposes the same row contract through backend
any-hit compatibility dispatch.

Use it when you have observer points, target points, and triangle blockers, and
you want one boolean visibility row for every observer-target pair.

## Data Shape

```text
observers + targets + blockers -> {observer_id, target_id, visible}
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

It supports 2D `Point`/`Triangle` records and 3D `Point3D`/`Triangle3D`
records, but all observers, targets, and blockers in one call must share the
same dimensionality.

## Current Boundary

- `visibility_rows_cpu` is the CPU standard-library helper in `v0.9.5`.
- `visibility_rows(..., backend=...)` can use real backend dispatch through
  `ray_triangle_any_hit`.
- Backend visibility dispatch currently inherits the any-hit boundary:
  OptiX, Embree, HIPRT, and current-main Vulkan use native early-exit any-hit
  when the loaded libraries export it, while Apple RT may compute
  `hit_count > 0`, proving backend execution and parity but not native
  early-exit Apple performance.
- It is intended for line-of-sight, visibility, blocker, and simple shadow-test
  application logic.
- It is not a full renderer, scene graph, dynamic occlusion system, or path
  tracer.
- Native backend-specific early-exit visibility kernels beyond the current
  OptiX, Embree, and HIPRT any-hit paths remain future backend performance
  work.
