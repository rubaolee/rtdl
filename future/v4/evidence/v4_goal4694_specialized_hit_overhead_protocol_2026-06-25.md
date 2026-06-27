# V4 Goal4694 Specialized Hit Callback Overhead Protocol

Status: protocol frozen, no timing claim and no Tier-3 support authorization

- validation: `passed`
- primary ratio: `hit_direct_device_callback_trace_loop_median_ms / hit_inline_formula_trace_loop_median_ms`
- trace iterations: `100000`
- warmup launches: `3`
- measured launches: `20`
- pass ratio max: `1.5`
- hard kill ratio min: `2.0`
- baseline: `hit_inline_formula_trace_loop_context`
- measured: `hit_direct_device_callback_trace_loop`

## Boundary

This protocol measures the specialized hit-program callback shape selected after Goal4693. It does not authorize performance claims or public Tier-3 support.
