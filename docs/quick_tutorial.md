# RTDL Quick Tutorial

RTDL is a geometric-query language that runs inside Python.

You write a kernel, a small function that describes what query to run, and then
call an RTDL runner to execute it. Python owns everything around the kernel:
data loading, post-processing, presentation, and output.

Command convention used below:

- use `python`
- if your shell only provides `python3`, substitute `python3`
- Bash/zsh examples use inline `PYTHONPATH=src:.`
- Windows PowerShell uses:
  - `$env:PYTHONPATH = "src;."`
  - then `python ...`

---

## Step 1: First run

From the repository root:

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

Windows PowerShell:

```powershell
$env:PYTHONPATH = "src;."
python examples/rtdl_hello_world.py
```

---

## Step 2: What is a kernel?

Every RTDL program has the same four-step shape:

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def my_kernel():
    probe = rt.input("probe_name", rt.Rays, role="probe")
    build = rt.input("build_name", rt.Triangles, role="build")
    candidates = rt.traverse(probe, build, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])
```

- `input` declares the geometry you will pass in
- `traverse` finds candidate pairs quickly with a BVH
- `refine` applies the exact predicate
- `emit` selects which fields appear in each output row

Then run it:

```python
rows = rt.run_cpu_python_reference(my_kernel, probe_name=(...), build_name=(...))
```

`rows` is a tuple of dicts, one per output row.

---

## Step 3: Same kernel, different backend

```bash
PYTHONPATH=src:. python examples/rtdl_hello_world_backends.py --backend cpu_python_reference
```

Expected output:

```json
{
  "backend": "cpu_python_reference",
  "triangle_hit_count": 2,
  "visible_hit_rect_id": 2,
  "visible_hit_label": "hello, world"
}
```

Then try:

```bash
PYTHONPATH=src:. python examples/rtdl_hello_world_backends.py --backend cpu
PYTHONPATH=src:. python examples/rtdl_hello_world_backends.py --backend embree
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "src;."
python examples/rtdl_hello_world_backends.py --backend cpu_python_reference
python examples/rtdl_hello_world_backends.py --backend cpu
python examples/rtdl_hello_world_backends.py --backend embree
```

If your machine is configured for GPU backends:

```bash
PYTHONPATH=src:. python examples/rtdl_hello_world_backends.py --backend optix
PYTHONPATH=src:. python examples/rtdl_hello_world_backends.py --backend vulkan
```

What stays the same:

- the scene
- the kernel
- the output meaning

What changes:

- which runner executes the kernel

---

## Step 4: Try a spatial query

```bash
PYTHONPATH=src:. python examples/rtdl_fixed_radius_neighbors.py --backend cpu_python_reference
```

Expected output excerpt:

```json
{
  "app": "fixed_radius_neighbors",
  "radius": 0.5,
  "neighbors_by_query": {
    "100": [{"neighbor_id": 1, "distance": 0.0}],
    "101": [{"neighbor_id": 4, "distance": 0.2}]
  }
}
```

The kernel shape is still the same:

```python
@rt.kernel(backend="rtdl", precision="float_approx")
def fixed_radius_neighbors_kernel():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=0.5, k_max=3))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])
```

---

## Tutorial ladder

Follow this order to learn progressively:

1. [Hello World](tutorials/hello_world.md)
2. [Sorting Demo](tutorials/sorting_demo.md)
3. [Segment And Polygon Workloads](tutorials/segment_polygon_workloads.md)
4. [Nearest-Neighbor Workloads](tutorials/nearest_neighbor_workloads.md)
5. [RTDL Plus Python Rendering](tutorials/rendering_and_visual_demos.md)

Or jump directly to the full hub:

- [RTDL Tutorials](tutorials/README.md)

---

## Three things to remember

- the kernel describes the query; Python runs the surrounding program
- `rt.run_cpu_python_reference(...)` is the easiest runner to start with
- switching backends changes execution, not the public kernel shape
