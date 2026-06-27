# V4 Goal4695: Specialized Hit Callback Overhead Measurement

Date: 2026-06-25
Status: `specialized_hit_overhead_measured_not_support`
Classification: `pass_hit_overhead_gate_not_support`

## Result

Goal4695 ran the frozen Goal4694 hit-program trace-loop overhead protocol on
the current POD `root@194.68.245.170:22089`.

The specialized direct-device callback path passed the focused overhead gate:

- primary ratio:
  `hit_direct_device_callback_trace_loop_median_ms / hit_inline_formula_trace_loop_median_ms`
- measured ratio: `1.0355240926982583x`
- pass threshold: `<= 1.50x`
- hard kill threshold: `> 2.00x`
- classification: `pass_hit_overhead_gate_not_support`

Evidence:

- `future/v4/evidence/v4_goal4695_specialized_hit_overhead_measurement_2026-06-25.json`
- `future/v4/evidence/v4_goal4695_specialized_hit_overhead_measurement_2026-06-25.md`

## Measured Rows

Each row used `100,000` trace iterations per launch, `3` warmups, and `20`
measured launches.

- `hit_inline_formula_trace_loop_context`
  - median: `218.1055 ms`
  - correctness: passed

- `hit_direct_device_callback_trace_loop`
  - median: `225.8535 ms`
  - correctness: passed

## Interpretation

This is the strongest Tier-3 evidence in the current V4 chain:

- SBT direct callable remained yellow in Goal4691 at `1.67x`.
- The module-specialized direct device callback path passed in Goal4695 at
  `1.036x` in a real `optixTrace -> closesthit` loop.
- The pivot selected by Goal4692 is therefore justified.

This still does not authorize public Tier-3 support by itself. It is a focused
probe, not an app-level benchmark, not arbitrary callback coverage, and not
external-review authorization.

## Boundary

Not authorized:

- arbitrary callback support
- action-shaped callback support
- app-level speedup claims
- V4 release or tag claims

Goal4696 should decide whether to productize a constrained Tier-3 specialized
callback surface and define the app-route validation needed before public
support.

## Goal-Level Decision Audit

1. Was I being stupid?
   No. The measurement used the frozen Goal4694 denominator and did not compare
   against an easier after-the-fact baseline.

2. If yes, what action made it stupid?
   The bad action would be to claim broad callback support from one scalar
   callback shape. This report keeps the support boundary closed.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes. Use specialized direct-device callback composition for hot hit-program
   callbacks, while keeping SBT direct-callable dynamic callbacks experimental.

4. Can I now try the different path that actually solves the problem?
   Yes. Goal4696 should turn this into a constrained productization decision
   and define the app-level validation gate.
