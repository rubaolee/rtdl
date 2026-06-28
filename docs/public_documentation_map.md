# Public Documentation Map

The current V4 documentation path is deliberately short.

## First-Time User Path

1. [Project README](../README.md)
2. [Docs index](README.md)
3. [V4 release notes](v4_release_notes.md)
4. [Current V4 status](current_v4_status.md)
5. [Operator catalog](learn/operator_catalog.md)
6. [Partner choice](learn/partner_choice.md)
7. [Tutorials](../tutorials/current/README.md)
8. [Runnable examples](../examples/README.md)
9. [App-level benchmark summary](app_level_benchmark_summary.md)

## Quick Check Path

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\tutorial_programs\hello_world.py
py -3 examples\tutorial_programs\v4_frontdoor_quickstart.py
py -3 examples\tutorial_programs\sorting_rows.py
py -3 examples\tutorial_programs\operator_primitives.py
py -3 examples\tutorial_programs\partner_choices.py
py -3 examples\tutorial_programs\nearest_neighbor.py
py -3 examples\tutorial_programs\measure_phases.py
py -3 examples\tutorial_programs\point_in_polygon.py
py -3 examples\tutorial_programs\spatial_join_lsi.py
py -3 examples\tutorial_programs\benchmark_app_recipes.py
py -3 scripts\v4_catalog_regression_gate.py --mode dry-run
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/hello_world.py
PYTHONPATH=src:. python examples/tutorial_programs/v4_frontdoor_quickstart.py
PYTHONPATH=src:. python examples/tutorial_programs/sorting_rows.py
PYTHONPATH=src:. python examples/tutorial_programs/operator_primitives.py
PYTHONPATH=src:. python examples/tutorial_programs/partner_choices.py
PYTHONPATH=src:. python examples/tutorial_programs/nearest_neighbor.py
PYTHONPATH=src:. python examples/tutorial_programs/measure_phases.py
PYTHONPATH=src:. python examples/tutorial_programs/point_in_polygon.py
PYTHONPATH=src:. python examples/tutorial_programs/spatial_join_lsi.py
PYTHONPATH=src:. python examples/tutorial_programs/benchmark_app_recipes.py
PYTHONPATH=src:. python scripts/v4_catalog_regression_gate.py --mode dry-run
```
