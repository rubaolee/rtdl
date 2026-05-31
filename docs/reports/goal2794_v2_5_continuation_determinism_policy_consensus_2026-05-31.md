# Goal2794 Consensus - v2.5 Continuation Determinism Policy

Date: 2026-05-31

## Inputs

- Codex implementation/report:
  `docs/reports/goal2794_v2_5_continuation_determinism_policy_2026-05-31.md`
- Independent Gemini review:
  `docs/reviews/goal2794_gemini_review_continuation_determinism_policy_2026-05-31.md`

## Verdicts

| Reviewer | Verdict | Notes |
| --- | --- | --- |
| Codex | `accept-with-boundary` | The policy makes v2.5 continuation determinism testable, but does not authorize performance or release claims. |
| Gemini | `accept` | The policy covers all 12 v2.5 partner-continuation operations exactly once and makes tie-break, tolerance, and fail-closed behavior concrete. |

## Consensus

`accept-with-boundary`

Goal2794 is accepted as a deterministic comparison-contract layer for v2.5
partner continuations. It closes the planning gap where witness/tie-break risks
were previously documented but not connected to an acceptance test.

## Claim Boundary

Still blocked:

- public speedup claims;
- whole-app speedup claims;
- release readiness;
- replacing RT traversal with partner continuation code;
- hidden partner selection or automatic execution strategy selection.

Goal2794 is a policy and test gate only. It does not change runtime selection,
does not add app-specific semantics, and does not promote v2.5 to public
release status.
