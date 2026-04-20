# Ray/Triangle Any Hit

## Purpose

`ray_tri_anyhit` is RTDL's bounded early-exit ray-query workload.

Use it when the probe side is rays, the build side is triangles, and the
application only needs to know whether each ray hits at least one triangle.
This avoids asking the workload to count every hit when a boolean blocker flag
is enough.

## Kernel Shape

```python
rays = rt.input("rays", rt.Rays, role="probe")
triangles = rt.input("triangles", rt.Triangles, role="build")
candidates = rt.traverse(rays, triangles, accel="bvh")
hits = rt.refine(candidates, predicate=rt.ray_triangle_any_hit(exact=False))
return rt.emit(hits, fields=["ray_id", "any_hit"])
```

Input data becomes one row per ray:

```text
rays + triangles -> {ray_id, any_hit}
```

`any_hit` is `1` when the finite ray intersects at least one triangle and `0`
otherwise. The contract permits traversal to stop after the first accepted hit.
It does not return the first blocker id or closest distance.

## Example

Run:

```bash
PYTHONPATH=src:. python examples/rtdl_ray_triangle_any_hit.py
```

Use `python3` instead if that is what your shell exposes.

## Best Practices

- Use this for visibility, collision screening, shadow/blocker queries, and
  other yes/no ray workloads.
- Use `ray_triangle_hit_count` when the application needs the number of hits.
- Use `ray_triangle_closest_hit` when the application needs the nearest hit.
- Keep rays finite by setting `tmax` to the intended segment length or by using
  a normalized parameterization.

## Current Boundary

- `v0.9.5` exposes the language predicate, lowering metadata, CPU Python
  reference path, and `run_cpu` oracle fallback.
- OptiX has a native early-exit any-hit path that sets `any_hit=1` and
  terminates the ray after the first accepted triangle hit.
- Embree has a native early-exit any-hit path using `rtcOccluded1`.
- HIPRT has a native any-hit path that breaks its HIPRT traversal loop after
  the first reported accepted hit.
- Current `main` adds native Vulkan any-hit through a dedicated Vulkan RT
  pipeline and raw row ABI when `librtdl_vulkan` is rebuilt from current source.
- Current `main` adds Apple MPS RT 3D any-hit by querying nearest-intersection
  existence instead of counting all hits.
- Current `main` adds Apple RT 2D MPS-prism any-hit with per-ray mask
  early-exit plus exact 2D acceptance when `librtdl_apple_rt` is rebuilt.
- Apple any-hit remains native-assisted MPS traversal, not programmable
  shader-level any-hit.
- The implementation is float-based and bounded; it is not a rendering API.
