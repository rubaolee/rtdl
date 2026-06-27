# Call For Review: V4 Goal4712 Next Lever After Custom-Scored Failure

Date: 2026-06-26

Requested verdict labels:

- `accept_goal4712_selection_continue_goal4713_protocol`
- `accept_with_required_amendments`
- `reject_selection_reconsider_next_lever`

## Files To Review

- Completion report:
  `future/v4/v4_goal4712_next_lever_after_custom_scored_failure_2026-06-26.md`
- Evidence JSON:
  `future/v4/evidence/v4_goal4712_next_lever_after_custom_scored_failure_2026-06-26.json`
- Evidence Markdown:
  `future/v4/evidence/v4_goal4712_next_lever_after_custom_scored_failure_2026-06-26.md`
- Source:
  `src/rtdsl/v4_goal4712_next_lever_after_custom_scored_failure.py`
- Script:
  `scripts/v4_goal4712_next_lever_after_custom_scored_failure.py`
- Tests:
  `tests/v4_goal4712_next_lever_after_custom_scored_failure_test.py`
- Goal4711 result:
  `future/v4/v4_goal4711_custom_scored_app_focused_pod_2026-06-26.md`

## Review Questions

1. Does Goal4711's `1.029x` result justify rejecting post-hit scalar
   accumulation polish as the next high-performance V4 route?
2. Is `custom_predicate_early_exit_multi_hit` a valid next V4 target because it
   changes traversal/candidate/materialization cost?
3. Does the selected target preserve the app-agnostic boundary?
4. Is the callback/action split correct?
   - user callback: pure scalar/boolean;
   - RTDL action: terminate/filter/count policy.
5. Should Goal4713 freeze a protocol before POD instead of jumping straight to
   timing?
6. Are any release or public Tier-3 claims accidentally authorized?

## Non-Authorization

This review request does not authorize:

- POD timing;
- all-app benchmarking;
- V4 release;
- formal high-performance wording;
- public Tier-3 support;
- arbitrary callback support;
- raw OptiX callback support.

