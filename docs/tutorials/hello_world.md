# Tutorial: Hello World

This is the first RTDL kernel you should read in full.

It teaches the smallest complete RTDL idea:

- RTDL handles the geometric query
- Python handles the surrounding program

Command convention used below:

- use `python`
- if your shell only provides `python3`, substitute `python3`

---

## Run it first

```bash
PYTHONPATH=src:. python examples/rtdl_hello_world.py
```

Expected output:

```text
hello, world
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\rtdl_hello_world.py
```

---

## The scene

The ray travels left to right across three rectangles:

- one left miss
- one middle hit labelled `hello, world`
- one right miss

RTDL works with triangles, so the visible rectangle is encoded as two triangles.
That is why the underlying hit count is `2` even though the printed answer is a
single label.

---

## The full kernel

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

### Line by line

`@rt.kernel(...)`

- marks the function as an RTDL kernel
- `precision="float_approx"` means the traversal side may use float-oriented approximations internally

`rt.input("rays", ..., role="probe")`

- declares the active geometry, the things that search

`rt.input("triangles", ..., role="build")`

- declares the geometry to be searched
- this side is built into the acceleration structure

`rt.traverse(rays, triangles, accel="bvh")`

- runs BVH traversal to find candidate `(ray, triangle)` pairs quickly

`rt.refine(candidates, predicate=...)`

- applies the exact predicate to keep only real hits

`rt.emit(hits, fields=[...])`

- chooses which output fields appear in each result row

---

## The Python wrapper

The kernel only describes the query. Python runs the program:

```python
rows = rt.run_cpu_python_reference(
    hello_world_kernel,
    rays=rays,
    triangles=triangles,
)
```

That returns rows like:

```python
({"ray_id": 0, "hit_count": 2},)
```

Then Python maps `hit_count == 2` back to the visible rectangle label and
prints:

```text
hello, world
```

---

## Try a different backend

```bash
PYTHONPATH=src:. python examples/rtdl_hello_world_backends.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_hello_world_backends.py --backend cpu
PYTHONPATH=src:. python examples/rtdl_hello_world_backends.py --backend embree
```

If your machine is configured for GPU backends:

```bash
PYTHONPATH=src:. python examples/rtdl_hello_world_backends.py --backend optix
PYTHONPATH=src:. python examples/rtdl_hello_world_backends.py --backend vulkan
```

Expected JSON excerpt:

```json
{
  "backend": "cpu_python_reference",
  "triangle_hit_count": 2,
  "visible_hit_label": "hello, world"
}
```

What to notice:

- the kernel stays the same
- the scene stays the same
- only the runner/backend changes

---

## Next

- [Sorting Demo](sorting_demo.md)
- [Segment And Polygon Workloads](segment_polygon_workloads.md)
