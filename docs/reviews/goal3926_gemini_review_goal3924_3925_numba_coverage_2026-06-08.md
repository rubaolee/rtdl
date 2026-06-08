# Gemini Review: Goal3926 Gemini Review Of Goal3924-3925 Numba Coverage

**Date:** 2026-06-08  
**Verdict:** `accept`

## Summary

This review covers Goals 3924 and 3925, which focus on verifying Numba functional readiness and recording the current custom-partner coverage for the v2.6 benchmark suite. The work ensures that users have Numba reference implementations for all benchmark apps requiring custom continuation logic, fulfilling the project mandate to avoid forcing users into CuPy RawKernel code.

## Answered Questions

### 1. Does Goal3924 honestly classify local Linux GTX 1070 smoke evidence as functional readiness only, not release performance evidence?

**Yes.** Goal3924 explicitly states that the local GTX 1070 results are "functional readiness evidence only" and "not release performance evidence." The report and its corresponding test (`tests/goal3924_local_linux_rtdbscan_numba_optix_smoke_test.py`) rigorously maintain this boundary, preventing any unauthorized benchmark-speedup claims based on local development hardware.

### 2. Does Goal3925 correctly distinguish primitive-first apps from apps needing custom Numba continuation logic?

**Yes.** Goal3925 provides a systematic audit of the ten-app suite. It correctly identifies `hausdorff_xhd` and `rtnn` as `rtdl_primitive` first, while flagging `spatial_rayjoin`, `rt_dbscan`, `raydb_style`, and `triangle_counting` as requiring Numba references for custom continuations (e.g., row-stream compaction, component labeling, grouped scalar reductions).

### 3. Does the guidance avoid any CuPy-only recommended custom-continuation gap?

**Yes.** The `src/rtdsl/v2_6_partner_choice_guidance.py` script and the Goal3925 audit confirm that every app requiring custom logic now has a Numba reference path. Even for `barnes_hut`, where CuPy remains the fastest measured partner, a Numba "no-RawKernel" reference is provided and documented for users who prefer Python JIT.

### 4. Are RTDBSCAN blocked Numba modes still correctly bounded pending Goal3920 A5000 timing?

**Yes.** Both the Goal3924 smoke report and the `v2_6_partner_choice_guidance.py` metadata explicitly state that the blocked column-signature modes for RTDBSCAN "await A5000 timing before default promotion" (Goal3920). The tests confirm this bounding.

### 5. Do the reports and tests avoid release/public-speedup/broad-RT-core/true-zero-copy/automatic-partner-selection overclaims?

**Yes.** The reports include explicit "Boundary" sections. Furthermore, the `V26PartnerChoiceGuidanceRow` class in the implementation enforces these boundaries by raising `ValueError` if any authorization flags (e.g., `public_speedup_claim_authorized`) are set to `True`.

### 6. What should be improved before the next pod performance packet?

- **Parity Verification:** While `triangle_counting` mentions CPU parity, a more systematic "parity-by-default" verification should be integrated into the Numba contract evidence for all custom continuations to ensure the references are not just functional but numerically correct.
- **Path Standardization:** Ensure the Numba reference implementations are easily discoverable for users, possibly by providing a centralized lookup or standardized location in the `examples/` directory.
- **Guidance Transition Plan:** Establish a clear path for transitioning `rt_dbscan` from `measured_reference_path` to `recommended_reference_path` immediately following the Goal3920 A5000 evidence intake.

## Technical Inspection Notes

- **Source Integrity:** The use of `dataclasses` and explicit validation in `src/rtdsl/v2_6_partner_choice_guidance.py` is excellent for maintaining machine-checkable constraints.
- **Test Coverage:** The tests for Goals 3921, 3924, 3925, and 3054 provide comprehensive coverage of both the report content and the underlying metadata logic.
- **Audit Depth:** Goal3925 successfully reconciles the recent Numba work (Goals 3918-3924) with the broader v2.6 roadmap.

## Limitation

This review was conducted as a read-only inspection of source code and report artifacts. No tests were executed on local or pod hardware.
