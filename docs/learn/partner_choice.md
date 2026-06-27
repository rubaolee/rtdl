# V4 Partner Choice

V4 makes partner choice explicit. The user picks a partner, and the planner
returns the current supported surface or a closed response.

```python
import rtdsl.v4 as rt

for request, partner in [
    ("fixed_radius", "torch"),
    ("grouped_sum", "cupy"),
    ("component_union", "numba"),
    ("aabb_index_query", "rtdl_native"),
]:
    plan = rt.plan_operator_request_v4(request, partner=partner)
    print(request, partner, plan.status, plan.api_surface)
```

## Partner Guide

| Partner | Use when | Example request |
| --- | --- | --- |
| Torch CUDA | You already keep tensor columns in Torch and need a measured V4 device-array surface. | `fixed_radius`, `any_hit`, `point_group_nearest` |
| CuPy | You need a grouped continuation on device columns and choose CuPy explicitly. | `grouped_sum` |
| Numba | You need a measured Numba continuation or a constrained pure predicate workflow. | `component_union`, `custom_predicate_early_exit` |
| RTDL native | RTDL owns the prepared index/frontier route. | `aabb_index_query`, `aggregate_frontier` |

## Closed Requests

Unsupported callback shapes fail closed. For example, arbitrary Python actions,
shared-state mutation, dynamic allocation, variable-length output, raw OptiX
callbacks, and Tier-3 PTX/module linking are not V4.0 public features.

```python
import rtdsl.v4 as rt

plan = rt.plan_operator_request_v4(
    "custom_predicate_early_exit",
    partner="numba",
    callback_shape="custom_action",
    mutates_shared_state=True,
)

print(plan.status)
```

## Rule Of Thumb

Start with the data you already own:

- Torch tensors: ask for a Torch surface first.
- CuPy arrays: ask only for surfaces that explicitly name CuPy.
- Numba device logic: keep it within the supported continuation or predicate
  shapes.
- Spatial indexes/frontiers: let RTDL native prepared runners own the route.

If the planner does not return a supported surface, keep the logic outside the
operator or use an inherited benchmark route that already implements the task.

