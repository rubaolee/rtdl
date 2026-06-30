# Handoff: Goal3926 Gemini Review Of Goal3924-3925 Numba Coverage

Please perform a read-only review of Goals3924 and 3925.

## Context

The user has a hard requirement that benchmark apps needing custom partner
logic should have Numba reference implementations so users are not forced to
write CuPy RawKernel code. Goals3924-3925 do not add new runtime behavior; they
verify local development readiness and make the current Numba coverage picture
machine-checkable.

## Files To Inspect

- `docs/reports/goal3924_local_linux_rtdbscan_numba_optix_smoke_2026-06-08.md`
- `tests/goal3924_local_linux_rtdbscan_numba_optix_smoke_test.py`
- `docs/reports/goal3925_numba_custom_partner_coverage_after_local_smokes_2026-06-08.md`
- `tests/goal3925_numba_custom_partner_coverage_after_local_smokes_test.py`
- `src/rtdsl/v2_6_partner_choice_guidance.py`
- `tests/goal3921_partner_choice_guidance_after_numba_reference_refresh_test.py`
- `tests/goal3054_v2_6_partner_choice_guidance_test.py`

## Questions

1. Does Goal3924 honestly classify local Linux GTX 1070 smoke evidence as
   functional readiness only, not release performance evidence?
2. Does Goal3925 correctly distinguish primitive-first apps from apps needing
   custom Numba continuation logic?
3. Does the guidance avoid any CuPy-only recommended custom-continuation gap?
4. Are RTDBSCAN blocked Numba modes still correctly bounded pending Goal3920
   A5000 timing?
5. Do the reports and tests avoid release/public-speedup/broad-RT-core/
   true-zero-copy/automatic-partner-selection overclaims?
6. What should be improved before the next pod performance packet?

## Required Output

Write your review to:

`docs/reviews/goal3926_gemini_review_goal3924_3925_numba_coverage_2026-06-08.md`

Use one of the project verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

If you cannot run tests, state that limitation and ground the review in source
and artifact inspection.
