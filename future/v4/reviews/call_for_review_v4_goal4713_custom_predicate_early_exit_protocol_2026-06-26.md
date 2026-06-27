# Call For Review: V4 Goal4713 Custom Predicate Early-Exit Protocol

Date: 2026-06-26

Requested verdict labels:

- `accept_goal4713_protocol_continue_goal4714_runner_smoke`
- `accept_with_required_amendments`
- `reject_protocol_rewrite_required`

## Files To Review

- Completion report:
  `future/v4/v4_goal4713_custom_predicate_early_exit_protocol_2026-06-26.md`
- Evidence JSON:
  `future/v4/evidence/v4_goal4713_custom_predicate_early_exit_protocol_2026-06-26.json`
- Evidence Markdown:
  `future/v4/evidence/v4_goal4713_custom_predicate_early_exit_protocol_2026-06-26.md`
- Source:
  `src/rtdsl/v4_goal4713_custom_predicate_early_exit_protocol.py`
- Script:
  `scripts/v4_goal4713_custom_predicate_early_exit_protocol.py`
- Tests:
  `tests/v4_goal4713_custom_predicate_early_exit_protocol_test.py`
- Goal4711 failure:
  `future/v4/v4_goal4711_custom_scored_app_focused_pod_2026-06-26.md`
- Goal4712 next-lever selection:
  `future/v4/v4_goal4712_next_lever_after_custom_scored_failure_2026-06-26.md`

## Review Questions

1. Does this protocol correctly target a changed cost model after Goal4711?
2. Are the primary regimes serious enough, especially `dense_early_accept_k32`?
3. Are late-accept/reject/no-hit rows correctly classified as controls only?
4. Are the V2/V3 denominator requirements fair and strong enough?
5. Are the bars too weak, too strong, or appropriate for formal high-performance
   V4 candidacy?
6. Is the callback/action split safe and app-agnostic?
7. Does Goal4713 correctly avoid authorizing POD until Goal4714?

## Non-Authorization

This review request does not authorize:

- POD timing;
- all-app benchmarking;
- V4 release;
- formal high-performance wording;
- public Tier-3 support;
- arbitrary callback support;
- raw OptiX callback support.

