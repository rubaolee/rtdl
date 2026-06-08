# Handoff: Gemini Review Goal3921 Partner Guidance Refresh

Please independently review Goal3921, which updates the machine-readable
partner-choice guidance after newer Numba reference work.

## Files To Inspect

- `src/rtdsl/v2_6_partner_choice_guidance.py`
- `tests/goal3054_v2_6_partner_choice_guidance_test.py`
- `tests/goal3921_partner_choice_guidance_after_numba_reference_refresh_test.py`
- `docs/reports/goal3921_partner_choice_guidance_after_numba_reference_refresh_2026-06-08.md`
- `docs/learn/benchmark_partner_reference_matrix.md`
- `docs/learn/partner_choice_for_custom_logic.md`

## Questions

1. Does the RT-DBSCAN guidance correctly move the current reference path to
   Numba while preserving CuPy as a same-contract baseline/opponent?
2. Does the RT-DBSCAN row avoid overclaiming the blocked Numba variants before
   Goal3920 A5000 timing evidence lands?
3. Does the Barnes-Hut guidance correctly keep CuPy as the measured winner
   while exposing Numba as a no-RawKernel exact-force reference?
4. Do the updated tests protect the guidance and public docs from drifting
   backward?
5. Are all claim boundaries intact: no auto partner selection, no public
   speedup claim, no release authorization, no true-zero-copy wording, and no
   app-specific native-engine logic?

## Expected Output

Write your review to:

`docs/reviews/goal3922_gemini_review_goal3921_partner_guidance_refresh_2026-06-08.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. Please state that this is an independent Gemini review distinct from
Codex authoring.
