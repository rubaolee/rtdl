# V4 Goal4690 Tier-3 Callback Overhead Protocol

Status: protocol frozen, no timing claim and no Tier-3 support authorization

- validation: `passed`
- callback shape: `double_return_four_args_scalar_reduce`
- primary ratio: `direct_callable_loop_median_ms / direct_device_function_loop_median_ms`
- inner iterations: `1000000`
- warmup launches: `5`
- measured launches: `30`
- pass ratio max: `1.5`
- hard kill ratio min: `2.0`

## Baselines

- `direct_device_function_loop_same_numba_callback`: primary denominator.
- `inline_formula_loop_context_only`: context-only lower bound, not the release denominator.

## Measured Variant

- `optix_direct_callable_loop_same_numba_callback`: primary measured path.

## Boundary

This protocol does not authorize performance claims. Goal4691 must run the POD measurement and keep release/support flags false.
