# RTDL V3.0.0

RTDL V3.0.0 is the current RTDL user surface.

## What RTDL Is

RTDL is a Python-hosted ray-tracing DSL/runtime for non-graphical workloads:
spatial search, nearest-neighbor screening, collision checks, graph-style
queries, and database-like summaries.

The core contract is simple:

```text
Python owns the application.
RTDL expresses RT-shaped kernels and prepared execution.
Backends and partners are explicit choices, not hidden promises.
```

The Python package is `rtdsl`.

## What V3.0.0 Adds

The current user-facing V3.0.0 surface is:

- a single Python-hosted RTDL programming path;
- prepared execution and runtime-trunk APIs used by current examples;
- explicit backend and partner boundaries;
- source-tree checks that tell users whether the checkout is usable;
- exact, scoped performance wording for measured rows.

## Start Here

Run from the repository root:

```powershell
$env:PYTHONPATH = "src;."
py -3 scripts\rtdl_source_tree_doctor.py --run-smoke
py -3 examples\current\getting_started\rtdl_hello_world.py
```

On Linux or macOS:

```bash
PYTHONPATH=src:. python scripts/rtdl_source_tree_doctor.py --run-smoke
PYTHONPATH=src:. python examples/current/getting_started/rtdl_hello_world.py
```

Expected hello-world output:

```text
hello, world
```

## Current User Paths

| Path | Use |
| --- | --- |
| [docs/README.md](docs/README.md) | Small current documentation index. |
| [tutorials/current/README.md](tutorials/current/README.md) | Short V3.0.0 learning path. |
| [examples/current/getting_started/](examples/current/getting_started/) | Runnable first examples. |
| [docs/learn/performance_wording.md](docs/learn/performance_wording.md) | Performance wording guide. |
| [docs/learn/source_tree_doctor.md](docs/learn/source_tree_doctor.md) | Checkout sanity-check guide. |

## Repository Layout

| Path | Purpose |
| --- | --- |
| `src/rtdsl/` | RTDL Python DSL/runtime source. |
| `examples/current/` | Current runnable examples and benchmark code inventory. |
| `tutorials/current/` | Clean V3.0.0 tutorial path. |
| `docs/` | Clean current V3.0.0 documentation. |
| `scripts/` | Developer and verification tools. |
| `tests/` | Regression and gate tests. |
