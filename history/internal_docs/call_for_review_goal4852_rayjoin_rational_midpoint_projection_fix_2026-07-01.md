# Call For Review: Goal4852 RayJoin Rational Midpoint Projection Fix

Date: 2026-07-01

## Requested Verdict

Please return one of:

- `approve_goal4852_rational_midpoint_projection_fix`
- `approve_with_required_amendments`
- `block_goal4852_rational_midpoint_projection_fix`

## Context

Claude's Goal4851 review noted that `tests.goal4374_rayjoin_exact_paper_suite_test`
still had a small `8e-14` failure in output-chain midpoint projection. This
follow-up fixes that exact regression.

Primary report:

- `history/internal_docs/goal4852_rayjoin_rational_midpoint_projection_fix_2026-07-01.md`

Primary code:

- `src/rtdsl/rayjoin_overlay.py`

Primary test:

- `tests/goal4374_rayjoin_exact_paper_suite_test.py`

## Review Questions

1. Is the root cause correctly identified as truncating each rational
   intersection coordinate before midpoint projection?
2. Is averaging `Fraction` coordinates first and then truncating once the right
   author-scaled midpoint behavior for this output-chain step?
3. Is the change narrow, limited to `_midpoints_for_sorted_xsects()`, and not a
   hidden change to LSI/PIP or public planar-map LSI semantics?
4. Does the local evidence show the previously failing `goal4374` exact-paper
   suite now passes?
5. Does the Goal4851 focused test still pass after this change?
6. Are the claim boundaries correct: no full Section 5.7 claim, no broad
   RayJoin performance claim, and no public speedup wording?

## Non-Authorization

This review must not authorize:

- full RayJoin paper reproduction,
- public performance claims,
- any V3/V4 release claim,
- or unrelated runtime/native changes.
