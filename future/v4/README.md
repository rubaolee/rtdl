# RTDL V4 Development Front Door

Status: V4 development surface, not a release announcement

V4 is the Python GPU-array RT-core lane. If your program already owns Torch CUDA
arrays, RTDL should accept those arrays, run a generic fused RT operator, and
write results back to GPU arrays without Python row objects in the hot path.

Use one import:

```python
import rtdsl.v4 as rtdl_v4
```

## Measured V4 Tier-2 Operators

The current measured Torch CUDA surfaces are:

- fixed-radius count-threshold
- closest-hit grouped argmin
- ray/triangle any-hit flags

List them programmatically:

```python
for row in rtdl_v4.measured_operator_catalog_v4():
    print(row["operator"], row["api_surface"])
```

Plan a request before building a route:

```python
plan = rtdl_v4.plan_operator_request_v4("any-hit", partner="torch")
print(plan.status)
print(plan.api_surface)
```

## Complex Callback Boundary

V4.0 does not expose raw OptiX callbacks. Complex user logic is handled by a
strict planner:

- recognized operators route to measured Tier-2 surfaces
- scalar Numba device callbacks are Tier-3 spike-only, not supported release
  surfaces
- action-shaped callbacks that mutate shared state, allocate dynamically, or
  produce variable-length output are rejected/deferred for V4.0

Run the local no-CUDA boundary examples:

```bash
python future/v4/examples/v4_frontdoor_quickstart.py
python future/v4/examples/operator_callback_planning.py --case complex-callback
python scripts/v4_catalog_regression_gate.py --mode dry-run
```

## Operator Docs

- `future/v4/fixed_radius_device_array_frontdoor.md`
- `future/v4/ray_triangle_device_array_frontdoor.md`
- `future/v4/tier2_operator_catalog.md`
- `future/v4/callback_and_operator_planning.md`
- `future/v4/v4_0_scope_gate.md`
- `future/v4/tier3_numba_ptx_spike.md`

The catalog regression gate is `scripts/v4_catalog_regression_gate.py`.

## Scope Boundary

V4.0 development scope is limited to the measured Torch CUDA Tier-2 surfaces and
the conservative planner. Tier-3 Numba/PTX callbacks, raw OptiX callbacks, CuPy
performance, embedding/C-ABI, and non-Python host bindings are V4.x or later.

## Non-Claims

This page does not authorize:

- V4 release
- broad V4 speedup wording
- whole-application speedup wording
- Tier-3 callback/PTX support claims
- raw OptiX callback support
- app-specific native engine kernels
- embedding/C-ABI claims
