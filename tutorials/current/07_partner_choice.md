# Partner Choice

V4 does not hide partner choice. The app author chooses the partner, and RTDL
returns the matching operator plan when the route is part of the current public
surface.

```python
import rtdsl.v4 as rt

torch_plan = rt.plan_operator_request_v4("fixed_radius", partner="torch")
cupy_plan = rt.plan_operator_request_v4("grouped_sum", partner="cupy")
numba_plan = rt.plan_operator_request_v4("component_union", partner="numba")
native_plan = rt.plan_operator_request_v4("aabb_index_query", partner="rtdl_native")

print(torch_plan.status, torch_plan.api_surface)
print(cupy_plan.status, cupy_plan.api_surface)
print(numba_plan.status, numba_plan.api_surface)
print(native_plan.status, native_plan.api_surface)
```

Use Torch when your app already keeps device columns as Torch tensors and the
operator catalog names a Torch surface.

Use CuPy when you explicitly want a CuPy continuation over device columns.

Use Numba when the current surface names a Numba continuation or a constrained
pure predicate workflow.

Use RTDL native when the route is an RTDL-owned prepared index or frontier.

Requests outside the current surface return a bounded planner result:

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

That bounded result is part of the contract: V4.0 supports constrained
predicate early-exit and keeps arbitrary RT-traversal actions outside the
current public surface.
