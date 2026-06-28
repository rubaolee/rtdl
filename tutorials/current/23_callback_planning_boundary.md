# Callback Planning Boundary

RTDL V4 recognizes operator shapes. It does not accept arbitrary action-shaped
callbacks as if they were ordinary public V4 code.

Run the three planning cases:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/operator_callback_planning.py --case tier2
PYTHONPATH=src:. python examples/tutorial_programs/operator_callback_planning.py --case scalar-callback
PYTHONPATH=src:. python examples/tutorial_programs/operator_callback_planning.py --case complex-callback
PYTHONPATH=src:. python examples/tutorial_programs/custom_predicate_early_exit_planning.py
```

## Boundary

Use this rule:

| Program shape | V4.0 treatment |
| --- | --- |
| Recognized relation or continuation | Plan it with an explicit partner. |
| Constrained pure boolean predicate | Allowed only in the narrow documented predicate path. |
| Arbitrary action with mutation, dynamic allocation, or variable output | Decompose it into row production plus app-owned continuation. |

This is not a weakness of the language model. It keeps the public V4 surface
clear: relation rows first, continuation second, side effects outside the
generic operator.

Rewrite example:

```text
bad shape:
  on every ray hit, append a variable-length Python object to a shared list

RTDL shape:
  1. emit hit rows: ray_id, primitive_id, payload_id, score
  2. use a bounded or grouped continuation if the output shape is regular
  3. let ordinary app code update the shared Python object after RTDL returns
```

The key question is not "can OptiX do this in C++?" The V4.0 public question is
"can this be expressed as a recognized relation or continuation with a stable
contract?" If not, keep it outside the generic operator.

Next: [Benchmark App Bridge](24_benchmark_app_bridge.md)
