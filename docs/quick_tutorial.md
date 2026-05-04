# RTDL Quick Tutorial

RTDL is a geometric-query language that runs inside Python.

You write a kernel, a small function that describes what query to run, then call
an RTDL runner to execute it. Python owns the surrounding program: data loading,
post-processing, presentation, and output.

The point is to avoid rewriting backend-specific ray-tracing workload plumbing.
An RT workload usually needs acceleration-structure setup, candidate traversal,
exact candidate refinement, output normalization, and CPU/GPU/backend variants.
RTDL compresses that into one kernel shape:

```text
input -> traverse -> refine -> emit
```

The "10x reduction" goal is about authoring burden: fewer backend files, less
duplicated traversal code, and a thinner Python app around optimized kernels. It
is not a promise that every backend is always 10x faster.

For the boundary between "RTDL can do this" and "RTDL is not this whole
system", read [Capability Boundaries](capability_boundaries.md). For exact
current backend support, read
[RTDL Current Main Support Matrix](current_main_support_matrix.md) and
[App Engine Support Matrix](app_engine_support_matrix.md).

## Setup

From a fresh checkout:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If your shell only provides `python3`, substitute `python3` for `python` in the
commands below.

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

## Step 1: First Run

Run this from the repository root:

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

## Step 2: Kernel Shape

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

- `input` declares the geometry you will pass in.
- `traverse` finds candidate pairs quickly with a BVH.
- `refine` applies the predicate.
- `emit` selects which fields appear in each output row.

Then run it:

```python
rows = rt.run_cpu_python_reference(my_kernel, probe_name=(...), build_name=(...))
```

`rows` is a tuple of dicts, one per output row.

## Step 3: Same Kernel, Different Backend

Start with the portable reference backend:

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

Then try optional native backends if your machine has them configured:

```bash
PYTHONPATH=src:. python examples/rtdl_hello_world_backends.py --backend cpu
PYTHONPATH=src:. python examples/rtdl_hello_world_backends.py --backend embree
```

If your Linux GPU host is configured for GPU backends:

```bash
PYTHONPATH=src:. python examples/rtdl_hello_world_backends.py --backend optix
PYTHONPATH=src:. python examples/rtdl_hello_world_backends.py --backend vulkan
```

What stays the same:

- the scene
- the kernel shape
- the output meaning

What changes:

- which runner executes the kernel

## Step 4: Try A Spatial Query

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

## Step 5: Pick A Feature Or App

For one compact recipe per feature:

```bash
PYTHONPATH=src:. python examples/rtdl_feature_quickstart_cookbook.py
```

Then read [Feature Quickstart Cookbook](tutorials/feature_quickstart_cookbook.md).

For app-shaped demos, use [App And Example Quickstart](app_example_quickstart.md).
For the full command archive, use
[Release-Facing Examples](release_facing_examples.md).
For app boundaries and backend support, use
[Application Catalog](application_catalog.md) and
[App Engine Support Matrix](app_engine_support_matrix.md).
Repository paths: `docs/application_catalog.md` and
`docs/app_engine_support_matrix.md`.
Current app entry points include `examples/rtdl_database_analytics_app.py` and
`examples/rtdl_apple_rt_demo_app.py`; older scenario-specific DB and Apple RT
files are compatibility helpers rather than the recommended public start.

## Backend And Claim Boundaries

Portable first-run backends:

- `cpu_python_reference` is pure Python and should run on every OS.
- `cpu` auto-builds the native C oracle library on first use.
- `embree` auto-builds/probes `build/librtdl_embree.*` on first use when the
  host has Embree headers/libraries available.

Optional backend build commands:

```bash
make build-embree
make build-optix
make build-vulkan
make build-hiprt HIPRT_PREFIX=/path/to/hiprtSdk
make build-apple-rt
```

NVIDIA RT-core claim note:

- `--backend optix` selects an OptiX-capable path; it is not by itself a
  NVIDIA RT-core acceleration claim.
- use `--require-rt-core` only in claim-sensitive app runs; public apps fail
  fast unless the selected OptiX mode is a documented bounded RT-core path.
- Start from [Application Catalog](application_catalog.md) and
  [App Engine Support Matrix](app_engine_support_matrix.md) before benchmarking
  or publishing RTX claims.
- Goal1177 and Goal1184 are external-review input only; they do not authorize
  new public RTX speedup wording.

Current released feature terms you will see in public docs include
`ray_triangle_any_hit`, `visibility_rows`, and `reduce_rows`. `reduce_rows` is a
Python helper over emitted rows, not a native backend reduction. OptiX, Embree,
and HIPRT have released native early-exit any-hit coverage. Vulkan and Apple RT
also have released bounded paths, but backend support varies by predicate and
platform.

## Three Things To Remember

- The kernel describes the query; Python runs the surrounding program.
- `rt.run_cpu_python_reference(...)` is the easiest runner to start with.
- Switching backends changes execution, not the public kernel shape.
