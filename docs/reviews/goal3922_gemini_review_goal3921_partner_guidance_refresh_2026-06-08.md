# Independent Gemini Review for Goal3921 Partner Guidance Refresh

**Reviewer:** Gemini (Independent AI)
**Date:** 2026-06-08
**Verdict:** accept-with-boundary

This is an independent Gemini review, distinct from Codex authoring.

## Files Inspected:

*   `src/rtdsl/v2_6_partner_choice_guidance.py`
*   `tests/goal3054_v2_6_partner_choice_guidance_test.py`
*   `tests/goal3921_partner_choice_guidance_after_numba_reference_refresh_test.py`
*   `docs/reports/goal3921_partner_choice_guidance_after_numba_reference_refresh_2026-06-08.md`
*   `docs/learn/benchmark_partner_reference_matrix.md`
*   `docs/learn/partner_choice_for_custom_logic.md`

## Questions and Answers:

### 1. Does the RT-DBSCAN guidance correctly move the current reference path to Numba while preserving CuPy as a same-contract baseline/opponent?

Yes, the `rt_dbscan` row in `src/rtdsl/v2_6_partner_choice_guidance.py` now lists `recommended_partner="numba"` and describes `cupy_role="established prepared-grid/components baseline and same-contract opponent"`. This is further supported by `docs/learn/benchmark_partner_reference_matrix.md` and `docs/learn/partner_choice_for_custom_logic.md`, which state that Numba is the current reference path while CuPy remains a baseline/opponent. The test `test_rt_dbscan_recommends_numba_and_keeps_blocked_modes_timing_bounded` in `tests/goal3921_partner_choice_guidance_after_numba_reference_refresh_test.py` also confirms this.

### 2. Does the RT-DBSCAN row avoid overclaiming the blocked Numba variants before Goal3920 A5000 timing evidence lands?

Yes, the `numba_role` for `rt_dbscan` explicitly states "blocked column-signature modes are added but await A5000 timing before default promotion" in `src/rtdsl/v2_6_partner_choice_guidance.py`. The `user_advice` further cautions to "treat blocked variants as timing candidates until Goal3920 pod evidence lands." The `docs/reports/goal3921_partner_choice_guidance_after_numba_reference_refresh_2026-06-08.md` also explicitly mentions this, as does the relevant test, ensuring no overclaiming.

### 3. Does the Barnes-Hut guidance correctly keep CuPy as the measured winner while exposing Numba as a no-RawKernel exact-force reference?

Yes, the `barnes_hut` row in `src/rtdsl/v2_6_partner_choice_guidance.py` lists `recommended_partner="cupy"` with `cupy_role="active exact force-vector partner reference"` and `numba_role="measured no-RawKernel exact-force reference; near-CuPy but not the default winner"`. This is consistently reflected in `docs/learn/benchmark_partner_reference_matrix.md` and `docs/learn/partner_choice_for_custom_logic.md`. The test `test_barnes_hut_keeps_cupy_winner_but_exposes_numba_reference` in `tests/goal3921_partner_choice_guidance_after_numba_reference_refresh_test.py` confirms these roles.

### 4. Do the updated tests protect the guidance and public docs from drifting backward?

Yes, the tests `tests/goal3054_v2_6_partner_choice_guidance_test.py` and `tests/goal3921_partner_choice_guidance_after_numba_reference_refresh_test.py` collectively provide strong protection. `goal3054_v2_6_partner_choice_guidance_test.py` validates the overall structure, claim boundaries, and core recommendations. `goal3921_partner_choice_guidance_after_numba_reference_refresh_test.py` specifically targets the changes made in Goal3921 for RT-DBSCAN and Barnes-Hut, asserting their updated roles and ensuring the claim boundaries related to these changes are upheld. The tests assert against specific values and key phrases in the documentation and code.

### 5. Are all claim boundaries intact: no auto partner selection, no public speedup claim, no release authorization, no true-zero-copy wording, and no app-specific native-engine logic?

Yes, all claim boundaries are robustly maintained.
- The `V26PartnerChoiceGuidanceRow` class in `src/rtdsl/v2_6_partner_choice_guidance.py` explicitly defaults all authorization flags (e.g., `automatic_partner_selection_allowed`, `public_speedup_claim_authorized`) to `False` and raises a `ValueError` if any are set to `True`.
- The `validate_v2_6_partner_choice_guidance` function further checks that these flags remain `False` at the module level and for each row.
- The `V2_6_PARTNER_CHOICE_CLAIM_BOUNDARY` string explicitly disavows these claims, and this string is included in the metadata.
- The public-facing documentation (`docs/learn/benchmark_partner_reference_matrix.md`, `docs/learn/partner_choice_for_custom_logic.md`) and the `docs/reports/goal3921_partner_choice_guidance_after_numba_reference_refresh_2026-06-08.md` report consistently reinforce these boundaries.
- The tests `test_guidance_validates_and_covers_all_promoted_benchmark_apps` and `test_explain_helper_respects_user_choice_without_auto_selecting` in `tests/goal3054_v2_6_partner_choice_guidance_test.py`, and `test_report_records_non_authorizing_metadata_only_boundary` in `tests/goal3921_partner_choice_guidance_after_numba_reference_refresh_test.py` all verify these claim boundaries.

---
**Verdict:** accept-with-boundary
**Verdict Rationale:** The changes correctly update the partner guidance for RT-DBSCAN and Barnes-Hut in both the programmatic and human-readable documentation, consistent with the described Numba reference work. All critical claim boundaries are explicitly maintained and validated by the code, documentation, and comprehensive tests. The update avoids overclaiming by clearly stating the status of blocked Numba variants and their dependency on future timing evidence.
