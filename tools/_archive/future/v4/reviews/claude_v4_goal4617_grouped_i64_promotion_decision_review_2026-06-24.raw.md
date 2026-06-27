I have read all three evidence JSON files. Now I'll render the formal review.

---

## External Reviewer Decision — `goal4617` Grouped-I64 Promotion

**Date:** 2026-06-24
**Reviewer:** Claude (external, acting in review-only capacity)
**Evidence examined:** All three width-gated POD evidence files (width=1, 16, 256)

---

## Verdict

**`authorize_grouped_i64_promotion_patch`**

---

## Findings by Severity

### Critical (blocking) — None

No blocking findings. All six gated runs passed. No unauthorized claims detected in evidence metadata.

### Major (non-blocking) — None

### Informational / Minor

**I-1: Single-session, single-machine evidence.**
All three width runs share hostname `0256b71980f1` and ran within a 41-second window (22:40:48–22:41:29 UTC). This is consistent with the V4 gating standard for Tier-2 operators and does not block promotion. It is correctly scoped to one hardware configuration.

**I-2: Group-width=256 ratio is modest (1.64x at 32K rays, 2.98x at 131K rays).**
The packet correctly explains this mechanically: with 128–512 group rows, the legacy route's host materialization cost is small and the delta narrows. Parity still holds at all widths. The operator is not a performance regression at any tested point. This should be noted in measured-catalog documentation so callers understand the benefit is group-count-dependent.

**I-3: `measured_partner: false` / `measured_partners: []` in all evidence records.**
This is correct pre-promotion state. The patch will update these fields atomically. No action required before the patch.

**I-4: `true_zero_copy_authorized: false` is correctly maintained throughout.**
The device-output route uses `device_ray3d_columns_gpu_pack` transfer mode, not zero-copy. This is accurately reflected. No issue.

**I-5: OptiX 9.1 not tested.**
The packet accounts for this with an explicit maximum-ABI ceiling. Acceptable for measured-catalog promotion under OptiX 8.0 scope. The ceiling must appear in the catalog entry itself, not only in the evidence file.

---

## Explicit Answers to the Six Reviewer Questions

**Q1. Should grouped-i64 be authorized for the atomic measured-catalog promotion patch, or kept as candidate?**

Authorized. All six parity checks across three group widths and two ray counts passed, double-verified against both analytic fixture and legacy host output. The evidence is internally consistent, the claim boundary is conservative, and all prior amendment requirements are addressed by the proposed patch.

**Q2. Does the new group-width evidence close the prior A1 coverage concern?**

Yes. Advisory A1 asked for multiple group widths or an explicit validated scope. The evidence spans a 256× range in group width (1, 16, 256) at two ray counts each, covering both the high-ratio regime (width=1, 411x) and the low-ratio regime (width=256, 1.64x). All combinations pass parity. The coverage concern is closed.

**Q3. Is the OptiX 8.0 maximum-validated ABI scope acceptable for measured-catalog promotion, or must OptiX 9.1 be tested first?**

Acceptable. The proposed scope statement (OptiX 8.0, RTX A5000/Ampere, driver 570.195.03, Python 3.12.3, Torch 2.8.0+cu128) is honest and complete. OptiX 9.1 is explicitly and correctly excluded pending a separate validated gate. The scope ceiling must appear verbatim in the catalog entry for grouped-i64. OptiX 9.1 testing is not required before this promotion.

**Q4. Are the proposed patch steps sufficient to satisfy R1/R2/R4 without claim drift?**

Yes. Patch steps 1–5 satisfy R2 (atomic catalog + claim boundary update). Patch step 6 satisfies R1 (inclusion in GPU-mode catalog gate) and R4 (quickstart count from 3→4). The non-authorization flags (`release_claim_authorized: false`, `broad_v4_speedup_claim_authorized: false`, `whole_app_speedup_claim_authorized: false`, `tier3_callback_claim_authorized: false`, `true_zero_copy_authorized: false`) are explicitly preserved in the patch specification. No claim drift is introduced.

**Q5. Are any additional correctness or performance gates required before the patch may be applied?**

No. The post-patch gates listed below are sufficient. No additional pre-patch gates are required.

**Q6. If promotion is authorized and the post-patch GPU gate passes, may `goal4617` proceed to 3-AI completion review?**

Yes, subject to the post-patch gates below passing without exception.

---

## Required Post-Patch Gates Before `goal4617` Completion

The following gates are required after the atomic patch is applied, before `goal4617` proceeds to 3-AI completion review:

1. **Local test suite must pass** (patch step 8). All updated tests in `tests/v4_operator_catalog_test.py`, `tests/v4_frontdoor_test.py`, `tests/v4_ray_triangle_device_array_api_test.py`, and `tests/v4_catalog_regression_gate_test.py` must pass cleanly.

2. **GPU catalog regression gate must pass in measured mode** (patch step 8). The gate in `scripts/v4_catalog_regression_gate.py` must run successfully on the POD with grouped-i64 classified as a measured surface. The gate result must confirm `measured_surface_count == 4`. This run is the R1 satisfaction record.

3. **The OptiX 8.0 ABI ceiling must appear in the measured catalog entry itself**, not only in the evidence file or this decision record. If the patch does not include this scope statement in the catalog, that is a pre-completion defect.

4. **3-AI completion review** must accept the patch and gate results before `goal4617` is closed.

---

## Non-Authorization Boundaries (Preserved)

This authorization does not authorize:

- V4 release
- Broad V4 speedup wording
- Whole-app speedup wording
- Public true-zero-copy wording
- Tier-3 callback support
- Raw OptiX callback support
- C ABI / embedding / non-Python host work
- App-specific native kernels (Barnes-Hut, RayDB, DBSCAN, or similar)
- CuPy performance claims
- OptiX 9.1 scope
