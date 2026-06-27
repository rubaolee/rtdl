# Simple RTDL V4 Examples

These scripts are small learning programs. They run from the repository root
with `PYTHONPATH=src:.`.

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\simple\v4_frontdoor_quickstart.py
py -3 examples\simple\benchmark_app_recipes.py
py -3 examples\simple\operator_callback_planning.py --case complex-callback
py -3 examples\simple\fixed_radius_torch_device_arrays.py --dry-run
py -3 examples\simple\ray_triangle_any_hit_weighted_sum_torch_device_arrays.py --dry-run
py -3 examples\simple\aabb_index_all_ops_count.py --dry-run
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/simple/v4_frontdoor_quickstart.py
PYTHONPATH=src:. python examples/simple/benchmark_app_recipes.py
PYTHONPATH=src:. python examples/simple/operator_callback_planning.py --case complex-callback
PYTHONPATH=src:. python examples/simple/fixed_radius_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/simple/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/simple/aabb_index_all_ops_count.py --dry-run
```

Use `benchmark_app_recipes.py` to learn how the 10 benchmark apps are assembled
from V4 operators.
