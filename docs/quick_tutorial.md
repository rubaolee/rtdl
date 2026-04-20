# RTDL Quick Tutorial

RTDL is a geometric-query language that runs inside Python.

You write a kernel, a small function that describes what query to run, and then
call an RTDL runner to execute it. Python owns everything around the kernel:
data loading, post-processing, presentation, and output.

If you first need the boundary between "RTDL can do this" and "RTDL is not
intended to become this whole system", read
[RTDL Capability Boundaries](capability_boundaries.md).

The point is to avoid writing the same ray-tracing workload plumbing again for
each backend. A typical RT workload needs acceleration-structure setup,
candidate traversal, exact candidate refinement, output row normalization, and
CPU/GPU/backend variants. RTDL compresses that into one kernel shape:
`input -> traverse -> refine -> emit`.

The "10x reduction" goal in RTDL is about authoring burden: fewer backend files,
less duplicated traversal code, and a thinner Python app around optimized
kernels. It is not a promise that every backend is always 10x faster.

Command convention used below:

- use `python`
- if your shell only provides `python3`, substitute `python3`
- Bash/zsh examples use inline `PYTHONPATH=src:.`
- Windows PowerShell uses:
  - `$env:PYTHONPATH = "src;."`
  - then `python ...`

One-time setup for a fresh checkout:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Windows `cmd.exe`:

```bat
py -3 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Windows PowerShell:

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If `python3 -m venv` fails on Debian/Ubuntu because `ensurepip` is missing,
install the OS package first:

```bash
sudo apt install python3-venv
```

Backend note:

- `cpu_python_reference` is pure Python and should run on every OS
- `cpu` auto-builds the native C oracle library on first use
- `embree` auto-builds/probes `build/librtdl_embree.*` on first use when the
  host has Embree headers/libraries available
- on Linux with a configured GPU stack, `optix` and `vulkan` can run too
- released `v0.9.0` HIPRT support exists after `v0.8.0`; `run_hiprt` covers
  the current 18-workload HIPRT matrix on the Linux validation host,
  while `prepare_hiprt` currently covers prepared 3D `ray_triangle_hit_count`
  and prepared 3D `fixed_radius_neighbors`, plus prepared graph CSR reuse for
  `bfs_discover` and `triangle_match`, and prepared bounded DB table reuse for
  repeated `conjunctive_scan`, `grouped_count`, and `grouped_sum` queries
- released `v0.9.1` Apple RT support exists on Apple Silicon macOS;
  native Apple Metal/MPS execution currently covers 3D
  `ray_triangle_closest_hit`
- released v0.9.4 Apple RT work makes all 18 current predicates callable
  through `run_apple_rt` with explicit native or native-assisted modes
- supported geometry and nearest-neighbor slices use Apple MPS RT; bounded DB
  and graph slices use Apple Metal compute/native-assisted filtering, not Apple
  ray-tracing-hardware traversal
- use `native_only=True` when an app must reject unsupported shape/backend
  combinations instead of falling back to a compatibility path
- released v0.9.4 Apple RT work also adds prepared closest-hit reuse and
  masked traversal for hit-count and segment-intersection

Optional Embree backend build/probe:

```bash
make build-embree
```

On Windows, set `RTDL_EMBREE_PREFIX` to an x64 Embree prefix and set
`RTDL_VCVARS64` if Visual Studio Build Tools are not in the default location.
If a copied snapshot contains a stale `build/librtdl_embree.dll`, delete it and
rerun the Embree probe so RTDL rebuilds from the current source.

On Linux GPU hosts, build the GPU backend libraries once before using the
`optix` and `vulkan` commands:

```bash
make build-optix
make build-vulkan
```

On Linux hosts with the HIPRT SDK installed, build the HIPRT backend before
using the HIPRT example or matrix tests:

```bash
make build-hiprt HIPRT_PREFIX=/path/to/hiprtSdk
export RTDL_HIPRT_LIB=$PWD/build/librtdl_hiprt.so
export LD_LIBRARY_PATH=/path/to/hiprtSdk/hiprt/linux64:${LD_LIBRARY_PATH:-}
```

On Apple Silicon macOS, build the Apple RT backend before using the
Apple RT closest-hit example or current Apple RT native/native-assisted tests:

```bash
make build-apple-rt
```

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

For yes/no ray queries in the released `v0.9.5` line, use the same shape with
`rt.ray_triangle_any_hit(exact=False)` and emit `["ray_id", "any_hit"]`.
For line-of-sight applications, `rt.visibility_rows_cpu(...)` turns observers,
targets, and blocker triangles into `{observer_id, target_id, visible}` rows.
When the app needs a summary after emission, `rt.reduce_rows(...)` can reduce
rows by `any`, `count`, `sum`, `min`, or `max`; it is a Python helper, not a
native RT backend reduction.

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

If your Linux machine is configured for the HIPRT backend, use the
dedicated 3D prepared-path example first:

```bash
PYTHONPATH=src:. python examples/rtdl_hiprt_ray_triangle_hitcount.py
```

If your Apple Silicon Mac is configured for the Apple RT backend, use the
dedicated closest-hit example first:

```bash
PYTHONPATH=src:. python examples/rtdl_apple_rt_closest_hit.py
```

What stays the same:

- the scene
- the kernel
- the output meaning

What changes:

- which runner executes the kernel

---

## Step 3.5: Pick a feature

If you already understand `input -> traverse -> refine -> emit` and want to
know which RTDL feature matches your data, use the cookbook:

```bash
PYTHONPATH=src:. python examples/rtdl_feature_quickstart_cookbook.py
```

Then read [Feature Quickstart Cookbook](tutorials/feature_quickstart_cookbook.md).

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
5. [Graph Workloads](tutorials/graph_workloads.md)
6. [Database Workloads](tutorials/db_workloads.md)
7. [RTDL Plus Python Rendering](tutorials/rendering_and_visual_demos.md)

Optional bounded `v0.7.0` DB release examples:

```bash
PYTHONPATH=src:. python examples/rtdl_db_conjunctive_scan.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_db_grouped_count.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_db_grouped_sum.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_v0_7_db_app_demo.py --backend auto
PYTHONPATH=src:. python examples/rtdl_v0_7_db_kernel_app_demo.py --backend auto
```

These DB examples are analytical RTDL kernels over denormalized rows. They are
not SQL execution and RTDL is not a database system.

The two `rtdl_v0_7_*_demo.py` scripts show the app-level and kernel-form usage
of the same bounded DB surface. They are release-facing examples, not a DBMS
claim.

Or jump directly to the full hub:

- [RTDL Tutorials](tutorials/README.md)

---

## Three things to remember

- the kernel describes the query; Python runs the surrounding program
- `rt.run_cpu_python_reference(...)` is the easiest runner to start with
- switching backends changes execution, not the public kernel shape
