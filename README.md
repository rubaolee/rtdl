# RTDL

RTDL is a language/runtime for expressing workloads that can be accelerated by
ray tracing, including workloads that map well to ray-tracing cores on modern
GPUs.

It gives you:

- built-in workload primitives for released workload families in the current repository
- a Python-hosted DSL for writing kernels
- multiple execution backends behind one public surface
- a clean model where RTDL owns the heavy accelerated work and Python owns the surrounding application logic

The current released surface now spans geometric, nearest-neighbor, and graph
workloads, but the language goal is broader than any one workload family alone.

This branch also carries a bounded `v0.7` development line for DB-style
analytical workloads. That `v0.7` line is not the current tagged release on
`main`.

RTDL is not a general-purpose renderer or graphics engine.  
The visual demo in this repository exists as a proof that the same RTDL compute
core can power a bounded Python application.

## Version Status At A Glance

- current released version: `v0.6.1`
- current active branch line here: bounded `v0.7` RT DB work
- current released graph surface today:
  - `bfs`
  - `triangle_count`
- current bounded `v0.7` DB branch surface:
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
- current `v0.6.1` additions over `v0.5.0`:
  - the first released RTDL graph workload family
  - RTDL-kernel graph execution across CPU/oracle, Embree, OptiX, and Vulkan
  - PostgreSQL-backed graph correctness anchoring

For exact status:

- [RTDL v0.6 Release Statement](docs/release_reports/v0_6/release_statement.md)
- [RTDL v0.6 Support Matrix](docs/release_reports/v0_6/support_matrix.md)
- [RTDL v0.7 Branch Statement](docs/release_reports/v0_7/release_statement.md)
- [RTDL v0.7 Branch Support Matrix](docs/release_reports/v0_7/support_matrix.md)
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

## OS Support At A Glance

Current honest platform story:

- `Linux`:
  - primary validation platform
  - current graph correctness/performance claims are made here
- `Windows`:
  - bounded support in the current `v0.6.1` line
  - graph validation is part of the bounded support story
- `local macOS`:
  - bounded support in the current `v0.6.1` line
  - focused regression and local checks

If you want the exact current boundary instead of the short front-page summary,
use:

- [RTDL v0.6 Support Matrix](docs/release_reports/v0_6/support_matrix.md)

## See It Quickly

Primary front-door links:

- [Watch The Public 4K Demo Video](https://youtu.be/d3yJB7AmCLM)
- [Quick Tutorial](docs/quick_tutorial.md)
- [Tutorials](docs/tutorials/README.md)
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

Then try the released graph line:

```bash
PYTHONPATH=src:. python examples/rtdl_graph_bfs.py --backend cpu_python_reference
PYTHONPATH=src:. python examples/rtdl_graph_triangle_count.py --backend cpu_python_reference
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\rtdl_hello_world.py
python examples\rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 16
python examples\rtdl_graph_bfs.py --backend cpu_python_reference
python examples\rtdl_graph_triangle_count.py --backend cpu_python_reference
```

PowerShell:

```powershell
$env:PYTHONPATH="src;."
python examples/rtdl_hello_world.py
python examples/rtdl_segment_polygon_hitcount.py --backend cpu_python_reference --copies 16
python examples/rtdl_graph_bfs.py --backend cpu_python_reference
python examples/rtdl_graph_triangle_count.py --backend cpu_python_reference
```

Notes:

- expected Python floor: `3.10+`
- local package name: `rtdsl`
- if your shell only provides `python3`, substitute `python3`
- `PYTHONPATH=src:.` is what makes the local `src/rtdsl/` package importable
- `cpu` auto-builds the native C oracle library on first use
- `embree` runs when the Embree backend is present
- on Linux with a configured GPU stack, `optix` and `vulkan` can run after the backend libraries are available

Optional Linux GPU backend build step:

```bash
make build-optix
make build-vulkan
```

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

If you want the current bounded DB branch line:

- [RTDL v0.7 Branch Statement](docs/release_reports/v0_7/release_statement.md)
- [RTDL v0.7 Branch Support Matrix](docs/release_reports/v0_7/support_matrix.md)

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

- `v0.6.1`

Current active branch line:

- bounded `v0.7` RT DB work

Released workload surface:

- `bfs`
- `triangle_count`

Release and preview layers inside the current repository:

- `v0.2.0`: stable released segment/polygon and overlap workload family
- `v0.3.0`: released proof-of-capability demo/application layer on the same RTDL core
- `v0.4.0`: released nearest-neighbor workload expansion
- `v0.5.0`: released 3D nearest-neighbor and multi-backend expansion
- `v0.6.1`: released corrected RT graph line
- `v0.7`: active bounded DB branch line, not yet tagged as the new mainline release

Current public demo artifact:

- [RTDL 4K hidden-star demo video](https://youtu.be/d3yJB7AmCLM)

For exact backend/workload status, use:

- [RTDL v0.6 Release Statement](docs/release_reports/v0_6/release_statement.md)
- [RTDL v0.6 Support Matrix](docs/release_reports/v0_6/support_matrix.md)
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

## Why RTDL Exists

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
- [Quick Tutorial](docs/quick_tutorial.md)
- [Feature Homes](docs/features/README.md)
- [RTDL v0.4 Release Package](docs/release_reports/v0_4/README.md)
