---

## Closure Record — V4 Section 8 Device-Array Front-Door

**Date:** 2026-06-24
**Reviewer:** Claude (Sonnet 4.6)
**Scope:** Amendment verification only; no re-review of underlying evidence.

---

### Amendment 1 — CuPy status: Torch is measured, CuPy is unmeasured

**Satisfied.**

- Report (lines 55–57): explicitly states "The measured partner is Torch CUDA tensors. The harness has a CuPy mode, but CuPy was not installed on the measured pod, so this report does not claim CuPy performance or CuPy product readiness."
- JSON: `"measured_partners": ["torch"]`, `"partner_support_declared_unmeasured": ["cupy"]`. These fields are structurally distinct; no ambiguity.
- Harness: computes `partner_support_declared_unmeasured` as the complement of the measured partner — mechanically correct.
- Test: asserts `measured_partners == ["torch"]` and `"cupy" in partner_support_declared_unmeasured` — locked by test.

---

### Amendment 2 — `authorized_next_step` requires productizing fixed-radius API wrapper before second primitive; no `or_next_primitive`

**Satisfied.**

- JSON (line 23): `"authorized_next_step": "external_review_then_productize_fixed_radius_api_wrapper_before_second_primitive"`.
- Harness (`_evaluate_gate`, lines 304–309): the pass branch encodes this exact string; the fail branch encodes `"stop_second_primitive_work_and_continue_product_boundary_reduction"`. Neither branch contains `or_next_primitive`.
- Report "Next Engineering Target" (lines 149–154) is consistent: step 1 is the public API wrapper, step 3 gates a second primitive on review acceptance of the wrapper.

---

### Amendment 3 — Report explains cold-start prepare anomaly

**Satisfied.**

- Report (lines 84–88): "The first measured size reported a much larger `prepare_sec` than the later sizes. That is consistent with CUDA context creation and OptiX module/library initialization on the first prepared call; prepare time is outside the timed hot path above. Later steady-state prepares were in the 2-5 ms range for the larger fixtures."
- JSON confirms the numbers: first size `prepare_sec ≈ 0.546 s`; second `≈ 0.0025 s`; third `≈ 0.0050 s`. The textual claim and data are consistent.
- The report correctly places `prepare_sec` outside the timed hot path, so the anomaly does not contaminate timing conclusions.

---

### Amendment 4 — Report clarifies true zero-copy vs internal device staging

**Satisfied.**

- Report (lines 113–117): "The JSON metadata uses `true_zero_copy_authorized` for the caller-supplied columns and output columns: those buffers avoid host staging in the hot path. It also discloses internal device-resident AABB/BVH staging inside the native route. Those two facts are compatible: zero-copy here means no host round-trip for the user-facing array handoff, not absence of native device workspace."
- JSON per-result metadata: `"true_zero_copy_authorized": true`, `"internal_device_staging_disclosed": true`, `"internal_device_staging_scope": "device-resident AABB/BVH staging may occur inside the native route"`. Both flags present and reconciled.

---

### Non-Authorization Integrity Check

All non-authorizations from the original review remain intact in both the report and the JSON:

| Prohibition | Report | JSON |
|---|---|---|
| V4 release | explicitly listed under Unauthorized Claims | `release_claim_authorized: false` |
| Broad V4 speedup wording | explicitly listed | no broad speedup claim present |
| Whole-app speedup wording | explicitly listed | `whole_app_speedup_claim_authorized: false` (per-result metadata) |
| Tier 3 callback/PTX claims | explicitly listed | `tier3_callback_claim_authorized: false` |
| RT-core speedup claim | not claimed | `rt_core_speedup_claim_authorized: false` (per-result metadata) |

---

## Verdict

**`accept_amendments_closed_continue_fixed_radius_api`**

All four amendments are present, structurally correct, and consistent across the report, JSON evidence, harness, and test. No non-authorizations have been weakened or removed. The packet is closed as the baseline for the next step: productize the fixed-radius public API wrapper (Torch as measured first partner, CuPy gated until measured) before any second Tier 2 primitive work begins.
