# V4 Goal4691: Tier-3 Callback Overhead Measurement

Date: 2026-06-25
Status: `tier3_overhead_measured_not_support`
Classification: `yellow_overhead_between_pass_and_kill`

## Result

Goal4691 ran the frozen Goal4690 overhead protocol on the current POD
`root@194.68.245.170:22089`.

All correctness checks passed, but the overhead gate did not pass:

- primary ratio:
  `direct_callable_loop_median_ms / direct_device_function_loop_median_ms`
- measured ratio: `1.6705538933080346x`
- pass threshold: `<= 1.50x`
- hard kill threshold: `> 2.00x`
- classification: `yellow_overhead_between_pass_and_kill`

Evidence:

- `future/v4/evidence/v4_goal4691_tier3_overhead_measurement_2026-06-25.json`
- `future/v4/evidence/v4_goal4691_tier3_overhead_measurement_2026-06-25.md`

## Measured Rows

Each row used `1,000,000` inner iterations, `5` warmups, and `30` measured
launches.

- `inline_formula_loop_context_only`
  - median: `25.3571 ms`
  - correctness: passed
  - role: context-only lower bound

- `direct_device_function_loop_same_numba_callback`
  - median: `137.03 ms`
  - correctness: passed
  - role: primary denominator

- `optix_direct_callable_loop_same_numba_callback`
  - median: `228.916 ms`
  - correctness: passed
  - role: measured path

## Interpretation

This is real Tier-3 progress, but not enough for public support:

- Goal4689 proved a scalar Numba callback can launch through an OptiX direct
  callable and produce the correct output.
- Goal4691 proves the same shape is currently about `1.67x` slower than calling
  the same Numba callback as a direct device function.
- That is below the hard-kill threshold, so the route is not dead.
- It is above the pass threshold, so it cannot be promoted as supported or
  performance-acceptable yet.

## Boundary

Not authorized:

- public Tier-3 callback support
- arbitrary user callback support
- callback overhead/performance claims
- app-level speedup claims
- V4 release or tag claims

Goal4692 must decide whether to optimize the callable ABI path, keep Tier-3 as
experimental, or redesign the callback surface.

## Goal-Level Decision Audit

1. Was I being stupid?
   No. The result was read against the frozen protocol, not reinterpreted after
   the fact.

2. If yes, what action made it stupid?
   The bad action would be to call `1.67x` "close enough" and promote Tier-3.
   The report does not do that.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes. Treat this as a yellow engineering signal: correctness and launch path
   are real, but overhead must be optimized or scoped before support.

4. Can I now try the different path that actually solves the problem?
   Yes. Goal4692 should make the support decision and, if continuing, select a
   concrete overhead-reduction experiment rather than re-running the same probe.
