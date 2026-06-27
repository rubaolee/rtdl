# Public Documentation Map

The current V4 public documentation is deliberately short and current-only.

## First-Time User Path

1. [Project README](../README.md)
2. [Current V4 Status](current_v4_status.md)
3. [Release Notes](v4_release_notes.md)
4. [Operator Catalog](learn/operator_catalog.md)
5. [Partner Choice](learn/partner_choice.md)
6. [Tutorials](../tutorials/current/README.md)
7. [Runnable Examples](../examples/README.md)
8. [App-Level Benchmark Summary](app_level_benchmark_summary.md)
9. [Performance Wording](learn/performance_wording.md)

## Quick Check Path

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\v4\v4_frontdoor_quickstart.py
py -3 examples\v4\benchmark_app_recipes.py
py -3 examples\v4\operator_callback_planning.py --case complex-callback
py -3 scripts\v4_catalog_regression_gate.py --mode dry-run
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/v4/v4_frontdoor_quickstart.py
PYTHONPATH=src:. python examples/v4/benchmark_app_recipes.py
PYTHONPATH=src:. python examples/v4/operator_callback_planning.py --case complex-callback
PYTHONPATH=src:. python scripts/v4_catalog_regression_gate.py --mode dry-run
```

## Evidence Path

The public learning path is the numbered list above. Compact evidence and
release files exist for maintainers, but new users do not need them to learn or
run V4.
