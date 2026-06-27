# Handoff: Goal3930 Gemini Review Of Goal3928-3929 Numba Discovery And Parity

Please perform a read-only review of Goals3928 and 3929.

## Context

Goal3926's Gemini review accepted the Numba coverage audit and suggested:

- making Numba references easier to discover;
- adding more systematic parity-by-default expectations.

Goal3928 added `rtdsl.v2_6_numba_reference_index()`.
Goal3929 added `rtdsl.v2_6_numba_parity_expectations()`.

Both helpers are advisory only and built from the existing v2.6 partner-choice
guidance surface. They must not become hidden partner selection, release
authorization, or speedup wording.

## Files To Inspect

- `src/rtdsl/v2_6_partner_choice_guidance.py`
- `src/rtdsl/__init__.py`
- `docs/learn/benchmark_partner_reference_matrix.md`
- `docs/reports/goal3928_numba_reference_discovery_index_2026-06-08.md`
- `tests/goal3928_numba_reference_discovery_index_test.py`
- `docs/reports/goal3929_numba_reference_parity_expectations_2026-06-08.md`
- `tests/goal3929_numba_reference_parity_expectations_test.py`

## Questions

1. Do the new helpers avoid creating a second source of truth?
2. Does `v2_6_numba_reference_index()` clearly answer the discoverability
   question without auto-selecting a partner?
3. Does `v2_6_numba_parity_expectations()` cover all currently available Numba
   reference rows and keep RTDBSCAN blocked-mode evidence pending?
4. Do the docs and tests avoid release/public-speedup/broad-RT-core/
   true-zero-copy/automatic-partner-selection overclaims?
5. What should be improved before the next A5000 performance packet?

## Required Output

Write your review to:

`docs/reviews/goal3930_gemini_review_goal3928_3929_numba_discovery_parity_2026-06-08.md`

Use one of the project verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

If you cannot run tests, state that limitation and ground the review in source
and artifact inspection.
