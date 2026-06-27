# Check Your Checkout

Use these commands to confirm that the current V4 tree is reachable.

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\simple\v4_frontdoor_quickstart.py
py -3 examples\simple\benchmark_app_recipes.py
py -3 scripts\v4_catalog_regression_gate.py --mode dry-run
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/simple/v4_frontdoor_quickstart.py
PYTHONPATH=src:. python examples/simple/benchmark_app_recipes.py
PYTHONPATH=src:. python scripts/v4_catalog_regression_gate.py --mode dry-run
```

These checks run without CUDA by using dry-run paths where needed. They confirm
that the V4 front door, benchmark-app recipes, operator catalog, callback
planner, and example commands are reachable from a clean checkout.

For a broader local check:

```bash
PYTHONPATH=src:. python -m unittest tests.v4_frontdoor_test tests.v4_catalog_regression_gate_test
```
