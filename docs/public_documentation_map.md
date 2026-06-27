# Public Documentation Map

The current V4 public documentation is deliberately short and current-only.

## First-Time User Path

1. [Project README](../README.md)
2. [Current V4 Status](current_v4_status.md)
3. [Operator Catalog](learn/operator_catalog.md)
4. [Tutorials](../tutorials/current/README.md)
5. [Runnable Examples](../examples/README.md)
6. [App-Level Benchmark Summary](app_level_benchmark_summary.md)
7. [Performance Wording](learn/performance_wording.md)

## Quick Check Path

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\v4\v4_frontdoor_quickstart.py
py -3 examples\v4\operator_callback_planning.py --case complex-callback
py -3 scripts\v4_catalog_regression_gate.py --mode dry-run
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/v4/v4_frontdoor_quickstart.py
PYTHONPATH=src:. python examples/v4/operator_callback_planning.py --case complex-callback
PYTHONPATH=src:. python scripts/v4_catalog_regression_gate.py --mode dry-run
```

## Audit Path

The public learning path does not require old planning notes or review packets.
Maintainer audit material is retained under `history/` and evidence-only
directories. Treat those files as provenance, not current user guidance.
