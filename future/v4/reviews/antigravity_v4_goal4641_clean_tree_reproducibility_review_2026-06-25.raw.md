# RTDL V4 Goal4641 Clean-Tree Reproducibility External Review Report

**Date of Review:** 2026-06-25  
**Reviewer:** Antigravity (External Reviewer)  
**Status:** Completed  

---

## Verdict

`approve_goal4641_clean_tree_reproducibility_continue_goal4642`

---

## Findings by Severity

### Critical / Blocker
- **None.** All reproducibility checks passed successfully.

### Major
- **None.**

### Minor / Informational
- **Missing Dependency Catch:** During the initial clean-tree validation run, a V4 dependency (`scripts/v3_0_m30_librts_prepared_all_ops_refresh.py`) was identified as missing from the committed package. This led to a test failure, which was successfully corrected by committing the file. This is recorded as a useful defect catch rather than hidden, which validates the integrity and utility of the clean-tree validation process.
- **Evidence Timeline:** The clean validation commit (`35d04dbf0b1734e7c1fc323c366a046de51edee8`) represents the state of the codebase at the time validation was executed. The documentation of the gate and decision files was committed subsequently. This is standard and acceptable, provided that the overall CI/CD regression checks run and pass on the final integrated commit.

---

## Answers to the Call-for-Review Questions

### 1. Does Goal4641 actually prove committed clean-tree reproducibility for the V4 release-hardening package?
**Yes.** Goal4641 successfully proves committed clean-tree reproducibility. The validation was performed using a detached clone at commit `35d04dbf0b1734e7c1fc323c366a046de51edee8` in a separate worktree (`C:/Users/Lestat/Desktop/work/rtdl_v4_goal4641_clean_tree_check`). It verified that:
- The full V4 test group runs and passes (`165 tests OK`).
- The catalog dry-run regression gate passes without any failed examples.
- The V4 quickstart example runs successfully with an `ok` status.
- `git status --short` remains clean before and after validation, confirming that no untracked files are required to build, test, or run the package, and no uncommitted modifications or side effects are generated during execution.
- The process successfully caught and forced the correction of a missing dependency (`scripts/v3_0_m30_librts_prepared_all_ops_refresh.py`) that was present locally but omitted from the git tree, demonstrating that the check is robust and effective.

### 2. Is it acceptable that the evidence records the clean validation commit `35d04dbf...`, while the Goal4641 evidence file itself is added after that validation, assuming the local and later clean gates pass?
**Yes.** It is standard practice to validate a clean tree at a specific freeze commit, and then commit the metadata/evidence files confirming the validation afterwards. The subsequent local tests and CI/CD validation gates verify that adding these metadata files does not introduce any regressions or break the clean-tree status.

### 3. Did the release decision correctly remove `goal4641_clean_tree_reproducibility_gate_not_done` while preserving final 3-AI authorization as a blocker?
**Yes.** In [v4_release_decision.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/v4_release_decision.py), the blocker `goal4641_clean_tree_reproducibility_gate_not_done` has been removed from `release_blockers` and the G10 clean-tree gate status has been updated to `passed_for_release=True`. Crucially, the blocker `goal4642_final_3ai_release_authorization_not_done` is preserved, and the final gate G11 (`G11_final_release_authorization`) remains marked with `passed_for_release=False`.

### 4. Did Goal4641 avoid broad release, broad speedup, whole-app speedup, true-zero-copy, Tier-3 callback, CuPy, C ABI, embedding, and non-Python host overclaims?
**Yes.** 
- In [v4_goal4641_clean_tree_reproducibility_decision.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/v4_goal4641_clean_tree_reproducibility_decision.py), the `V4Goal4641CleanTreeReproducibility` class hardcodes all authorization flags to `False` (`release_authorized`, `release_candidate_authorized`, `broad_v4_speedup_claim_authorized`, `whole_app_speedup_claim_authorized`, `true_zero_copy_claim_authorized`, `tier3_callback_claim_authorized`, `cupy_performance_claim_authorized`, `non_python_host_claim_authorized`).
- The validation function `validate_v4_goal4641_clean_tree_reproducibility` asserts that none of these claims are authorized, raising a `ValueError` if any are set to `True`.
- In [v4_release_decision.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/v4_release_decision.py), the `v4_goal4632_release_decision` function maintains all corresponding claim authorization flags as `False`, list of `forbidden_claims` includes all restricted claims, and `validate_v4_goal4632_release_decision` verifies that these flags are strictly `False`.

### 5. Are any amendments required before Goal4642 final 3-AI authorization?
**No amendments are required for Goal4641.** The gate is fully complete, valid, and correctly integrated into the release decision. The remaining external review debts for Goal4633, Goal4635, Goal4637, Goal4638, Goal4639, and Goal4640 are already tracked in the release blockers and will need to be resolved or explicitly closed before final 3-AI authorization.

---

## Non-Authorization Boundary

> [!IMPORTANT]
> **This review does NOT authorize final V4 release, release-candidate wording, broad V4 speedup wording, whole-application speedup wording, public true-zero-copy wording, Tier-3 callback support, raw OptiX callback support, CuPy performance wording, C ABI, embedding, non-Python host bindings, or app-specific native kernels.**
