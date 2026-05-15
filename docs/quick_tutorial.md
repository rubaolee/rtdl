# RTDL Quick Tutorial

RTDL is a Python-hosted ray-tracing DSL/runtime for non-graphical workloads.

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

The productivity win is about authoring burden: fewer backend files, less
duplicated traversal code, and a thinner Python app around optimized kernels. It
is not a promise that every backend is always faster.

For the boundary between "RTDL can do this" and "RTDL is not this whole
system", read [Capability Boundaries](capability_boundaries.md). For exact
current backend support, read
[RTDL Support Matrix](current_main_support_matrix.md) and
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

Windows users should create the same virtual environment with `py -3 -m venv
.venv`, activate it from `cmd.exe` or PowerShell, then run the same `pip`
commands. If `python3 -m venv` fails on Debian/Ubuntu because `ensurepip` is
missing, install `python3-venv` first.

Windows PowerShell setup:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
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

## Step 2.5: Python App, Generic Engine

The current v2.0-facing design is intentionally split:

| You write in Python | RTDL owns in the engine |
| --- | --- |
| app data, labels, command-line flags, policies, reductions, output formatting | typed inputs, traversal, refinement, emitted rows, backend dispatch |

So a Python file may be named for an app, such as Hausdorff, graph analytics, or
database analytics. The RTDL engine underneath should still expose generic
runtime concepts such as nearest candidates, any-hit rows, frontier traversal,
columnar payload scans, or segment-pair intersections.

That is why the tutorial starts with the portable `cpu_python_reference`
backend: it teaches the public program shape before you think about native
libraries or performance.

## Backend Names In Two Places

RTDL uses the word "backend" in two related but different places:

| Place | Meaning |
| --- | --- |
| `@rt.kernel(backend="rtdl")` | The kernel is authored for the RTDL language and lowering contract. Use this spelling for new kernels. |
| `--backend cpu_python_reference`, `embree`, `optix`, ... | The runtime execution engine selected by an example or app. |

For learning, start with `cpu_python_reference`; it is the portable learning
backend and avoids native build or GPU setup. Use `cpu` when you intentionally
want the native CPU validation path, and use Embree/OptiX/HIPRT/Vulkan/Apple RT
only after checking backend support and local dependencies.

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
For the full command archive, use [Release-Facing Examples](release_facing_examples.md).
For app boundaries and backend support, use [Application Catalog](application_catalog.md)
and [App Engine Support Matrix](app_engine_support_matrix.md).

Repository paths: `docs/application_catalog.md` and
`docs/app_engine_support_matrix.md`. Current app entry points include
`examples/rtdl_database_analytics_app.py` and
`examples/rtdl_apple_rt_demo_app.py`; older scenario-specific DB and Apple RT
files are compatibility helpers rather than the recommended public start.

## Backend And Claim Boundaries

Portable first-run backends:

- `cpu_python_reference` is pure Python and should run on every OS.
- `cpu` auto-builds the native C oracle library on first use.
- `embree` auto-builds/probes `build/librtdl_embree.*` on first use when the
  host has Embree headers/libraries available.

Optional native/backend build commands:

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
Current feature terms you will see in public docs include
`ray_triangle_any_hit`, `visibility_rows`, `reduce_rows`, and stable
primitive/reduction contract names `ANY_HIT`, `COUNT_HITS`,
`REDUCE_FLOAT(MIN|MAX|SUM)`, and `REDUCE_INT(COUNT|SUM)`. The public
`reduce_rows` helper is a deterministic Python helper over emitted rows; do not
read it as a blanket native-backend reduction speedup claim. OptiX, Embree, and
HIPRT have released native early-exit any-hit coverage. Vulkan and Apple RT
also have released bounded paths, but backend support varies by predicate and
platform.

## Three Things To Remember

- The kernel describes the query; Python runs the surrounding program.
- `rt.run_cpu_python_reference(...)` is the easiest runner to start with.
- Switching backends changes execution, not the public kernel shape.

## Common First-Run Problems

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `ModuleNotFoundError: No module named 'rtdsl'` | `PYTHONPATH` is not set from the repository root | Set `PYTHONPATH=src:.` on Bash/zsh or `$env:PYTHONPATH = "src;."` in PowerShell |
| Native or GPU backend fails to load | Backend library, SDK, driver, or compiler is not configured | Rerun with `--backend cpu_python_reference`, then check backend-specific setup docs |
| Kernel compiles but runtime input fails | Host-side Python data shape does not match the `rt.input(...)` names and geometry fields | Copy the input shape from the closest public example before generalizing |
| Windows prints `Could not find platform independent libraries <prefix>` but output is correct | Local Python installation noise | Treat RTDL as passing if the expected example output appears; fix Python installation only if imports fail |
