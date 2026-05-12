# RTDL

RTDL is a Python-hosted ray-tracing DSL/runtime for non-graphical workloads:
spatial search, visibility, nearest-neighbor screening, collision checks, and
database-style summaries.

The core idea is simple: write app-shaped Python code, describe the
traversal-heavy part as an RTDL kernel, and choose a backend such as the Python
reference runner, Embree, or OptiX without rewriting the application.

RTDL is not a renderer or graphics engine. It uses ray-tracing-style
acceleration structures and traversal for application kernels.

The current released version is `v1.8`: the first source-tree Python+RTDL
language release with the tracked native release surface migrated to an
app-agnostic engine contract. Use it from the repository source tree with
`PYTHONPATH=src:.`; do not read this release as a package-install promise,
broad speedup claim, or Python+partner+RTDL claim.

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

## v1.8 Design In One Page

For the v1.8 Python+RTDL boundary, learn RTDL as two layers:

| Layer | What belongs there |
| --- | --- |
| Python app layer | data loading, fixtures, policy, orchestration, reductions, labels, files, plots, and final app answers |
| RTDL engine layer | typed inputs, traversal, refinement, emitted rows, backend dispatch, and app-agnostic native runtime symbols |

This is the key design rule: user programs may be app-shaped Python, but the
native engine must stay app-agnostic. App names such as graph, database,
polygon, or robot can appear in examples and Python compatibility helpers; they
must not become special private engine products.

The fastest way to learn the design is:

1. Run `examples/rtdl_hello_world.py`.
2. Read [Quick Tutorial](docs/quick_tutorial.md).
3. Run `examples/rtdl_feature_quickstart_cookbook.py`.
4. Pick one app from [App And Example Quickstart](docs/app_example_quickstart.md).
5. Read [Current Architecture](docs/current_architecture.md) only after you can
   explain `input -> traverse -> refine -> emit`.

## What RTDL Provides

RTDL is an embedded Python DSL, so it is not a fixed box of apps. You write the
Python program around it. RTDL provides the kernel language, runtime contract,
and backend bridge for the RT-shaped part of that program.

In v1.8, the public building blocks include:

| Building block | What it lets you express |
| --- | --- |
| Kernel shape | `input -> traverse -> refine -> emit` |
| Spatial rows | nearest-neighbor rows, fixed-radius rows, closest-hit rows, any-hit rows, visibility rows |
| Reductions | Python `reduce_rows` plus documented backend reduction contracts where supported |
| IR and lowering | `CompiledKernel` lowering into `RTExecutionPlan` |
| Backend selection | CPU reference, native CPU, Embree, OptiX, HIPRT, Vulkan, Apple RT/MPS RT where documented |

The examples show what users have built with those blocks: Hausdorff distance,
ANN candidate search, outlier detection, DBSCAN, robot screening, Barnes-Hut,
graph visibility, bounded DB-style summaries, road hazard screening, and
segment/polygon summaries. That list is a teaching catalog, not the capacity of
the language.

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

The video is a visual tour of the RTDL idea, not a separate product surface.
It shows a Python-hosted application driving RT-shaped query work while RTDL
keeps the backend engine generic. The goal is to make the design easy to see:
Python owns scene setup and presentation, RTDL owns the traversal/refinement
kernel boundary, and backend choice stays a runtime decision.

Why this demo exists: RTDL is easiest to understand when you can watch the
application layer and kernel layer cooperate. The animation gives a quick
mental model before you dive into the source-tree examples and docs.

How to reproduce the demo locally: run the primary visual demo from the
repository root with the source tree on `PYTHONPATH`. The script lives under
`examples/visual_demo/`; if optional video dependencies are unavailable, use the
other examples first and treat the linked 4K video as the reference recording.

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
