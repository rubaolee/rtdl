# RTDL V4 Goal4642 Final 3-AI Release Authorization Amendment Recheck Report

**Date of Recheck:** 2026-06-25  
**Reviewer:** Antigravity (External Reviewer)  
**Status:** Completed  

---

## Verdict

`amendments_satisfied_authorize_publication`

### Verdict Clarification and Prior Authorization Status
Prior authorization of the final release remains fully valid under the narrow label: **"RTDL v4.0.0 formal high-performance generic RT-core operator release"**. All out-of-scope and forbidden claims remain forbidden. No claims are broadened by this authorization.

---

## Amendment Audit and Verification

Each of the four required amendments from the Independent Codex review has been verified against the codebase:

### 1. Machine-readable forbidden-claim coverage
* **Implementation:** The forbidden claims `"Barnes-Hut covered by V4.0"`, `"Spatial RayJoin covered by V4.0"`, and `"LibRTS paper reproduction"` have been added to:
  * [src/rtdsl/v4_release_decision.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/v4_release_decision.py#L241-L243) inside `forbidden_claims`.
  * [src/rtdsl/v4_goal4642_final_authorization_packet.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/v4_goal4642_final_authorization_packet.py#L65-L67) inside `forbidden_claims`.
* **Testing:** 
  * [tests/v4_goal4632_release_decision_test.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v4_goal4632_release_decision_test.py#L184-L186) asserts presence in the release decision.
  * [tests/v4_goal4642_final_authorization_packet_test.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v4_goal4642_final_authorization_packet_test.py#L45-L50) asserts presence in the authorization packet structure and verify their inclusion in the generated markdown documentation text.
  * [tests/v4_goal4644_post_release_guardrails_test.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v4_goal4644_post_release_guardrails_test.py#L29-L35) verifies subset inclusion.
* **Status:** **Satisfied**.

### 2. Update README stale status
* **Implementation:** [README.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/README.md#L5-L8) has been updated. The status section now explicitly states: *"Public-doc cleanup and clean-tree reproducibility have passed; final publication remains gated on final release authorization and the publication step."* The stale text stating that they remain pending has been removed.
* **Testing:** Guarded by [tests/v4_goal4644_post_release_guardrails_test.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v4_goal4644_post_release_guardrails_test.py#L48-L49), asserting the updated phrasing is present and the stale phrasing is absent.
* **Status:** **Satisfied**.

### 3. Record final clean-tree revalidation commit in machine state
* **Implementation:** The final revalidation commit hash `437b79a2a382082e269d0d0ee128528caf0ae112` (along with initial commit `35d04dbf0b1734e7c1fc323c366a046de51edee8`) has been recorded directly in the machine state inside [src/rtdsl/v4_goal4641_clean_tree_reproducibility_decision.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/v4_goal4641_clean_tree_reproducibility_decision.py#L62-L63).
* **Testing:** Guarded by [tests/v4_goal4641_clean_tree_reproducibility_test.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v4_goal4641_clean_tree_reproducibility_test.py#L27-L28).
* **Status:** **Satisfied**.

### 4. Guardrail tests to prevent regression
* **Implementation:** A dedicated test suite has been introduced at [tests/v4_goal4644_post_release_guardrails_test.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v4_goal4644_post_release_guardrails_test.py).
* **Details:** The suite runs tests verifying:
  * Machine forbidden claims are subset-verified in both the release decision and authorization packet (`test_machine_forbidden_claims_cover_deferred_and_reproduction_overclaims`).
  * No candidate surfaces are counted as measured surfaces (`test_candidate_surfaces_are_not_counted_as_measured`).
  * README.md contains the updated status language and all public-facing docs retain required release caveats such as "whole-application speedup", "public true-zero-copy", "Tier-3", and "CuPy" (`test_public_docs_keep_release_caveats_and_no_stale_goal4640_4641_gate`).
  * Excluded families like `barnes_hut` and `spatial_rayjoin` are documented as deferred/excluded (`test_deferred_families_remain_out_of_v4_0_claims`).
* **Execution:** All unit tests pass cleanly (`Ran 15 tests, OK`).
* **Status:** **Satisfied**.

---

## Reviewed Files

Only the following requested files were reviewed:
* [README.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/README.md)
* [src/rtdsl/v4_release_decision.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/v4_release_decision.py)
* [src/rtdsl/v4_goal4642_final_authorization_packet.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/v4_goal4642_final_authorization_packet.py)
* [src/rtdsl/v4_goal4641_clean_tree_reproducibility_decision.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/v4_goal4641_clean_tree_reproducibility_decision.py)
* [tests/v4_goal4632_release_decision_test.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v4_goal4632_release_decision_test.py)
* [tests/v4_goal4642_final_authorization_packet_test.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v4_goal4642_final_authorization_packet_test.py)
* [tests/v4_goal4641_clean_tree_reproducibility_test.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v4_goal4641_clean_tree_reproducibility_test.py)
* [tests/v4_goal4644_post_release_guardrails_test.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v4_goal4644_post_release_guardrails_test.py)
* [future/v4/tier2_operator_catalog.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/future/v4/tier2_operator_catalog.md)

---

## Explicit Scope Limitations and Forbidden Claims

> [!IMPORTANT]
> **Release Scope Constraint Verification:**
> 1. Release publication remains authorized **only** under the narrow label: **"RTDL v4.0.0 formal high-performance generic RT-core operator release"**.
> 2. The following claims are strictly out-of-scope, unauthorized, and forbidden:
>    * Broad V4 speedup wording.
>    * Whole-application / all-benchmark speedups.
>    * Public true-zero-copy claims.
>    * Tier-3 callback support or raw OptiX callback support.
>    * CuPy performance claims.
>    * C ABI, embedding, or non-Python host language bindings.
>    * Application-specific native kernels.
>    * Barnes-Hut covered by V4.0 (deferred).
>    * Spatial RayJoin covered by V4.0 (deferred).
>    * LibRTS paper reproduction or author code comparisons.
