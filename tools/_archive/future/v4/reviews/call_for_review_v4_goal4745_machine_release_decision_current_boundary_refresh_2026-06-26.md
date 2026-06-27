# Call For Review: V4 Goal4745 Machine Release Decision Current Boundary Refresh

Date: 2026-06-26

Reviewer requested: Claude and Antigravity when available.

Status: `external_review_requested_debt_allowed`

## Files To Review

- `future/v4/v4_goal4745_machine_release_decision_current_boundary_refresh_2026-06-26.md`
- `future/v4/evidence/v4_goal4745_machine_release_decision_current_boundary_refresh_2026-06-26.json`
- `src/rtdsl/v4_release_decision.py`
- `src/rtdsl/v4_goal4644_post_release_guardrails.py`
- `tests/v4_goal4632_release_decision_test.py`
- `tests/v4_goal4644_post_release_guardrails_test.py`
- `tests/v4_goal4745_machine_release_decision_refresh_test.py`

## Questions

1. Does the machine release decision now match the current Goal4742/Goal4744
   public/front-door boundary?
2. Is it correct to remove old Goal4655/Goal4718 labels from the current
   machine release-decision surface?
3. Do G13/G14 correctly represent the current public-doc cleanup and full V4
   local gate?
4. Are release blockers and non-authorization boundaries preserved?
5. Is the 558-test V4 discover pass sufficient local evidence for this machine
   decision refresh?

## Requested Verdict Labels

- `accept_goal4745_machine_release_decision_refresh`
- `accept_with_required_amendments`
- `reject_machine_release_decision_stale_or_overclaiming`

## Non-Authorization

This review must not authorize final V4 tag, all-benchmark speedup claims,
broad V4-over-V2.14 claims, arbitrary callbacks, raw OptiX callbacks,
true-zero-copy wording, non-Python embedding/C ABI, or app-specific native
kernels.
