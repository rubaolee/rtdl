# Call For Review: V4 Goal4692 Tier-3 Support Decision

Date: 2026-06-25
Requested verdict labels:

- `accept_goal4692_pivot_continue_goal4693`
- `reject_goal4692_decision_invalid`
- `hard_kill_tier3`
- `accept_with_required_amendments`

## Files To Review

- Completion report:
  `future/v4/v4_goal4692_tier3_support_decision_2026-06-25.md`
- Machine decision evidence:
  `future/v4/evidence/v4_goal4692_tier3_support_decision_2026-06-25.json`
- Goal4691 measurement:
  `future/v4/v4_goal4691_tier3_overhead_measurement_2026-06-25.md`
- Decision module:
  `src/rtdsl/v4_goal4692_tier3_support_decision.py`

## Review Questions

1. Is it correct to reject public SBT direct-callable support after the `1.67x`
   overhead result?
2. Is it correct not to hard-kill Tier-3, given that the direct device-function
   Numba callback denominator was correct and faster?
3. Is `module_specialized_direct_device_callback_in_hit_program` the right next
   track?
4. Does Goal4692 preserve non-authorization boundaries?
5. Should Goal4693 proceed as a minimal OptiX hit-program probe?

## Non-Authorization

This review request does not authorize:

- final V4 release
- public Tier-3 callback support
- arbitrary callback support
- direct-callable performance claims
- app-level benchmark claims
