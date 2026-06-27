# RTDL V4

RTDL V4.0.0 is the current Python eDSL/operator-pushdown surface for writing
reusable RT-core GPU operators from Python.

Use one import:

```python
import rtdsl.v4 as rtdl_v4
```

V4 is a V2/V3 superset: it includes the useful V2.14 and V3 routes, adds V4
operator planning, and presents the system as one current Python package
instead of a stack of old releases.

## What RTDL Does

RTDL helps Python programs express RT-shaped work:

- fixed-radius neighbor queries;
- nearest-witness search;
- ray/triangle hit predicates;
- grouped reductions over hit streams;
- AABB and aggregate-frontier queries;
- constrained custom predicate early-exit for supported Numba predicates.

The application stays in Python. RTDL plans generic RT-shaped operators and
hands device-array work to an explicit partner such as Torch CUDA, CuPy, Numba,
or an RTDL native prepared runner.

## Quick Start

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\simple\v4_frontdoor_quickstart.py
py -3 examples\simple\benchmark_app_recipes.py
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/simple/v4_frontdoor_quickstart.py
PYTHONPATH=src:. python examples/simple/benchmark_app_recipes.py
```

The quickstart prints the current V4 import, supported measured partners, and
the next files to open.

## Current User Paths

| Path | Purpose |
| --- | --- |
| [docs/README.md](docs/README.md) | Current V4 documentation index. |
| [docs/v4_release_notes.md](docs/v4_release_notes.md) | What changed in V4.0.0. |
| [docs/current_v4_status.md](docs/current_v4_status.md) | Current feature and performance snapshot. |
| [docs/learn/operator_catalog.md](docs/learn/operator_catalog.md) | Current operator and workflow surfaces. |
| [docs/learn/partner_choice.md](docs/learn/partner_choice.md) | How to choose Torch, CuPy, Numba, or RTDL native routes. |
| [docs/app_level_benchmark_summary.md](docs/app_level_benchmark_summary.md) | Complete 10-app RT-core benchmark table. |
| [tutorials/current/README.md](tutorials/current/README.md) | Step-by-step learning path. |
| [examples/README.md](examples/README.md) | Runnable simple examples, benchmark apps, and paper-reproduction entrypoints. |

## Performance Snapshot

The current NVIDIA RT-core benchmark table has rows for all 10 promoted
benchmark apps across V2.14, V3.0.2, and V4.0.

The table has two material hot-path rows over V2.14 and similar-speed or
modest-gain rows elsewhere.

The short reading is:

- Triangle counting and Barnes-Hut show material hot-path gains over V2.14.
- RayDB-style, Contact manifold, Hausdorff threshold, Robot collision, RTNN,
  LibRTS spatial index, Spatial RayJoin, and RTDBSCAN are similar-speed or
  modest-gain rows on the current table.
- The V4 custom predicate early-exit workflow is a separate V4-specific
  workflow win, not one of the legacy 10-app rows.

Read the full table before summarizing performance:
[docs/app_level_benchmark_summary.md](docs/app_level_benchmark_summary.md).

## Repository Layout

| Path | Purpose |
| --- | --- |
| `src/rtdsl/` | RTDL Python DSL/runtime source. |
| `examples/simple/` | Current runnable V4 examples. |
| `examples/benchmark_apps/` | Source for the 10 benchmark apps. |
| `examples/paper_reproduction/` | Paper-oriented app entrypoints. |
| `tutorials/current/` | Current V4 tutorial path. |
| `docs/` | Current V4 documentation. |
| `scripts/` | Developer and verification tools. |
| `tests/` | Regression and release gate tests. |
