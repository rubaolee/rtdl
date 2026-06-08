# Gemini Review: Goal3928-3929 Numba Discovery and Parity

- **Review Date:** 2026-06-08
- **Scope:** Goal3928 (Numba Discovery Index) and Goal3929 (Numba Parity Expectations)
- **Verdict:** `accept`

## Summary

This review covers the addition of two advisory helpers, `rtdsl.v2_6_numba_reference_index()` and `rtdsl.v2_6_numba_parity_expectations()`, designed to improve the discoverability and correctness-tracking of Numba benchmark reference implementations.

## Question Responses

### 1. Do the new helpers avoid creating a second source of truth?

**Yes.** The implementation in `src/rtdsl/v2_6_partner_choice_guidance.py` leverages the existing `V2_6_PARTNER_CHOICE_ROWS` as the foundational data. `v2_6_numba_reference_index()` derives its rows directly from these established guidance records. `v2_6_numba_parity_expectations()` further builds upon the index. While parity requirements are stored in a new `V2_6_NUMBA_PARITY_EXPECTATIONS` dictionary, they are keyed by benchmark app IDs that correspond to the main guidance rows, ensuring structural alignment.

### 2. Does `v2_6_numba_reference_index()` clearly answer the discoverability question without auto-selecting a partner?

**Yes.** The index clearly distinguishes between apps where Numba is a recommended reference, a measured alternative, or a future candidate. It explicitly exposes the `numba_role` for every benchmark app. Crucially, it sets `automatic_partner_selection_allowed: False` for every row and for the overall index metadata, maintaining the project doctrine that users must choose partners explicitly.

### 3. Does `v2_6_numba_parity_expectations()` cover all currently available Numba reference rows and keep RTDBSCAN blocked-mode evidence pending?

**Yes.** The helper covers the six benchmark apps with active Numba references: `hausdorff_xhd`, `spatial_rayjoin`, `rt_dbscan`, `raydb_style`, `barnes_hut`, and `triangle_counting`. For `rt_dbscan`, the `parity_status` is explicitly set to `covered_for_unblocked_reference_blocked_modes_pending_goal3920`, correctly identifying that blocked-mode evidence is still awaiting A5000 timing results.

### 4. Do the docs and tests avoid release/public-speedup/broad-RT-core/true-zero-copy/automatic-partner-selection overclaims?

**Yes.** The implementation rigorously enforces this boundary by:
- Including `V2_6_PARTNER_CHOICE_CLAIM_BOUNDARY` in all advisory outputs.
- Hardcoding `False` for all authorization flags (e.g., `public_speedup_claim_authorized`).
- Validating these boundaries in the unit tests (`tests/goal3928_numba_reference_discovery_index_test.py` and `tests/goal3929_numba_reference_parity_expectations_test.py`).
- Adding clear disclaimers in `docs/learn/benchmark_partner_reference_matrix.md` and the report files.

### 5. What should be improved before the next A5000 performance packet?

The primary remaining gap is the completion of **Goal 3920** (RT-DBSCAN blocked-mode evidence). Once Goal 3920 lands with favorable A5000 timing, the `parity_status` for `rt_dbscan` should be updated to `covered` (or similar), and the Numba reference for these modes can be promoted to the default recommendation if it outperforms existing paths.

## Technical Observations

- **Exports:** The new helpers are exposed via `src/rtdsl/__init__.py` but are intentionally excluded from `__all__`. This matches the "narrow advisory" intent and is verified by tests.
- **Test Coverage:** The new tests provide good coverage for the derivation logic and the enforcement of the advisory boundary.
- **Documentation:** The updates to `docs/learn/benchmark_partner_reference_matrix.md` successfully integrate these helpers into the "How To Use" section, making them discoverable via documentation as well as API inspection.

## Verdict Grounds

The changes successfully address the feedback from Goal 3926's review by providing structured, discoverable metadata for Numba without introducing architectural drift or overclaims. The implementation is safe, read-only, and maintainable.
