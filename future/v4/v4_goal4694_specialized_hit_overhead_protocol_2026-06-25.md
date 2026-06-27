# V4 Goal4694: Specialized Hit Callback Overhead Protocol

Date: 2026-06-25
Status: `goal4694_specialized_hit_callback_overhead_protocol_frozen_not_measured`

## Result

Goal4694 freezes the overhead protocol for the specialized hit-program callback
track proven by Goal4693.

Evidence:

- `future/v4/evidence/v4_goal4694_specialized_hit_overhead_protocol_2026-06-25.json`
- `future/v4/evidence/v4_goal4694_specialized_hit_overhead_protocol_2026-06-25.md`

## Frozen Protocol

- primary ratio:
  `hit_direct_device_callback_trace_loop_median_ms / hit_inline_formula_trace_loop_median_ms`
- trace iterations per launch: `100,000`
- warmup launches: `3`
- measured launches: `20`
- pass threshold: `<= 1.50x`
- hard kill threshold: `> 2.00x`
- correctness required: `true`

Baseline:

- `hit_inline_formula_trace_loop_context`

Measured path:

- `hit_direct_device_callback_trace_loop`

## Boundary

Goal4694 does not measure performance and does not authorize Tier-3 support. It
freezes the next POD measurement so Goal4695 cannot move the denominator after
seeing timing results.

## Goal-Level Decision Audit

1. Was I being stupid?
   No. Goal4693 was correctness-only, so a timing protocol is required before
   any support or performance language.

2. If yes, what action made it stupid?
   The bad action would be to claim the specialized hit callback is acceptable
   without comparing it to an inline hit-program denominator.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes. Measure in the same `optixTrace -> closesthit` shape rather than using
   raygen-only microbenchmarks.

4. Can I now try the different path that actually solves the problem?
   Yes. Goal4695 should run this frozen hit-overhead protocol on the POD.
