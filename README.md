# RTDL

RTDL is a language/runtime for expressing workloads that can be accelerated by
ray tracing, including workloads that map well to ray-tracing cores on modern
GPUs.

It gives you:

- built-in workload primitives for released workload families in the current repository
- a Python-hosted DSL for writing kernels
- multiple execution backends behind one public surface
- a clean model where RTDL owns the heavy accelerated work and Python owns the surrounding application logic

The current released surface now spans geometric, nearest-neighbor, graph, and
bounded database-style analytical workloads, but the language goal is broader
than any one workload family alone.

The current `main` branch carries the bounded `v0.7.0` release line for
DB-style analytical workloads.

RTDL is not a general-purpose renderer or graphics engine.
The visual demo in this repository exists as a proof that the same RTDL compute
core can power a bounded Python application.

## Why RTDL Is Useful

Modern ray-tracing workloads usually require the same hard plumbing before the
real idea appears: shape data into backend buffers, build acceleration
structures, launch backend-specific kernels, refine candidate hits, normalize
result rows, and keep CPU/GPU/RT-backend variants consistent.

RTDL's authoring target is a **10x reduction in workload-writing burden**. That
is an engineering-productivity target, not an unbounded speedup claim: you write
one compact kernel shape, keep application logic in Python, and let RTDL own the
accelerated traversal/refinement path across the supported backends.

The recurring mental model is:

1. declare `probe` and `build` inputs
2. run `traverse(..., accel="bvh")`
3. run `refine(...)` for exact workload semantics
4. `emit(...)` stable application rows

That same shape now covers released geometry, nearest-neighbor, graph, and
bounded DB-style analytical workloads.

## Version Status At A Glance

- current released version: `v0.7.0`
- current mainline release here: bounded `v0.7.0` RT DB work
- current released graph surface today:
  - `bfs`
  - `triangle_count`
- current bounded `v0.7.0` DB release surface:
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
  - native prepared DB dataset reuse on Embree, OptiX, and Vulkan
  - app-level and kernel-form DB demos
  - release-readiness and staging-authorization evidence through Goal 492
- previous `v0.6.1` additions over `v0.5.0`:
  - the first released RTDL graph workload family
  - RTDL-kernel graph execution across CPU/oracle, Embree, OptiX, and Vulkan
  - PostgreSQL-backed graph correctness anchoring

For exact status:

- [RTDL v0.6 Release Statement](docs/release_reports/v0_6/release_statement.md)
- [RTDL v0.6 Support Matrix](docs/release_reports/v0_6/support_matrix.md)
- [RTDL v0.7 Release Statement](docs/release_reports/v0_7/release_statement.md)
- [RTDL v0.7 Support Matrix](docs/release_reports/v0_7/support_matrix.md)
- [RTDL v0.5 Release Statement](docs/release_reports/v0_5/release_statement.md)
- [RTDL v0.5 Support Matrix](docs/release_reports/v0_5/support_matrix.md)
- [RTDL v0.4 Release Statement](docs/release_reports/v0_4/release_statement.md)
- [RTDL v0.4 Support Matrix](docs/release_reports/v0_4/support_matrix.md)

## Backend Names In Plain English

RTDL uses several backends behind one public kernel surface:

- `cpu_python_reference`:
  - the slowest but clearest Python truth path
- `CPU/oracle`:
  - RTDL's compiled C/C++ correctness baseline
  - this is what "oracle" means in this repo
- `Embree`:
  - the Intel CPU ray-tracing backend
  - current accelerated CPU backend
- `OptiX`:
  - the NVIDIA GPU ray-tracing backend
  - one of the main high-performance graph backends in `v0.6.1`
- `Vulkan`:
  - the Vulkan ray-tracing GPU backend
  - portable GPU path
  - one of the main high-performance graph backends in `v0.6.1`
- `PostGIS` / `PostgreSQL`:
  - not RTDL backends
  - used as external correctness/timing anchors for some workload families
  - for the `v0.7.0` DB release, PostgreSQL is the Linux correctness and
    repeated-query performance baseline

## OS Support At A Glance

Current honest platform story:

- `Linux`:
  - primary validation platform
  - current graph correctness/performance claims are made here
- `Windows`:
  - bounded support for the released graph/API/Embree surface
  - graph validation is part of the bounded support story
- `local macOS`:
  - bounded local support for portable Python/native paths
  - focused regression and local checks

If you want the exact current boundary instead of the short front-page summary,
use:

- [RTDL v0.6 Support Matrix](docs/release_reports/v0_6/support_matrix.md)
- [RTDL v0.7 Support Matrix](docs/release_reports/v0_7/support_matrix.md)

## See It Quickly

Primary front-door links:

- [Watch The Public 4K Demo Video](https://youtu.be/d3yJB7AmCLM)
- [Current Architecture](docs/current_architecture.md)
- [Quick Tutorial](docs/quick_tutorial.md)
- [Tutorials](docs/tutorials/README.md)
- [Feature Quickstart Cookbook](docs/tutorials/feature_quickstart_cookbook.md)
- [Release-Facing Examples](docs/release_facing_examples.md)
- [RTDL v0.4 Application Examples](docs/v0_4_application_examples.md)
- [Documentation Index](docs/README.md)

Demo preview:

<p>
  <a href="https://www.youtube.com/watch?v=d3yJB7AmCLM">
    <img
      src="docs/assets/rtdl_visual_demo_thumb.png"
      alt="RTDL demo video thumbnail"
      width="240"
    />
  </a>
</p>

<p>
  <a href="https://www.youtube.com/watch?v=d3yJB7AmCLM"><strong>Open the RTDL 4K demo video on YouTube</strong></a>
</p>

## Start In Two Minutes

Clone and enter the repository:

```bash
git clone https://github.com/rubaolee/rtdl.git
cd rtdl
```

Create a local virtual environment and install the basic Python requirements:

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

PowerShell:

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If `python3 -m venv` fails on Debian/Ubuntu because `ensurepip` is unavailable,
install the OS package first:

```bash
sudo apt install python3-venv
```

Run the smallest example:

```bash
PYTHONPATH=src:. python examples/rtdl_hello_world.py
```

Then run one released workload:

```bash
PYTHONPATH=src:. python examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 16
```

Then run the feature cookbook when you want a compact recipe for every public
feature:

```bash
PYTHONPATH=src:. python examples/rtdl_feature_quickstart_cookbook.py
```

Then try the released graph line:

```bash
PYTHONPATH=src:. python examples/rtdl_graph_bfs.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_graph_triangle_count.py --backend cpu_python_reference
```

Then try the bounded `v0.7.0` DB release line:

```bash
PYTHONPATH=src:. python examples/rtdl_db_conjunctive_scan.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_db_grouped_count.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_db_grouped_sum.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_v0_7_db_app_demo.py --backend auto
PYTHONPATH=src:. python examples/rtdl_v0_7_db_kernel_app_demo.py --backend auto
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\rtdl_hello_world.py
python examples\rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 16
python examples\rtdl_graph_bfs.py --backend cpu_python_reference
python examples\rtdl_graph_triangle_count.py --backend cpu_python_reference
python examples\rtdl_db_conjunctive_scan.py --backend cpu_python_reference
python examples\rtdl_db_grouped_count.py --backend cpu_python_reference
python examples\rtdl_db_grouped_sum.py --backend cpu_python_reference
python examples\rtdl_v0_7_db_app_demo.py --backend auto
python examples\rtdl_v0_7_db_kernel_app_demo.py --backend auto
```

PowerShell:

```powershell
$env:PYTHONPATH="src;."
python examples/rtdl_hello_world.py
python examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 16
python examples/rtdl_graph_bfs.py --backend cpu_python_reference
python examples/rtdl_graph_triangle_count.py --backend cpu_python_reference
python examples/rtdl_db_conjunctive_scan.py --backend cpu_python_reference
python examples/rtdl_db_grouped_count.py --backend cpu_python_reference
python examples/rtdl_db_grouped_sum.py --backend cpu_python_reference
python examples/rtdl_v0_7_db_app_demo.py --backend auto
python examples/rtdl_v0_7_db_kernel_app_demo.py --backend auto
```

Notes:

- expected Python floor: `3.10+`
- local package name: `rtdsl`
- if your shell only provides `python3`, substitute `python3`
- `PYTHONPATH=src:.` is what makes the local `src/rtdsl/` package importable
- `cpu` auto-builds the native C oracle library on first use
- `embree` auto-builds/probes `build/librtdl_embree.*` on first use when the
  host has Embree headers/libraries available
- on Linux with a configured GPU stack, `optix` and `vulkan` can run after the backend libraries are available

Optional Embree backend build/probe step:

```bash
make build-embree
```

Optional Linux GPU backend build step:

```bash
make build-optix
make build-vulkan
```

Windows Embree note: install or unpack Embree for x64, set
`RTDL_EMBREE_PREFIX` to that Embree prefix, and set `RTDL_VCVARS64` if Visual
Studio Build Tools are not in the default location. A binary Windows snapshot
must either include the matching `build/librtdl_embree.dll` from this checkout
or allow first-use rebuild from source; stale DLLs are rejected when required
exports such as `rtdl_embree_run_fixed_radius_neighbors` are missing.

## Choose Your Path

If you are new:

1. [Quick Tutorial](docs/quick_tutorial.md)
2. [Tutorials](docs/tutorials/README.md)
3. [Feature Homes](docs/features/README.md)

If you want the released core workloads:

- [RTDL v0.2 User Guide](docs/v0_2_user_guide.md)
- [Release-Facing Examples](docs/release_facing_examples.md)

If you want the newest released graph line:

- [RTDL v0.6 Release Statement](docs/release_reports/v0_6/release_statement.md)
- [RTDL v0.6 Support Matrix](docs/release_reports/v0_6/support_matrix.md)

If you want the current bounded DB release line:

- [RTDL v0.7 Release Statement](docs/release_reports/v0_7/release_statement.md)
- [RTDL v0.7 Support Matrix](docs/release_reports/v0_7/support_matrix.md)

If you want the earlier released nearest-neighbor line:

- [RTDL v0.4 Application Examples](docs/v0_4_application_examples.md)
- [RTDL v0.5 Release Statement](docs/release_reports/v0_5/release_statement.md)
- [RTDL v0.5 Support Matrix](docs/release_reports/v0_5/support_matrix.md)

If you want the application/demo side:

- [examples/visual_demo/rtdl_lit_ball_demo.py](examples/visual_demo/rtdl_lit_ball_demo.py)
- [examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py](examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py)
- [examples/visual_demo/render_hidden_star_chunked_video.py](examples/visual_demo/render_hidden_star_chunked_video.py)
- [Hidden-Star 4K Render Work Report](docs/reports/hidden_star_4k_render_work_report_2026-04-11.md)

## Current Release State

Current release:

- `v0.7.0`

Current mainline release line:

- bounded `v0.7.0` RT DB work

Newest released graph workload surface:

- `bfs`
- `triangle_count`

Release and preview layers inside the current repository:

- `v0.2.0`: stable released segment/polygon and overlap workload family
- `v0.3.0`: released proof-of-capability demo/application layer on the same RTDL core
- `v0.4.0`: released nearest-neighbor workload expansion
- `v0.5.0`: released 3D nearest-neighbor and multi-backend expansion
- `v0.6.1`: released corrected RT graph line
- `v0.7.0`: released bounded DB line
  - current native prepared DB dataset work is validated on Linux across
    Embree, OptiX, Vulkan, and PostgreSQL for bounded synthetic repeated-query
    gates
  - current canonical performance wording is Goal 452: against the best
    PostgreSQL modes tested so far, query-only results are mixed, while
    setup-plus-10-query total time favors RTDL in the measured Linux evidence
  - release-readiness evidence is Goal 492: the package was held until explicit
    release authorization, with `rtdsl_current.tar.gz` as the only default
    staging exclusion

Current public demo artifact:

- [RTDL 4K hidden-star demo video](https://youtu.be/d3yJB7AmCLM)

For exact backend/workload status, use:

- [RTDL v0.6 Release Statement](docs/release_reports/v0_6/release_statement.md)
- [RTDL v0.6 Support Matrix](docs/release_reports/v0_6/support_matrix.md)
- [RTDL v0.7 Release Statement](docs/release_reports/v0_7/release_statement.md)
- [RTDL v0.7 Support Matrix](docs/release_reports/v0_7/support_matrix.md)
- [RTDL v0.5 Release Statement](docs/release_reports/v0_5/release_statement.md)
- [RTDL v0.5 Support Matrix](docs/release_reports/v0_5/support_matrix.md)

## What RTDL Contains

The repository currently includes:

- a Python-hosted DSL for authoring kernels
- compiler/lowering code
- released workload primitives
- native runtime layers for:
  - CPU/oracle: compiled C/C++ correctness baseline
  - Embree: Intel CPU ray-tracing backend
  - OptiX: NVIDIA GPU ray-tracing backend
  - Vulkan: Vulkan ray-tracing GPU backend
- examples ranging from smallest first-run scripts to RTDL-plus-Python demos

The public examples are organized as:

- top-level `examples/`: first-run and release-facing examples
- `examples/reference/`: readable reference kernels and fixture builders
- `examples/generated/`: generated bundles and preserved generated output
- `examples/visual_demo/`: RTDL-plus-Python application demos
- `examples/internal/`: preserved internal and historical artifacts

## What The Video Shows

The visual demo shows the correct RTDL application boundary:

- RTDL handles the accelerated compute/query core
- Python handles scene setup, animation, shading, and output

That is why the demo belongs here. It is not a product pivot toward graphics.
It is a proof that RTDL can act as the query engine inside a larger Python
application.

## Research Context

Ray-tracing hardware and software are very good at hierarchical traversal,
intersection, and search-style computation. RTDL uses that machinery for
accelerated workloads beyond image rendering alone, with the current released
surface strongest on geometric and nearest-neighbor work.

The motivating research target in this repository is:

- Liang Geng, Rubao Lee, and Xiaodong Zhang,
  *RayJoin: Fast and Precise Spatial Join*,
  Proceedings of the 38th ACM International Conference on Supercomputing
  (ICS 2024),
  DOI: [10.1145/3650200.3656610](https://dl.acm.org/doi/10.1145/3650200.3656610)

RTDL asks the next question: can these accelerated workloads be expressed
through a programmable language/runtime surface while staying correct across
multiple backends?

For broader context:

- [Workloads And Research Foundations](docs/workloads_and_research_foundations.md)
- [Future Ray-Tracing Directions](docs/future_ray_tracing_directions.md)

## Current Limits

Important honesty boundaries:

- the current released surface is strongest on geometric and nearest-neighbor workloads
- visual demos are bounded RTDL-plus-Python applications, not a renderer claim
- backend/platform availability is not identical on every machine
- Linux remains the primary validation platform
- PostGIS is an external indexed comparison baseline, not an RTDL backend
- PostgreSQL is the external baseline for the bounded `v0.7.0` DB release; RTDL is
  still not a DBMS and does not execute arbitrary SQL
- RTDL is not a DBMS
- `v0.7` DB performance claims are bounded to the tested Linux synthetic
  workloads; Goal 452 is the canonical comparison against best-tested
  PostgreSQL modes, not an exhaustive PostgreSQL tuning claim
- `v0.7.0` is the current bounded DB release; release claims remain limited to
  the documented v0.7 support matrix and performance boundary

For the precise current release boundary, use the release statement and support
matrix instead of inferring from the front page.

## Repository Layout

Key locations:

- `src/rtdsl/`: Python package and runtime surface
- `src/native/`: native backend implementations
- `examples/`: runnable examples
- `docs/`: tutorials, release reports, references, and history
- `tests/`: automated verification

Best next pages:

- [Documentation Index](docs/README.md)
- [Current Architecture](docs/current_architecture.md)
- [Quick Tutorial](docs/quick_tutorial.md)
- [Feature Homes](docs/features/README.md)
- [RTDL v0.7 Release Package](docs/release_reports/v0_7/README.md)
- [Complete History Map](history/COMPLETE_HISTORY.md)
