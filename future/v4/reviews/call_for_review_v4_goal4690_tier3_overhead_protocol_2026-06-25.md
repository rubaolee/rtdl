# Call For Review: V4 Goal4690 Tier-3 Callback Overhead Protocol

Date: 2026-06-25
Requested verdict labels:

- `accept_goal4690_complete_continue_goal4691`
- `reject_goal4690_protocol_insufficient`
- `accept_with_required_amendments`

## Files To Review

- Completion report:
  `future/v4/v4_goal4690_tier3_overhead_protocol_2026-06-25.md`
- Machine evidence:
  `future/v4/evidence/v4_goal4690_tier3_overhead_protocol_2026-06-25.json`
- Protocol implementation:
  `src/rtdsl/v4_goal4690_tier3_overhead_protocol.py`
- Protocol script:
  `scripts/v4_goal4690_tier3_overhead_protocol.py`
- Tests:
  `tests/v4_goal4690_tier3_overhead_protocol_test.py`

## Review Questions

1. Is `direct_device_function_loop_same_numba_callback` the right primary
   denominator for isolating OptiX direct-callable overhead?
2. Are `1,000,000` inner iterations, `5` warmups, and `30` measured launches
   sufficient for a first focused overhead gate?
3. Are the thresholds `<=1.50x pass` and `>2.00x hard kill` consistent with the
   earlier Goal4685 ABI protocol?
4. Is `inline_formula_loop_context_only` correctly marked as context, not the
   release denominator?
5. Should Goal4691 proceed to POD measurement under this frozen protocol?

## Non-Authorization

This review request does not authorize:

- public Tier-3 callback support
- performance claims before Goal4691
- V4 release or tag
- app-level benchmark claims
- arbitrary callback support
