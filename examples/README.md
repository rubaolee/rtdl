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
| `reference/` | Small correctness references for maintainers. |

The default user path is `v4/`. Other example inventories are retained for
maintainers and benchmark development, but they are not the current learning
path.

## Runnable V4 Examples

```powershell
py -3 examples\v4\v4_frontdoor_quickstart.py
py -3 examples\v4\operator_callback_planning.py --case complex-callback
py -3 examples\v4\fixed_radius_torch_device_arrays.py --dry-run
py -3 examples\v4\ray_triangle_any_hit_flags_torch_device_arrays.py --dry-run
py -3 examples\v4\ray_triangle_any_hit_weighted_sum_torch_device_arrays.py --dry-run
py -3 examples\v4\aabb_index_all_ops_count.py --dry-run
```

Use [../docs/learn/performance_wording.md](../docs/learn/performance_wording.md)
before making any performance statement.
