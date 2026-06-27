# RTDL V4 Goal4626-4632 Scorecard Review Debt Audit

Date: 2026-06-24
Reviewer: Antigravity

## 1. Summary Verdict on Open Scorecard Review-Debt Items

Below is the classification verdict for each of the 9 scorecard review-debt items listed in [v4_goal4626_4632_open_review_debt_tracker_and_forward_message_2026-06-24.md](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/future/v4/reviews/v4_goal4626_4632_open_review_debt_tracker_and_forward_message_2026-06-24.md):

| ID | Goal | Reviewer | Debt Item Description | Verdict |
|---|---|---|---|---|
| **D1** | Goal4626 | Antigravity | Goal4626 Antigravity amendment-check empty output. | `close_debt` |
| **D2** | Goal4627 | Antigravity | Goal4627 Antigravity coverage-audit empty output. | `close_debt` |
| **D3** | Goal4629 | Antigravity | Goal4629 Antigravity amendment-check empty output. | `close_debt` |
| **D4** | Goal4630 | Claude | Goal4630 Claude session limit. | `close_debt` |
| **D5** | Goal4630 | Antigravity | Goal4630 Antigravity empty output. | `close_debt` |
| **D6** | Goal4631 | Claude | Goal4631 Claude session limit. | `close_debt` |
| **D7** | Goal4631 | Antigravity | Goal4631 Antigravity empty output. | `close_debt` |
| **D8** | Goal4632 | Claude | Goal4632 Claude session limit. | `close_debt` |
| **D9** | Goal4632 | Antigravity | Goal4632 Antigravity empty output. | `close_debt` |

***

## 2. Review Analysis and Justification for Each Debt Item

### D1: Goal4626 Antigravity Amendment-Check (Verdict: `close_debt`)
* **Objective:** Review the amended Goal4626 protocol and confirm the Claude amendments are closed.
* **Evidence:** In [v4_goal4626_section8_release_scorecard_protocol_2026-06-24.md](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/future/v4/v4_goal4626_section8_release_scorecard_protocol_2026-06-24.md), both required Claude amendments are successfully integrated:
  1. The Torch device-array front-door evidence chain explicitly includes `claude_v4_section8_device_array_frontdoor_amendment_closure_2026-06-24.md`.
  2. The prerequisite constraint that the fixed-radius API wrapper must be productized before Goal4628 / second primitive work begins is explicitly added to the G3 scorecard row (using the binder `external_review_then_productize_fixed_radius_api_wrapper_before_second_primitive`).
* **Verification:** The regression test in [v4_goal4626_section8_scorecard_protocol_test.py](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v4_goal4626_section8_scorecard_protocol_test.py) asserts both the prerequisite string and the amendment-closure filename.

### D2: Goal4627 Antigravity Coverage Audit (Verdict: `close_debt`)
* **Objective:** Review the Goal4627 coverage audit and confirm the split and triangle-counting candidate-bound amendment.
* **Evidence:** In [v4_coverage_audit.py](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/v4_coverage_audit.py) and [v4_goal4627_tier2_operator_coverage_audit_2026-06-24.md](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/future/v4/v4_goal4627_tier2_operator_coverage_audit_2026-06-24.md):
  - The audited set of 10 promoted benchmark apps contains the exact 1/5/1/3 coverage class split (1 strong measured, 5 partial measured, 1 candidate, and 3 deferred).
  - The `triangle_counting` candidate-bound amendment is closed: the audit explicitly notes that while the measured `grouped_i64` operator covers an adjacent grouped-reduction dimension of the app, its dominant `any_hit_weighted_sum` continuation path remains a candidate only, keeping the app candidate-bound until Goal4629 promotion.
* **Verification:** The test [v4_goal4627_coverage_audit_test.py](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v4_goal4627_coverage_audit_test.py) checks the exact 1/5/1/3 split counts and the candidate-bound explanation.

### D3: Goal4629 Antigravity Amendment-Check (Verdict: `close_debt`)
* **Objective:** Confirm the A1 amendment is closed (future promotion requirements mirror all promotion blockers).
* **Evidence:** In [v4_goal4629_weighted_sum_candidate_decision_2026-06-24.md](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/future/v4/v4_goal4629_weighted_sum_candidate_decision_2026-06-24.md) and [v4_weighted_sum_candidate_decision.py](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/v4_weighted_sum_candidate_decision.py):
  - The decision maintains the weighted-sum operator as a Tier-2 candidate.
  - The future promotion requirements are expanded to mirror all promotion blockers: expanding shape matrices, increasing repeats beyond the 5 candidate trials, measuring CuPy and non-Torch partners, proving primary triangle-counting route coverage, and obtaining explicit external review.
* **Verification:** [v4_goal4629_weighted_sum_candidate_decision_test.py](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v4_goal4629_weighted_sum_candidate_decision_test.py) asserts that all of these expanded promotion requirements are mapped and verified.

### D4 & D5: Goal4630 Claude & Antigravity Push-Down Recognizer (Verdict: `close_debt`)
* **Objective:** Verify the recognizer is a minimal fail-closed slice, and evaluate the CuPy weighted-sum candidate fail-closed amendment.
* **Evidence:** In [v4_operator_catalog.py](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/v4_operator_catalog.py) and [v4_goal4630_pushdown_recognizer_minimum_slice_2026-06-24.md](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/future/v4/v4_goal4630_pushdown_recognizer_minimum_slice_2026-06-24.md):
  - The push-down recognizer is a minimal slice routing generic operators (e.g. `fixed_radius`, `grouped_reduction`) and candidate operators (e.g. `weighted_sum` on Torch CUDA) while failing closed for unsupported logic.
  - The CuPy weighted-sum candidate fail-closed amendment is implemented: any request for a candidate operator (such as `ray_triangle_any_hit_weighted_sum`) utilizing an unmeasured partner like `cupy` is mapped directly to `pushdown_fail_closed_unmeasured_partner` with `pushdown_recognized=False` and `fail_closed=True`.
* **Verification:** [v4_goal4630_pushdown_recognizer_test.py](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v4_goal4630_pushdown_recognizer_test.py) runs test cases for all fail-closed classes: `test_unmeasured_partner_fails_closed`, `test_unmeasured_candidate_partner_fails_closed`, `test_app_identity_kernel_fails_closed_before_planning`, `test_action_shaped_callback_fails_closed`, and `test_scalar_numba_callback_is_tier3_spike_only_not_pushdown`.

### D6 & D7: Goal4631 Claude & Antigravity Tier-3 Spike Decision (Verdict: `close_debt`)
* **Objective:** Review Goal4631 and confirm that Tier-3 remains spike-only/deferred, and verify Stage 1/Stage 2 evidence interpretations.
* **Evidence:** In [v4_tier3_spike_decision.py](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/v4_tier3_spike_decision.py) and [v4_goal4631_tier3_spike_execution_decision_2026-06-24.md](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/future/v4/v4_goal4631_tier3_spike_execution_decision_2026-06-24.md):
  - The decision is `defer_tier3_not_v4_0_supported`, explicitly excluding Tier-3 from the V4.0 release dependency path.
  - Stage 1 is correctly classified as `ptx_generated_narrow_evidence` (useful as research, but fails the protocol's 20-attempt/4-variant requirement).
  - Stage 2 is correctly classified as blocked at `optix_module_create` (attempts to call `optixModuleCreate` on bare helper PTX returned an `Invalid input` error with the log message `No functions with semantic types found`).
* **Verification:** [v4_goal4631_tier3_spike_decision_test.py](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v4_goal4631_tier3_spike_decision_test.py) validates the narrow-evidence interpretation, checks the link-failure blocker, and parses the physical JSON probes to confirm the error matching.

### D8 & D9: Goal4632 Claude & Antigravity Final Release Decision (Verdict: `close_debt`)
* **Objective:** Review the final release scorecard packet and confirm the preview decision.
* **Evidence:** In [v4_release_decision.py](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/v4_release_decision.py) and [v4_goal4632_final_release_decision_2026-06-24.md](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/future/v4/v4_goal4632_final_release_decision_2026-06-24.md):
  - Evaluates all gates G1-G7. Since G2 (limited operator coverage), G4 (weighted-sum remains candidate), and G7 (final release decision) are marked `passed_for_release=False`, the final decision resolved to `development_state_performance_preview_not_release`.
* **Verification:** [v4_goal4632_release_decision_test.py](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v4_goal4632_release_decision_test.py) validates that the preview decision, the G1-G7 gate statuses, the release blockers, and the forbidden claims flags are strictly enforced.

***

## 3. Goal4632 Final Decision: Review of the Release Label

The current label **`development_state_performance_preview_not_release`** is **correct**. 

A formal high-performance release of V4 is not authorized at this time. The codebase must be represented under the following exact authorized public wording:
> *"V4 development-state performance preview for Torch CUDA generic Tier-2 RT-core operators."*

### Key Reasons and Blockers that Prevent a Formal Release:
1. **Limited Operator Coverage:** The coverage audit shows that out of 10 promoted benchmark apps, only 1 (`raydb_style`) has strong measured operator coverage. 5 have partial coverage, 1 has candidate coverage, and 3 are deferred/uncovered.
2. **Weighted-Sum is Candidate-Only:** The primary execution route for `triangle_counting` depends on `weighted_sum` which has not completed a promotion gate (needs expanded shapes, release-level repeat counts, and partner evaluation).
3. **Tier-3 is Blocked:** Numba device function compilation to PTX does not link with OptiX. Attempting direct module creation (`optixModuleCreate`) on bare PTX returns `Invalid input` and `No functions with semantic types found`. An OptiX wrapper or ABI is missing.
4. **Unmeasured Partners:** CuPy performance is unmeasured and requests currently fail closed.
5. **No Whole-App Benchmarks:** There are no all-application benchmark runs to justify whole-application speedup claims.

***

## 4. Minimum Next Engineering and Review Steps for Formal V4 Release

To achieve a formal high-performance V4 release in the future, the following minimum steps are required:

1. **Resolve Review Debt:** Officially close the 9 external scorecard review-debt items reviewed in this document.
2. **Complete Goal4628 Scorecard Gate:** Productize the fixed-radius API wrapper as mandated by G1, then run the scorecard reconciliation and acceptance gate for the second Tier-2 operator (`grouped_i64_reduction` under `raydb_style`).
3. **Execute a Weighted-Sum Promotion Gate:** Promote `weighted_sum` by running an expanded promotion gate containing:
   - At least 5 shape sizes (not just 2).
   - Release-level repetition counts (20+ runs).
   - Parity and performance measurements for CuPy partners.
4. **Develop a Tier-3 OptiX Wrapper / ABI:**
   - Write a C++ OptiX wrapper or direct-callable ABI handler that can structure PTX emitted by Numba device functions into a valid OptiX module.
   - Re-run G6 protocol gates to measure compilation overhead and ensure it does not compromise hot-path performance.
5. **Run Whole-Application Performance Benchmarks:** Rerun the entire benchmark catalog end-to-end to verify that the operator-level same-contract speedups translate into measurable whole-application performance gains.

***

## 5. Reaffirmation of the Non-Authorization Boundary

In accordance with the release scorecard guidelines, the following boundaries remain strictly active:
* **No broad speedup claims** or **whole-application/all-benchmark speedup claims**.
* **No public true-zero-copy claims** (as data structures are still bounded to Torch CUDA array segments).
* **No Tier-3 or raw OptiX callback support** in public docs.
* **No CuPy performance claims**.
* **No C ABI / embedding / non-Python host integration** claims.
* **No app-specific native kernels** (only generic, catalog-mapped operators are supported).
