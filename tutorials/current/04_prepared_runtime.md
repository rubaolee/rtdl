# Prepare, Run, Continue

In V4, planning and execution are separate steps.

Once the planner gives you a surface, a real program moves through three phases:

1. **prepare** reusable state for the operator and data layout;
2. **run** the RT-shaped relation;
3. **continue** with a compact summary or app step.

The exact prepare function depends on the operator. You can discover the
surface first, then open the matching example.

```python
import rtdsl.v4 as rt

operators = [
    "fixed_radius",
    "any_hit",
    "weighted_sum",
    "point_group_nearest",
    "aabb_index_query",
    "aggregate_frontier",
]

for name in operators:
    partner = "rtdl_native" if name in {"aabb_index_query", "aggregate_frontier"} else "torch"
    plan = rt.plan_operator_request_v4(name, partner=partner)
    print(name, "->", plan.api_surface)
```

The examples below run in dry-run mode, so they are safe on a machine without a
CUDA device:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\v4\fixed_radius_torch_device_arrays.py --dry-run
py -3 examples\v4\ray_triangle_any_hit_flags_torch_device_arrays.py --dry-run
py -3 examples\v4\point_group_nearest_witness_torch_device_arrays.py --dry-run
py -3 examples\v4\aabb_index_all_ops_count.py --dry-run
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/v4/fixed_radius_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/v4/ray_triangle_any_hit_flags_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/v4/point_group_nearest_witness_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/v4/aabb_index_all_ops_count.py --dry-run
```

In a full GPU program, replace dry-run inputs with device arrays from your
chosen partner. The important design rule stays the same: keep the relation
generic, and keep app meaning in the code that chooses and consumes the
relation.

Next: [Measure a Program](05_measurement_boundaries.md)
