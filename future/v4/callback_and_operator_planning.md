# V4 Operator And Callback Planning

Status: V4 development guidance, not a release announcement

V4 does not expose raw OptiX callbacks as the public programming model. The
public model is operator push-down: a user asks for a generic continuation such
as count-threshold, any-hit flags, or grouped argmin, and RTDL routes that
request to a measured fused Tier-2 operator when one exists.

## The Rule

RTDL V4 may contain fused native kernels for generic continuation operators.
It must not contain application-identity kernels.

Allowed examples:

- count / threshold
- any-hit flag
- grouped argmin
- scalar min/max or reduce candidates after review

Not allowed as V4.0 public surfaces:

- "Barnes-Hut kernel"
- "DBSCAN kernel"
- "RayJoin kernel"
- raw OptiX callback hooks
- action-shaped callbacks that mutate shared state, allocate dynamically, or
  produce variable-length output

## Programmatic Planning

Use the planner before building a new V4 route:

```python
from rtdsl.v4_operator_catalog import plan_v4_operator_request

plan = plan_v4_operator_request("fixed-radius", partner="torch")
print(plan.status)
print(plan.api_surface)
```

For a supported Tier-2 operator this returns a measured device-array surface:

```text
tier2_measured_ready
v4_fixed_radius_count_threshold_2d_device_arrays
```

For a scalar Numba device callback, V4 is honest: it is only a Tier-3 spike
candidate until the Numba-to-PTX-to-OptiX path links, runs, and is measured.
The 2026-06-24 evidence is deliberately narrow: Numba PTX generation passed,
but direct `optixModuleCreate` on the bare helper PTX failed because there were
no OptiX semantic entry functions. A future Tier-3 path therefore needs
wrapper/direct-callable ABI evidence before any support claim.

```python
plan = plan_v4_operator_request(
    "custom-force-score",
    callback_shape="custom_scalar_reduce",
    numba_device_function=True,
    partner="torch",
)
```

Expected status:

```text
tier3_spike_only_not_v4_0_release_surface
```

For complex action-shaped callbacks, V4.0 rejects rather than pretending that
RTDL can safely wrap arbitrary OptiX logic:

```python
plan = plan_v4_operator_request(
    "custom-collision-response",
    callback_shape="custom_action",
    mutates_shared_state=True,
    variable_length_output=True,
    dynamic_allocation=True,
    partner="torch",
)
```

Expected status:

```text
rejected_action_shaped_callback_deferred
```

## Runnable Example

```bash
python future/v4/examples/operator_callback_planning.py --case tier2
python future/v4/examples/operator_callback_planning.py --case scalar-callback
python future/v4/examples/operator_callback_planning.py --case complex-callback
```

These commands do not need CUDA. They are boundary checks, not performance
measurements.

## Non-Claims

This page does not authorize:

- V4 release
- broad V4 speedup wording
- Tier-3 callback/PTX support claims
- raw OptiX callback support
- app-specific native engine kernels
