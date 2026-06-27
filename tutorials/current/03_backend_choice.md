# Operator Choice

V4 keeps partner choice explicit. A partner is measured only inside its recorded
scope.

Current measured partner scopes:

- Torch CUDA for the device-array surfaces;
- Numba for fixed-radius graph component union;
- RTDL native prepared runner for AABB all-ops count.

Plan an operator request before building a route:

```python
import rtdsl.v4 as rtdl_v4

plan = rtdl_v4.plan_operator_request_v4("any-hit", partner="torch")
print(plan.status)
print(plan.api_surface)
```

Requests outside the current surface return a bounded planner result:

```powershell
py -3 examples\v4\operator_callback_planning.py --case complex-callback
```

Do not infer performance from a partner name. Use only the measured operator
surface, partner, hardware, and metric you can point to.

Next: [Measured Runtime Surfaces](04_prepared_runtime.md)
