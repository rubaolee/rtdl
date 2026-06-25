I have verified all key evidence. Here is my formal verdict.

---

## External Completion Review — `goal4617` Grouped-I64 Promotion

**Date:** 2026-06-24
**Reviewer:** Claude (external completion reviewer, acting in review-only capacity)
**Evidence examined:** Pre-patch authorization decisions (Claude + Antigravity retry), multi-width POD evidence (width 1/16/256), post-patch dry-run catalog gate, post-patch GPU catalog gate, live catalog source.

---

## Verdict

**`accept_goal4617_complete`**

---

## R1/R2/R3/R4 Closure

**R1 — GPU measured-mode catalog gate with `measured_surface_count == 4`**
Closed. `v4_goal4617_catalog_gpu_after_grouped_i64_promotion_32768_2026-06-24.json` shows `status: passed`, `mode: gpu`. The frontdoor quickstart payload records `measured_surface_count: 4`, `candidate_surface_count: 1`. `primitive_grouped_i64_reduction` example `payload_status: measured`. All 9 examples passed.

**R2 — Atomic catalog and claim boundary update**
Closed. `v4_operator_catalog.py` lines 36–47 show `V4_TIER2_PRIMITIVE_GROUPED_I64_REDUCTION` in `V4_TIER2_OPERATOR_SURFACES` with `measured_partners: ("torch",)` and `declared_unmeasured_partners: ("cupy",)`. `V4_TIER2_CANDIDATE_OPERATOR_SURFACES` contains only point-group nearest witness (`candidate_surface_count: 1`). Measured/candidate counts are consistent with pre-patch authorization (3→4 measured, 2→1 candidate).

**R3 — OptiX 8.0 ABI ceiling in the catalog entry itself**
Closed. `v4_operator_catalog.py` lines 42–47 record `validated_optix_abi: "8.0"`, `validated_gpu_family: "RTX A5000 / Ampere"`, `validated_driver: "570.195.03"`, `validated_partner_scope: "torch 2.8.0+cu128"`, `optix_9_1_validated: False` directly in the catalog dict for the grouped-i64 surface — not only in evidence prose. These fields propagate correctly into the GPU gate example payload (lines 407–410 of the GPU gate JSON).

**R4 — Quickstart `measured_surface_count: 4`**
Closed. Both dry-run (`measured_surface_count: 4` at line 159 of dry-run JSON) and GPU-mode frontdoor quickstart (`measured_surface_count: 4` at line 829 of GPU gate JSON) confirm the count. `candidate_operator_count: 1` is also consistent.

---

## Post-Patch Gate Summary

| Gate | Result |
|---|---|
| Local unit tests (35 tests) | `OK` in 8.880s |
| Python compile gate (6 files) | passed |
| Dry-run catalog gate | `status: passed`, `measured_surface_count: 4`, `candidate_surface_count: 1` |
| GPU catalog gate (RTX A5000, 32768 rays) | `status: passed`, `mode: gpu`, grouped-i64 `measured`, point-group `measured_candidate` |
| Multi-width POD evidence (width 1/16/256 × 32K/131K) | All 6 parity runs passed |

---

## Claim Drift Check

No drift detected. Verified across catalog source, GPU gate JSON, and dry-run JSON:

- `release_claim_authorized: false` — maintained at all levels
- `broad_v4_speedup_claim_authorized: false` — maintained
- `whole_app_speedup_claim_authorized: false` — maintained
- `tier3_callback_claim_authorized: false` — maintained
- `true_zero_copy_authorized: false` for grouped-i64 — maintained (the `device_ray3d_columns_gpu_pack` transfer mode correctly excludes zero-copy)
- CuPy remains `declared_unmeasured_partners` only — no CuPy performance claim introduced
- `optix_9_1_validated: False` — explicit in catalog and propagated to GPU gate payload
- Point-group nearest witness status is `measured_candidate` / `candidate_pod_repeat_gate_passed_requires_external_review_before_release_scope` — not promoted, correctly gated

One noted pre-patch evidence artifact: the width-1/16/256 POD JSON files show `measured_partner: false` / `measured_partners: []` because they were generated before the promotion patch. The packet correctly identifies these as historical pre-patch records. The post-patch GPU gate confirms the promotion took effect.

---

## Authorization Boundaries Preserved

The following remain unauthorized and are confirmed false in all live evidence:

- V4 release
- Broad V4 speedup wording
- Whole-app speedup wording
- Public true-zero-copy wording
- Tier-3 callback support
- Raw OptiX callback support
- C ABI / embedding / non-Python host work
- App-specific native kernels
- CuPy performance claims
- OptiX 9.1 scope

---

## May Codex Begin `goal4618`?

**Yes.** All pre-patch authorization gates (R1–R4), post-patch local and POD gates, and claim boundary checks are satisfied. `goal4617` is complete. Codex may proceed to `goal4618` without further action on this goal.
