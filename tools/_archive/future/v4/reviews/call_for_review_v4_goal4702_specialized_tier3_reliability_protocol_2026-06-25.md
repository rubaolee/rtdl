# Call For Review: V4 Goal4702 Specialized Tier-3 Reliability Matrix Protocol

Date: 2026-06-25

Requested verdict labels:

- `accept_goal4702_protocol_continue_goal4703`
- `accept_with_required_amendments_before_goal4703`
- `reject_goal4702_protocol_do_not_run_goal4703`

## Context

Goal4701 packaged the constrained specialized Tier-3 candidate:
module-specialized Numba C-ABI scalar device callback called as a direct device
function from an RTDL-generated OptiX hit-program route. Public support remains
false.

Goal4702 freezes the reliability matrix that must be run before any public
support decision can be considered.

## Review Inputs

- Completion record:
  `future/v4/v4_goal4702_specialized_tier3_reliability_protocol_2026-06-25.md`
- Evidence JSON:
  `future/v4/evidence/v4_goal4702_specialized_tier3_reliability_protocol_2026-06-25.json`
- Evidence markdown:
  `future/v4/evidence/v4_goal4702_specialized_tier3_reliability_protocol_2026-06-25.md`
- Source:
  `src/rtdsl/v4_goal4702_specialized_tier3_reliability_protocol.py`
- Tests:
  `tests/v4_goal4702_specialized_tier3_reliability_protocol_test.py`

## Questions For Reviewer

1. Does the protocol cover enough callback diversity for a support-candidate reliability gate?
2. Are 20 attempts / 4 variants / 5 attempts per variant sufficient for the next engineering gate?
3. Are dense, sparse, and no-hit datasets the right minimum correctness set?
4. Is the `>=0.95` compile/link/launch success floor appropriate for a pre-public-support reliability gate?
5. Are the cache and stage-specific failure-classification requirements strong enough?
6. Does the record preserve the correct non-authorization boundaries?
7. Is Goal4703 authorized as the next bounded engineering step, or should the matrix be amended first?

## Non-Authorization

This review must not authorize release, public Tier-3 support, arbitrary
callbacks, raw OptiX callback support, broad V4 speed claims, whole-app speed
claims, or public performance wording. It can authorize only whether Goal4703
may run under the frozen protocol.

