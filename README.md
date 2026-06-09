# RTDL

RTDL is a Python-hosted ray-tracing DSL/runtime for non-graphical workloads:
spatial search, visibility, nearest-neighbor screening, collision checks, and
database-style summaries.

The core idea is simple: write app-shaped Python code, describe the
traversal-heavy part as an RTDL kernel, and choose a backend such as the Python
reference runner, Embree, or OptiX without rewriting the application.

RTDL is not a renderer or graphics engine. It uses ray-tracing-style
acceleration structures and traversal for application kernels.

This documentation is written for the current v2.10 source-tree RTDL surface:
Python+partner+RTDL over a generic, app-agnostic native engine, with prepared
execution and a tested 10-app benchmark matrix. Use RTDL from the repository
source tree with `PYTHONPATH=src:.`; do not read any current doc
as a package-install promise, automatic partner-selection promise, general
device-residency/zero-copy product claim, or broad speedup claim.

## Start Fast

Run commands from the repository root. RTDL is used directly from the source
tree, so set `PYTHONPATH` before examples and tests.

Linux/pod native smoke prerequisites:

```bash
apt-get install -y libgeos-dev pkg-config libembree-dev
python -m pip install numpy pillow imageio imageio-ffmpeg  # Dependency install only; this does not install RTDL
```

Use a virtual environment if your Python distribution blocks system-wide
`pip`. The portable `cpu_python_reference` examples need fewer native
dependencies, but the current full runnable surface includes native CPU/Embree
paths and visual demos.

Bash or zsh:

```bash
PYTHONPATH=src:. python examples/v2_0/getting_started/rtdl_hello_world.py
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py --backend cpu_python_reference
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\v2_0\getting_started\rtdl_hello_world.py
python examples\v2_0\research_benchmarks\hausdorff_xhd\rtdl_hausdorff_distance_app.py --backend cpu_python_reference
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "src;."
python examples/v2_0/getting_started/rtdl_hello_world.py
python examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py --backend cpu_python_reference
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

## Design In One Page

Learn RTDL as two layers:

| Layer | What belongs there |
| --- | --- |
| Python app layer | data loading, fixtures, policy, orchestration, reductions, labels, files, plots, and final app answers |
| RTDL engine layer | typed inputs, traversal, refinement, emitted rows, backend dispatch, and app-agnostic native runtime symbols |

This is the key design rule: user programs may be app-shaped Python, but the
native engine must stay app-agnostic. App names such as graph, database,
polygon, or robot can appear in examples and Python compatibility helpers; they
must not become special private engine products.

The fastest way to learn the design is:

1. Run `examples/v2_0/getting_started/rtdl_hello_world.py`.
2. Read [Quick Tutorial](docs/quick_tutorial.md).
3. Run `examples/v2_0/getting_started/rtdl_feature_quickstart_cookbook.py`.
4. Pick one app from [App And Example Quickstart](docs/app_example_quickstart.md).
5. Read [Current Architecture](docs/current_architecture.md) only after you can
   explain `input -> traverse -> refine -> emit`.

## What RTDL Provides

RTDL is an embedded Python DSL, so it is not a fixed box of apps. You write the
Python program around it. RTDL provides the kernel language, runtime contract,
and backend bridge for the RT-shaped part of that program.

Current public building blocks include:

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

## v2.10 Source-Tree Surface

RTDL v2.10 is the current source-tree surface for this branch. It keeps the
Python+partner+RTDL language boundary, documents the promoted benchmark-app
portfolio, adds primitive discovery and prepared-execution guidance, and records
the app-agnostic primitive lessons from the benchmark wave.

The current matrix separates promoted benchmark apps from learner/example apps.
Promoted benchmarks are reconstruction instruments for RTDL language/runtime
design, not broad paper-reproduction or whole-application speedup claims.

Do not read v2.10 as a package-install promise, broad RT-core claim, arbitrary
PyTorch/CuPy/Numba acceleration claim, arbitrary polygon overlay claim, or proof
that every user program is faster. For the exact positive and negative rule, read
[Partner Acceleration Boundaries](docs/partner_acceleration_boundaries.md).

The v2.10 partner rule is user-chosen and evidence-gated:

- use fused RTDL primitives first when they exactly express the work;
- choose a partner explicitly when custom continuation logic is needed;
- prefer CuPy for mature CUDA-array/library continuations;
- use Numba for measured custom CUDA-style continuations such as selected
  compact-mask and grouped-reduction rows;
- keep Triton paused for recommended paths until same-contract timing proves it
  should return.

For the current partner-choice guide, read
[Choosing A Partner For Custom Logic](docs/learn/partner_choice_for_custom_logic.md)
and the [Benchmark Partner Reference Matrix](docs/learn/benchmark_partner_reference_matrix.md).
For the historical v2.8 10-app matrix, see
[Goal3518](docs/reports/goal3518_v2_8_benchmark_matrix_refresh_2026-06-05.md).
For the current v2.10 benchmark adequacy and AMD/HIPRT readiness position, see
[Goal3786](docs/reports/goal3786_current_benchmark_adequacy_after_hiprt_closeout_2026-06-07.md).

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
- [Choosing A Partner For Custom Logic](docs/learn/partner_choice_for_custom_logic.md)
- [Application Catalog](docs/application_catalog.md)
- [Feature Guide](docs/rtdl_feature_guide.md)
- [Engine Feature Support Contract](docs/features/engine_support_matrix.md)
- [App Engine Support Matrix](docs/app_engine_support_matrix.md)
- [Current Support Matrix](docs/current_main_support_matrix.md)
- [Capability Boundaries](docs/capability_boundaries.md)
- [Partner Acceleration Boundaries](docs/partner_acceleration_boundaries.md)
- [Current Architecture](docs/current_architecture.md)
- [Performance Model](docs/performance_model.md)
- [IR And Lowering](docs/rtdl/ir_and_lowering.md)

## History And Audit Trail

User-facing docs describe the current RTDL product surface. Project history,
release evidence, review records, and goal archives live separately:

- [History Index](docs/history/README.md)
- [Version Archive Notes](docs/history/version_archive_notes.md)
- [Historical v2.6 Evidence Archive](docs/release_reports/v2_6/README.md)
- [Historical v2.3 Evidence Archive](docs/release_reports/v2_3/README.md)
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

Root-level generated artifacts, archived proof apps, and schema files are kept
inside the appropriate source, script, example, or history directories rather
than as separate front-door folders.

For full navigation, start with [docs/README.md](docs/README.md).
