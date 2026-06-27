# Checkout Sanity Checks

For V4, the quickest portable check is the V4 front-door quickstart plus the
catalog regression dry-run gate.

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

These checks run without CUDA by using dry-run paths for GPU examples. They
verify that the V4 front door, benchmark-app recipe planner, operator catalog,
callback planner, and example commands are reachable from a clean checkout.

For deeper checks, use the broader V4 tests:

```bash
PYTHONPATH=src:. python -m unittest tests.v4_frontdoor_test tests.v4_catalog_regression_gate_test
```

For release readiness, use `scripts/v4_release_clean_checkout_gate.py` after
the tree is committed and the release tag is in place.
