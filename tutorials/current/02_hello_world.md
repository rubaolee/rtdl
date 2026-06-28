# Hello RTDL

The first RTDL program should still feel like hello world: run one command and
see one line:

Run it from the repository root:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\tutorial_programs\hello_world.py
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/hello_world.py
```

Expected output:

```text
hello, world
```

The point of the program is not the string. The point is that the string is
selected by an RTDL geometric query.

The kernel is the smallest complete RTDL shape:

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def hello_world_kernel():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])
```

Read it as:

1. `rt.input(..., role="probe")` declares the rays, the things that search.
2. `rt.input(..., role="build")` declares the triangles, the things searched.
3. `rt.traverse(...)` asks RTDL to find candidate ray/triangle pairs through a
   BVH-style traversal.
4. `rt.refine(...)` keeps the real ray/triangle hits.
5. `rt.emit(...)` chooses the result row fields.

The scene has one horizontal ray and three rectangles:

```text
left miss        middle hit          right miss
+--------+      +--------------+     +--------+
|        |      | hello, world |     |        |
+--------+ ---> +--------------+ ---> +--------+
```

RTDL works with triangles here, so each rectangle is encoded as two triangles.
The middle rectangle is hit by the ray, producing a hit count of `2`, and Python
maps that result row back to the rectangle label:

```text
rows = rt.run_cpu_python_reference(
    hello_world_kernel,
    rays=rays,
    triangles=triangles,
)
```

This first run uses the portable CPU reference path so every user can run it.
Later lessons use the same RTDL shape with current V4 operator surfaces,
partners, and benchmark-sized workloads.

Next run the sorting tutorial. It keeps the same idea: express the problem as
RT-shaped rows first, then let Python read the rows.

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\tutorial_programs\sorting_rows.py
```

Next: [Sorting Rows](03_sorting_rows.md)
