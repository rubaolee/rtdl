# RTDL Examples

This directory has three current entrypoints.

| Path | What to use it for |
| --- | --- |
| `simple/` | Small runnable V4 programs for learning the language. Start here. |
| `benchmark_apps/` | The 10 benchmark apps used to evaluate RTDL. |
| `paper_reproduction/` | Paper-oriented app entrypoints and notes. |

## Start Here

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

## Learn the Benchmark Apps

The tutorial is [../tutorials/current/06_benchmark_apps.md](../tutorials/current/06_benchmark_apps.md).
It explains how each app is built from V4 relations, operators, partners, and
continuations before you open the full app source.

The full benchmark app sources are in `benchmark_apps/`.

## Paper Reproduction

Paper-oriented app entrypoints live in `paper_reproduction/`. They are separate
from the 10-app benchmark suite so users can tell ordinary benchmark apps from
paper-specific reproduction work.
