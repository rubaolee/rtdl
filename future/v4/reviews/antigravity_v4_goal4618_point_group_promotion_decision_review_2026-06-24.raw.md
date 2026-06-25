# Antigravity Review: Phoenix V4 Point-Group Promotion Decision

Date: 2026-06-24
Reviewer: Antigravity (independent external review)
Decision Packet: future/v4/reviews/call_for_review_v4_goal4618_point_group_promotion_decision_2026-06-24.md

---

## Verdict

**`authorize_point_group_promotion_patch`**

---

## Findings and Explanation

* **Verified Correctness Parity:** Parity checks successfully passed for both 32,768 and 131,072 query sizes using the `mixed6` validation fixture, confirming that direct device output matches expected legacy host results for neighbor IDs and float32 distance semantics.
* **Significant Performance Speedups:** Direct device-output paths show median execution times of 0.000575s (32K) and 0.000476s (131K), representing speedups of 509.39x and 1863.10x respectively against legacy host-row materialization due to the elimination of host-to-device data transfers and serialization overhead in the hot run path.
* **Resolved Coverage Concerns:** The introduction of the `mixed6` validation fixture successfully closes Claude's prior advisory concern by exercising diagonal hits and diagonal no-hits, verifying correct behavior for non-axis misses.
* **Conservative Claim Boundary:** The evidence metadata correctly maintains strict boundaries, marking `release_claim_authorized`, `broad_v4_speedup_claim_authorized`, `whole_app_speedup_claim_authorized`, and `true_zero_copy_authorized` as `false`. This keeps direct device columns from being misrepresented as full input zero-copy.
* **Validated OptiX ABI Ceiling:** The validation is properly bounded to a maximum of OptiX 8.0, NVIDIA RTX A5000/Ampere, driver 570.195.03, and Torch 2.8.0+cu128. OptiX 9.1 is explicitly excluded pending a separate validation.

---

## Required Post-Patch Gates

The following gates are required after the atomic promotion patch is applied, before `goal4618` is closed and proceeds to 3-AI completion review:

1. **Local Test Suite Validation:** All updated local tests (including catalog, frontdoor, and device array API tests) must pass cleanly.
2. **GPU Catalog Regression Gate:** The regression gate script (`scripts/v4_catalog_regression_gate.py`) must run successfully on the POD with `point_group_nearest_witness` classified as a measured surface, confirming `measured_surface_count == 5` and `candidate_surface_count == 0` when include-candidates is False.
3. **ABI Scope Placement:** The OptiX 8.0 maximum-validated ABI ceiling must be documented directly in the measured catalog entry in `src/rtdsl/v4_operator_catalog.py`, not just in evidence files.
4. **3-AI Completion Review:** Consensus of 3-AI reviewers must accept the patch and gate results before final closure of `goal4618`.

---

## Non-Authorization Boundaries (Preserved)

This decision strictly **does not authorize**:
* V4 release.
* Broad V4 or whole-app speedup wording.
* Public "true zero-copy" wording.
* Tier-3 callback support or raw OptiX callback support.
* C ABI / embedding / non-Python host work.
* App-specific native kernels (e.g., spatial-join, DBSCAN, Barnes-Hut, or domain-specific routes).
* CuPy performance claims (CuPy remains unmeasured).
* OptiX 9.1 scope.
