# Gemini Review Request - Goal2794 v2.5 Continuation Determinism Policy

Please perform an independent read-only review of Goal2794 and write your
review to:

`docs/reviews/goal2794_gemini_review_continuation_determinism_policy_2026-05-31.md`

## Context

Goal2794 addresses a prior review concern that v2.5 witness/tie-break and
determinism risk needed a concrete acceptance hook. The implementation adds a
generic determinism policy for all v2.5 partner-continuation operations.

## Files To Inspect

- `src/rtdsl/v2_5_determinism_policy.py`
- `src/rtdsl/__init__.py`
- `tests/goal2794_v2_5_determinism_policy_test.py`
- `docs/reports/goal2794_v2_5_continuation_determinism_policy_2026-05-31.md`
- Existing context:
  - `docs/reviews/goal2773_claude_review_v2_5_status_next_goals_2026-05-31.md`
  - `src/rtdsl/partner_continuation_protocol.py`
  - `src/rtdsl/grouped_reduction_contracts.py`

## Questions

1. Does the policy cover every current v2.5 partner-continuation operation
   exactly once?
2. Are tie-breaks and tolerances concrete enough for deterministic comparison,
   especially `grouped_argmin_f64`, `grouped_argmax_f64`, `grouped_topk_f64`,
   floating sums, bounded collection, and event-ordered hit streams?
3. Does the implementation stay app-agnostic and avoid turning app semantics
   into core runtime policy?
4. Does the policy avoid overclaiming speedup, release readiness, whole-app
   acceleration, or RT traversal replacement?
5. Are the tests sufficient to prevent the same determinism/tie-break risk from
   becoming an untracked design note again?

## Required Output Shape

Please include:

- verdict: one of `accept`, `accept-with-boundary`, `needs-more-evidence`, or
  `reject`;
- findings, if any, with file/line references;
- explicit statement that this is an independent Gemini review distinct from
  Codex authoring.

Do not mutate source files other than writing the requested review document.
