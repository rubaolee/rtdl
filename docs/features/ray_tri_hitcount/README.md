# Ray/Triangle Hit Count

## Purpose

`ray_tri_hitcount` is RTDL's basic non-spatial-join ray-query workload.

Use it when the probe side is rays, the build side is triangles, and you want
one `hit_count` per ray.

## Docs

- canonical example:
  - [rtdl_ray_tri_hitcount.py](/Users/rl2025/rtdl_python_only/examples/rtdl_ray_tri_hitcount.py)
- language contracts:
  - [dsl_reference.md](/Users/rl2025/rtdl_python_only/docs/rtdl/dsl_reference.md)
  - [workload_cookbook.md](/Users/rl2025/rtdl_python_only/docs/rtdl/workload_cookbook.md)

Kernel shape:

```python
rays = rt.input("rays", rt.Rays, role="probe")
triangles = rt.input("triangles", rt.Triangles, role="build")
candidates = rt.traverse(rays, triangles, accel="bvh")
hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
return rt.emit(hits, fields=["ray_id", "hit_count"])
```

## Code

- predicate:
  - `rt.ray_triangle_hit_count(exact=False)`
- canonical reference kernel:
  - [ray_triangle_hitcount_reference](/Users/rl2025/rtdl_python_only/examples/rtdl_ray_tri_hitcount.py)

## Example

Run:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 examples/rtdl_ray_tri_hitcount.py
```

## Best Practices

- use this when you want a small, direct RT-style workload
- keep ray generation deterministic when you compare backends
- use it as an entry point for ray-style traversal understanding, not for polygon joins

## Try

- synthetic ray-query benchmarks
- small demo programs
- backend sanity checks for ray-style traversal

## Try Not

- spatial join semantics
- point/polygon or segment/polygon tasks
- treating triangle hit counts as object hit counts without an extra grouping layer

## Limitations

- this is a simpler ray-query feature, not the main live v0.2 workload-growth line
- current implementation is still float-based
- examples are synthetic, not the main public-data workload story
