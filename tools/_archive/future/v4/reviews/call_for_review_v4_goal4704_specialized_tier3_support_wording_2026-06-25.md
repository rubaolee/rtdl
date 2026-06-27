# Call For Review: V4 Goal4704 Specialized Tier-3 Support Wording Gate

Date: 2026-06-25

Requested verdict labels:

- `accept_goal4704_wording_gate_continue_goal4705`
- `accept_with_required_amendments_before_goal4705`
- `reject_goal4704_wording_gate_overclaims_support`

## Context

Goal4703 passed the specialized Tier-3 reliability matrix, but it did not
authorize public support or performance claims. Goal4704 adds a wording gate so
that the support candidate cannot be overstated.

## Review Inputs

- Completion record:
  `future/v4/v4_goal4704_specialized_tier3_support_wording_2026-06-25.md`
- Evidence JSON:
  `future/v4/evidence/v4_goal4704_specialized_tier3_support_wording_2026-06-25.json`
- Evidence markdown:
  `future/v4/evidence/v4_goal4704_specialized_tier3_support_wording_2026-06-25.md`
- Source:
  `src/rtdsl/v4_goal4704_specialized_tier3_support_wording.py`
- Tests:
  `tests/v4_goal4704_specialized_tier3_support_wording_test.py`

## Questions For Reviewer

1. Does Goal4704 preserve the correct boundary between support candidate and public support?
2. Are the prohibited public wordings strong enough?
3. Is it acceptable to expose the candidate in `claim_boundary_v4()` while keeping public support false?
4. Are the remaining public-support gates complete?
5. Is Goal4705, source-level PTX canonicalization/repeated compile cache stability, the right next engineering goal?

## Non-Authorization

This review must not authorize public Tier-3 support, arbitrary callbacks, raw
OptiX callbacks, release wording, broad speed claims, whole-app speed claims, or
final V4 release. It can authorize only whether Goal4704's wording gate is
acceptable and whether Goal4705 may proceed.

