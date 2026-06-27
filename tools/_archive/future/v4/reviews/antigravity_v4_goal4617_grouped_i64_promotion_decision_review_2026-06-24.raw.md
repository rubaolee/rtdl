# Antigravity Review: Phoenix V4 Grouped-I64 Promotion Decision

Date: 2026-06-24
Reviewer: Antigravity (independent external review)
Decision Packet: future/v4/reviews/call_for_review_v4_goal4617_grouped_i64_promotion_decision_2026-06-24.md

---

## Verdict

**`authorize_grouped_i64_promotion_patch`**

---

## Findings and Explanation

* **Verified Correctness Parity:** All six multi-width runs (widths 1, 16, 256; ray counts 32,768 and 131,072) passed parity check (`sum_count`, `min`, `max`) comparing the direct device-output front door against the legacy host route.
* **No Performance Regressions:** Median execution times remain faster than the legacy host route across all widths, with the speedup ratio ranging from 1.64x (low-row-count/width=256) up to 411.87x (high-row-count/width=1).
* **Resolved Coverage Concerns:** The new width-gated POD evidence directly closes Claude's prior advisory A1, validating performance and correctness over a 256x range in group widths.
* **Conservative Claim Boundary:** The evidence metadata correctly marks release, broad speedup, whole-app speedup, and true zero-copy claims as unauthorized, preserving catalog and claim integrity.
* **Formally Scoped OptiX ABI:** An honest and complete maximum-validated ABI ceiling is proposed (OptiX 8.0), avoiding unsafe assumptions about untested OptiX 9.1 platforms.

---

## Required Post-Patch Gates

The following gates are required after the atomic promotion patch is applied, before `goal4617` is closed and proceeds to 3-AI completion review:

1. **Local Test Suite Validation:** All updated local tests (including catalog, frontdoor, and device array API tests) must pass cleanly.
2. **GPU Catalog Regression Gate:** The regression gate script (`scripts/v4_catalog_regression_gate.py`) must run successfully on the POD with grouped-i64 classified as a measured surface, confirming `measured_surface_count == 4`.
3. **ABI Scope Placement:** The OptiX 8.0 maximum-validated ABI ceiling must be documented directly in the measured catalog entry in `src/rtdsl/v4_operator_catalog.py`, not just in evidence files.
4. **3-AI Completion Review:** Consensus of 3-AI reviewers must accept the patch and gate results before final closure of `goal4617`.

---

## Non-Authorization Boundaries (Preserved)

This decision strictly **does not authorize**:
* V4 release.
* Broad V4 or whole-app speedup wording.
* Public "true zero-copy" wording.
* Tier-3 callback support or raw OptiX callback support.
* C ABI / embedding / non-Python host work.
* App-specific native kernels (e.g., Barnes-Hut, RayDB, DBSCAN).
* CuPy performance claims (CuPy remains unmeasured).
* OptiX 9.1 scope.
