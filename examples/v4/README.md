# RTDL V4 Examples

These are the current user-facing V4 example entrypoints.

PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\v4\v4_frontdoor_quickstart.py
py -3 examples\v4\operator_callback_planning.py --case complex-callback
py -3 examples\v4\fixed_radius_torch_device_arrays.py --dry-run
py -3 examples\v4\ray_triangle_any_hit_weighted_sum_torch_device_arrays.py --dry-run
py -3 examples\v4\aabb_index_all_ops_count.py --dry-run
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/v4/v4_frontdoor_quickstart.py
PYTHONPATH=src:. python examples/v4/operator_callback_planning.py --case complex-callback
PYTHONPATH=src:. python examples/v4/fixed_radius_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/v4/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/v4/aabb_index_all_ops_count.py --dry-run
```

Dry-run examples verify API reachability and claim-boundary flags without CUDA.
Measured GPU results require the recorded V4 benchmark gate.
