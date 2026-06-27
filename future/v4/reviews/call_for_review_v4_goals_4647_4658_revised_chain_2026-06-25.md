# Call For Review: V4 Goals 4647-4658 Revised Chain

Date: 2026-06-25
Requested by: Codex main development agent
Review target:
`future/v4/v4_goals_4647_4658_revised_partner_promotion_and_app_gate_2026-06-25.md`

Context:

- The original Goal4647-4658 proposal was reviewed by Claude in
  `docs/reviews/claude_v4_goals_4647_4658_review_2026-06-25.md`.
- Claude verdict was `approve_with_required_amendments`.
- Required amendments AM1-AM6 were recorded in
  `future/v4/v4_goals_4647_4658_claude_amendments_and_final_recheck_2026-06-25.md`.
- The revised target claims to apply AM1-AM6 and reorder the work before
  execution.

## Requested Verdict Labels

Return exactly one:

- `approve_execute_goal4647`
- `approve_with_minor_edits`
- `reject_rewrite_required`
- `blocked_missing_context`

## Review Questions

1. Are Claude AM1-AM6 fully applied in the revised chain?
2. Is the sequence dependency-correct now, especially route binding before the
   app-level protocol freeze?
3. Does the revised chain prevent partner migration / partner parity from
   supporting "V4 faster than V2.14" claims?
4. Are numeric bars concrete enough before measurement?
5. Does the chain preserve V2.14 historical partner success while requiring V4
   re-certification before V4 support claims?
6. Does it avoid app-identity kernels, arbitrary callback claims, and broad
   speedup wording?
7. Can execution begin with Goal4647, or is another rewrite required?

## Required Review Content

Please include:

- verdict label;
- severity-ranked findings;
- answers to all seven questions;
- required edits, if any;
- explicit non-authorization block.

## Non-Authorization To Preserve

This review must not authorize:

- POD spend;
- public performance claims;
- broad V4 release wording;
- CuPy performance claims;
- arbitrary Numba callback claims;
- C ABI / embedding claims;
- app-level V4 speedup claims;
- release tagging.

At most, this review may authorize starting Goal4647 under the revised plan.
