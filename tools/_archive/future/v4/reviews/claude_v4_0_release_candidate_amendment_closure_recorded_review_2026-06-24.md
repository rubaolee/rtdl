# Claude Follow-Up Review Record: V4.0 Amendment Closure

Date: 2026-06-24

Reviewer: Claude Sonnet 4.6

Raw output: `future/v4/reviews/claude_v4_0_release_candidate_amendment_closure_review_2026-06-24.raw.md`

## Verdict

`approve_amendments_closed_not_release_authorized`

Claude confirmed that all five required amendments from the V4.0 release
candidate review were substantively closed.

## Closed Amendments

1. `v4_review_debt_open` is enumerated and resolvable.
2. A clean-commit rerun protocol exists.
3. Closest-hit grouped argmin documents its public true-zero-copy boundary.
4. `partner="cupy"` planning returns no V4.0 `api_surface`.
5. The catalog regression gate checks per-example forbidden claim flags.

## Low-Severity Follow-Up

Claude noted that forbidden-claim checks were presence-conditional and lacked a
negative regression test. This was closed immediately by making
`scripts/v4_catalog_regression_gate.py` recursively reject forbidden claim flags
in nested payload/metadata objects and by adding a negative test in
`tests/v4_catalog_regression_gate_test.py`.

## Remaining Release Blockers

- release decision record not obtained
- D2 Antigravity reviewer unavailability must be explicitly waived or otherwise
  resolved in the release decision record

## Non-Authorization

This review record does not authorize V4 release, broad V4 speedup wording,
whole-application speedup wording, Tier-3 callback/PTX support claims, raw OptiX
callback support, CuPy performance claims, embedding/C-ABI claims, non-Python
host binding claims, or app-specific native engine kernels.
