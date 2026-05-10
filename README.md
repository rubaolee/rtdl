# RTDL

RTDL is a Python-hosted ray-tracing DSL/runtime for non-graphical workloads:
spatial search, visibility, nearest-neighbor screening, collision checks, and
database-style summaries.

The core idea is simple: write app-shaped Python code, describe the
traversal-heavy part as an RTDL kernel, and choose a backend such as the Python
reference runner, Embree, or OptiX without rewriting the application.

RTDL is not a renderer or graphics engine. It uses ray-tracing-style
acceleration structures and traversal for application kernels.

## Start Fast

Run commands from the repository root. RTDL is used directly from the source
tree, so set `PYTHONPATH` before examples and tests.

Bash or zsh:

```bash
PYTHONPATH=src:. python examples/rtdl_hello_world.py
PYTHONPATH=src:. python examples/rtdl_hausdorff_distance_app.py --backend cpu_python_reference
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\rtdl_hello_world.py
python examples\rtdl_hausdorff_distance_app.py --backend cpu_python_reference
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "src;."
python examples/rtdl_hello_world.py
python examples/rtdl_hausdorff_distance_app.py --backend cpu_python_reference
```

## What You Write

An RTDL kernel has the same basic shape across workloads:

```python
import rtdsl as rt

@rt.kernel(backend="rtdl", precision="float_approx")
def visibility_kernel():
    rays = rt.input("rays", rt.Rays, role="probe")
    triangles = rt.input("triangles", rt.Triangles, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_any_hit())
    return rt.emit(hits, fields=["ray_id", "hit"])
```

Python owns the surrounding program: loading data, choosing a backend,
post-processing rows, and writing outputs. RTDL owns the kernel contract and
backend dispatch for supported RT-shaped primitive paths.

## What RTDL Contains

| Capability | Public shape |
| --- | --- |
| Geometry rows | `knn_rows`, `bounded_knn_rows`, `fixed_radius_neighbors`, closest-hit paths |
| Any-hit traversal | `ray_triangle_any_hit`, `visibility_rows`, prepared visibility/count helpers |
| Reductions | `reduce_rows` in Python plus documented backend reduction contracts where supported |
| IR and lowering | `CompiledKernel` lowers to `RTExecutionPlan` |
| Backends | CPU reference, native CPU, Embree, OptiX, HIPRT, Vulkan, Apple RT/MPS RT where documented |
| Apps | Hausdorff, ANN candidate search, outlier detection, DBSCAN, robot screening, Barnes-Hut, graph visibility, DB summaries, road hazard, segment/polygon summaries |

Backend support varies by feature and platform. Start with the portable
`cpu_python_reference` backend, then use Embree or OptiX when your host has the
native dependencies configured.

## Performance Boundary

`--backend optix` means the OptiX backend is selected. It is not by itself a
claim that every app, every phase, or every workload is faster on GPU.

Current measured evidence supports narrow statements: selected long RT-heavy
workloads can show large OptiX speedups over Embree on the same app-level
command surface. Short workloads may be dominated by Python orchestration,
packing, launch overhead, exact continuation, or summary work.

Use exact benchmark artifacts before publishing performance wording.

## Read Next

- [Docs Index](docs/README.md)
- [Public Documentation Map](docs/public_documentation_map.md)
- [Quick Tutorial](docs/quick_tutorial.md)
- [Tutorial Ladder](docs/tutorials/README.md)
- [App And Example Quickstart](docs/app_example_quickstart.md)
- [Application Catalog](docs/application_catalog.md)
- [Feature Guide](docs/rtdl_feature_guide.md)
- [Capability Boundaries](docs/capability_boundaries.md)
- [Current Architecture](docs/current_architecture.md)
- [Performance Model](docs/performance_model.md)
- [IR And Lowering](docs/rtdl/ir_and_lowering.md)

## History And Audit Trail

User-facing docs describe the current RTDL product surface. Project history,
release evidence, review records, and goal archives live separately:

- [History Index](docs/history/README.md)
- [Release Reports](docs/release_reports/)
- [Benchmark And Audit Reports](docs/reports/)

## Demo

- [Watch the public 4K demo video](https://www.youtube.com/watch?v=d3yJB7AmCLM)
- [Short 4K demo URL](https://youtu.be/d3yJB7AmCLM)
- Primary visual demo: `examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py`

## Repository Layout

| Path | Purpose |
| --- | --- |
| `src/rtdsl/` | Python DSL/runtime and backend adapters |
| `examples/` | Public example apps and demos |
| `docs/` | User docs, architecture docs, tutorials, and evidence indexes |
| `docs/reports/` | Benchmark evidence, audits, reviews, and consensus records |
| `tests/` | Regression tests for API, docs, release gates, and claim boundaries |
| `scripts/` | Audits, report generators, benchmark helpers, and intake tools |

For full navigation, start with [docs/README.md](docs/README.md).
