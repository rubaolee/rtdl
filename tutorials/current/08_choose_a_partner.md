# Choose a Partner

V4 keeps partner choice explicit.

RTDL owns the RT-shaped operator. The app author chooses the array ecosystem
that should feed or consume that operator.

Use this mental model:

- **Torch**: your tensors and model pipeline already live in Torch CUDA;
- **CuPy**: you want explicit CUDA-array continuation code in Python;
- **Numba**: you need a compiled Python device function for a constrained
  predicate or continuation;
- **RTDL native**: RTDL owns the prepared index, frontier, or traversal state.

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

The runnable partner-choice program prints both accepted and deferred
combinations, so you can see the planning boundary:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\tutorial_programs\partner_choices.py
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/partner_choices.py
```

For custom logic, first ask whether the logic can be expressed as a generic
operator such as filter, count, any-hit, argmin, grouped sum, or component
union. If it can, use the operator. If it is a pure boolean predicate over one
hit candidate, use the constrained Numba predicate path:

```python
import rtdsl.v4 as rt

plan = rt.plan_operator_request_v4(
    "custom_predicate_early_exit",
    partner="numba",
    callback_shape="pure_boolean_numba_cabi_device_function",
    numba_device_function=True,
)

print(plan.status)
print(plan.api_surface)
```

If your logic needs shared mutation, dynamic allocation, or variable-length
output during traversal, split the program: use RTDL for the relation, then run
the custom work as an explicit continuation.

Next: open [Build the Benchmark Apps](07_benchmark_apps.md) again and identify
which partner each app chooses.
