# V4 Operator And Callback Planning

Status: current V4 planning guidance; final release authorization pending

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
- scalar min/max or reduce operators after measurement and review

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
item until the falsifiable `goal4622` protocol passes. The protocol is
`future/v4/tier3_callback_spike_protocol_2026-06-24.md`. Its current status is
`tier3_protocol_goal4622_spike_only_not_support`.

The 2026-06-24 evidence is deliberately narrow: Numba PTX generation passed,
but direct `optixModuleCreate` on the bare helper PTX failed because there were
no OptiX semantic entry functions. A future Tier-3 path therefore needs
wrapper/direct-callable ABI evidence before any support claim.

The spike gates are fixed before implementation:

- compile reliability `>= 95%` across at least 20 attempts and 4 accepted scalar
  callback variants
- OptiX wrapper/direct-callable link/run reliability `>= 95%`
- correctness parity `100%`
- median callback route overhead `<= 1.50x` versus a matching hand-written
  Tier-2 fused route, with no tested size over `2.00x`

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

Expected protocol status:

```text
tier3_protocol_goal4622_spike_only_not_support
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

## Minimum Push-Down Recognizer

Goal4630 adds a thin declarative recognizer on top of the planner. It accepts a
single generic operator request and either routes it to a measured
Tier-2 surface or fails closed:

```python
from rtdsl.v4_operator_catalog import recognize_v4_pushdown_request

recognition = recognize_v4_pushdown_request(
    {
        "kind": "itre_relation_reduce",
        "relation": "fixed_radius",
        "reduction": "count_threshold",
    },
    partner="torch",
)
print(recognition.status)
print(recognition.plan.api_surface)
```

Expected status:

```text
pushdown_recognized_measured_tier2
```

The recognizer is deliberately small. It recognizes one operator at a time and
does not claim to be a full ITRE compiler. It fails closed for:

- unmeasured partners such as CuPy performance routes in V4.0;
- unmeasured operators when someone tries to count them as measured release
  surfaces;
- application-identity kernels such as Barnes-Hut or DBSCAN;
- action-shaped callbacks;
- Tier-3 scalar callback spikes;
- unsupported custom logic.

## Runnable Example

```bash
python examples/v4/operator_callback_planning.py --case tier2
python examples/v4/operator_callback_planning.py --case scalar-callback
python examples/v4/operator_callback_planning.py --case complex-callback
```

These commands do not need CUDA. They are boundary checks, not performance
measurements.

## Non-Claims

This page does not authorize:

- final V4 release before Goal4642
- broad V4 speedup wording
- Tier-3 callback/PTX support claims
- raw OptiX callback support
- app-specific native engine kernels
