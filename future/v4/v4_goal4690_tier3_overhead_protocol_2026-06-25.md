# V4 Goal4690: Tier-3 Callback Overhead Protocol

Date: 2026-06-25
Status: `goal4690_tier3_callback_overhead_protocol_frozen_not_measured`

## Result

Goal4690 freezes the overhead measurement protocol before any timing result is
used.

Evidence:

- `future/v4/evidence/v4_goal4690_tier3_overhead_protocol_2026-06-25.json`
- `future/v4/evidence/v4_goal4690_tier3_overhead_protocol_2026-06-25.md`

## Frozen Protocol

- callback shape: `double_return_four_args_scalar_reduce`
- primary ratio:
  `direct_callable_loop_median_ms / direct_device_function_loop_median_ms`
- inner iterations per launch: `1,000,000`
- warmup launches: `5`
- measured launches: `30`
- pass threshold: `<= 1.50x`
- hard kill threshold: `> 2.00x`
- correctness required: `true`

Primary denominator:

- `direct_device_function_loop_same_numba_callback`

Context-only lower bound:

- `inline_formula_loop_context_only`

Measured path:

- `optix_direct_callable_loop_same_numba_callback`

## Boundary

Goal4690 does not measure performance and does not authorize Tier-3 support.
It only prevents Goal4691 from moving the timing denominator after results are
known.

## Goal-Level Decision Audit

1. Was I being stupid?
   No. Measuring overhead without freezing the denominator would repeat the
   earlier "run first, explain later" failure mode.

2. If yes, what action made it stupid?
   The bad action would be timing only the direct-callable path and inventing a
   denominator afterward. This protocol blocks that.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes. Use the same Numba callback in both the direct-callable path and the
   direct device-function denominator, with inline formula only as context.

4. Can I now try the different path that actually solves the problem?
   Yes. Goal4691 should run the frozen POD measurement and classify the result
   by the predeclared `1.50x` / `2.00x` thresholds.
