# Partner Choice And Device Arrays

RTDL V4 separates the program meaning from the execution policy.

The meaning is the relation or continuation you want:

```text
fixed-radius rows
grouped sum rows
component labels
AABB predicate rows
```

The partner is how that shape is executed:

```text
Torch, CuPy, Numba, or RTDL native
```

Run:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/partner_choices.py --mode both
```

## What To Look For

The same operator intent can have different partner outcomes. A route can be
ready for one partner and deferred for another. That does not change the app
meaning. It tells you whether to choose the measured partner, keep the
continuation in your app, or decompose the program into a supported row shape.

Use this decision table after you know the relation shape:

| Need | Typical choice | Why |
| --- | --- | --- |
| Caller already owns Torch CUDA tensors | Torch | Keeps data in the user's existing tensor workflow. |
| Continuation is a grouped vector or scalar reduction | CuPy | Good fit for explicit columnar reductions when that route is measured. |
| Continuation is control-heavy but expressible as a compiled device function | Numba | Good for constrained compiled continuations, not arbitrary Python actions. |
| The RTDL prepared runner owns the indexed traversal | RTDL native | Useful for prepared AABB or aggregate-frontier routes. |

Rejected example:

```text
meaning: arbitrary callback mutates shared Python object during hit handling
partner request: numba
planner answer: not a V4.0 public surface
rewrite: emit hit rows, then do app-owned mutation after the relation step
```

Partner choice should never change the meaning of the app. It only selects a
measured execution path for a relation or continuation you already described.

## Device-Array Bridge

After you understand the relation, the device-array examples show how the same
shape is supplied as Torch columns:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/fixed_radius_torch_device_arrays.py --dry-run
PYTHONPATH=src:. python examples/tutorial_programs/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py --dry-run
```

Those scripts are advanced bridge examples. Read the concept program first,
then inspect the device-array contract.

Next: [Measurement Phases](22_measurement_phases.md)
