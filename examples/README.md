# RTDL V4 Examples

Use these examples with the source tree on `PYTHONPATH`.

First run:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\v4\v4_frontdoor_quickstart.py
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/v4/v4_frontdoor_quickstart.py
```

## Current Layout

| Path | Use |
| --- | --- |
| `v4/` | Current V4 user examples and dry-run checks. |
| `current/research_benchmarks/` | Source code for the 10 promoted benchmark apps. |
| `reference/` | Small correctness references for maintainers. |

The default learning path starts in `v4/`, then moves to
`current/research_benchmarks/` when the user wants to study complete apps.

These examples demonstrate the current V4 Python eDSL/operator-pushdown surface,
including measured generic operators, inherited V2/V3 routes, and the
constrained custom predicate early-exit workflow. They do not authorize
whole-application or broad legacy all-app high-performance claims; read
[../docs/app_level_benchmark_summary.md](../docs/app_level_benchmark_summary.md)
for the current V2.14/V3.0.2/V4 app-level result.

## Runnable V4 Examples

PowerShell:

```powershell
py -3 examples\v4\v4_frontdoor_quickstart.py
py -3 examples\v4\benchmark_app_recipes.py
py -3 examples\v4\operator_callback_planning.py --case complex-callback
py -3 examples\v4\fixed_radius_torch_device_arrays.py --dry-run
py -3 examples\v4\closest_hit_grouped_argmin_torch_device_arrays.py --dry-run
py -3 examples\v4\ray_triangle_any_hit_flags_torch_device_arrays.py --dry-run
py -3 examples\v4\primitive_grouped_i64_reduction_torch_device_arrays.py --dry-run
py -3 examples\v4\point_group_nearest_witness_torch_device_arrays.py --dry-run
py -3 examples\v4\ray_triangle_any_hit_weighted_sum_torch_device_arrays.py --dry-run
py -3 examples\v4\custom_predicate_early_exit_planning.py
py -3 examples\v4\aabb_index_all_ops_count.py --dry-run
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/v4/v4_frontdoor_quickstart.py
PYTHONPATH=src:. python examples/v4/benchmark_app_recipes.py
PYTHONPATH=src:. python examples/v4/operator_callback_planning.py --case complex-callback
PYTHONPATH=src:. python examples/v4/fixed_radius_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/v4/closest_hit_grouped_argmin_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/v4/ray_triangle_any_hit_flags_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/v4/primitive_grouped_i64_reduction_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/v4/point_group_nearest_witness_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/v4/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/v4/custom_predicate_early_exit_planning.py
PYTHONPATH=src:. python examples/v4/aabb_index_all_ops_count.py --dry-run
```

## Benchmark Apps

The benchmark app tutorial is
[../tutorials/current/06_benchmark_apps.md](../tutorials/current/06_benchmark_apps.md).
Start with `examples/v4/benchmark_app_recipes.py` before reading the full
benchmark harness source.

Use [../docs/learn/performance_wording.md](../docs/learn/performance_wording.md)
before making any performance statement.
