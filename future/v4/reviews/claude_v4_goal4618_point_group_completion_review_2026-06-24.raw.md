I have all the evidence I need. Here is the formal verdict.

---

## External Critical Review: `goal4618` Point-Group Completion

**Reviewer:** Claude Sonnet 4.6 (external, independent review)
**Date:** 2026-06-24
**Packet:** `v4_point_group_nearest_witness_2d_device_arrays` — post-patch completion

---

## Verdict

**`accept_goal4618_complete`**

All pre-patch authorization conditions are met, both prior M-concerns are closed, the post-patch GPU catalog gate passes cleanly, and no claim boundary drift was found at any layer.

---

## Reviewer Question Responses

**Q1 — Does the patch correctly implement the pre-patch authorization?**

Yes. The pre-patch authorization (`authorize_point_group_promotion_patch`) required: Torch moves to measured, CuPy remains declared_unmeasured, validated scope locked to OptiX 8.0 / RTX A5000 / Ampere / torch 2.8.0+cu128, no true-zero-copy. Verified directly in `src/rtdsl/v4_operator_catalog.py`: `measured_partners: ("torch",)`, `declared_unmeasured_partners: ("cupy",)`, `validated_optix_abi: "8.0"`, `optix_9_1_validated: False`, `distance_precision: "float32_computed_float64_output"`, `prepared_search_groups: "rtdl_owned_native_scene"`. Implementation matches authorization exactly.

**Q2 — Are M-1 and M-2 closed?**

**M-1 (planner gate may select new 5th surface):** CLOSED. The post-patch GPU gate confirms `operator_callback_planning_tier2` still selects `v4_fixed_radius_count_threshold_2d_device_arrays`, not the new surface. The planner example is fixture-pinned; adding the 5th measured surface did not disturb the gate.

**M-2 (candidate status string must not appear on measured Torch surface):** CLOSED. Verified in `src/rtdsl/v4_point_group.py`: when `measured=True` (i.e., partner is Torch), `partner_claim_status` is `"measured_on_v4_goal4618_pod_optix8"`. The `candidate_pod_repeat_gate_passed_requires_external_review_before_release_scope` string is gone from the measured partner path. CuPy correctly receives `"declared_unmeasured_not_performance_ready"`. The GPU gate evidence at the point-group example confirms `partner_claim_status: "measured_on_v4_goal4618_pod_optix8"` and `measured_partner: true`.

**Q3 — Does the post-patch GPU catalog gate satisfy the measured-catalog gate?**

Yes. Verified from `v4_goal4618_catalog_gpu_after_point_group_promotion_32768_2026-06-24.json`:
- `status: passed`, `mode: gpu`
- 9 examples, all `passed: true`
- Point-group: `status: measured`, `correctness_passed: true`, `distances_match: true`, `query_ids_match: true`, `neighbor_ids_match: true`
- `measured_surface_count: 5`, `candidate_surface_count: 0` (confirmed by frontdoor quickstart payload in same gate)
- `include_candidates: false`
- `release_authorized: false` at top level

**Q4 — Is the OptiX 8.0 / float32-distance / RTDL-owned-prepared-search scope visible enough?**

Yes. The catalog source explicitly records all three scope-limiting fields: `validated_optix_abi`, `distance_precision: "float32_computed_float64_output"`, and `prepared_search_groups: "rtdl_owned_native_scene"`. These propagate faithfully into the catalog dump and are confirmed in the GPU gate payload (`native_prepared_search_groups_owned_by_rtdl: true`, `distance_precision: "float32_computed_float64_output"`, `validated_optix_abi: "8.0"`). Scope visibility is sufficient.

**Q5 — Any claim-status drift, release drift, true-zero-copy drift, or app-specific-kernel drift?**

None found. Checked at three layers (catalog source, GPU gate payloads, frontdoor quickstart):

| Flag | Status |
|---|---|
| `release_claim_authorized` | `false` everywhere |
| `broad_v4_speedup_claim_authorized` | `false` everywhere |
| `whole_app_speedup_claim_authorized` | `false` everywhere |
| `tier3_callback_claim_authorized` | `false` everywhere |
| `true_zero_copy_authorized` (point-group) | `false` consistently |
| `app_specific_native_kernel_authorized` | `false` at gate top-level |
| `cupy_performance_claim_authorized` | `false` everywhere |
| `non_python_host_binding_claim_authorized` | `false` everywhere |
| `optix_9_1_validated` | `false` everywhere |
| `front_door_status` | `v4_development_front_door_not_release` |

No candidate string appears in any measured surface field. No drift.

**Q6 — May `goal4618` be marked complete and may Codex begin `goal4619`?**

Yes. Confirmed below.

---

## Claim Boundary Enforcement Confirmed

This review does NOT authorize the following; their prohibition flags are correctly locked in evidence:

- V4 release
- Broad V4 or whole-application speedup wording
- Public true-zero-copy wording (point-group surface has `true_zero_copy_authorized: false`; the fixed-radius and any-hit-flags surfaces retain their pre-existing true-zero-copy authorizations, which are not new or changed by this patch)
- Tier-3 callbacks or raw OptiX callback support
- C ABI / embedding / non-Python host work
- App-specific native kernels
- CuPy performance claims
- OptiX 9.1 scope

The mixed6 POD ratios (509x at 32K, 1863x at 131K) are correctly scoped as same-contract comparisons against the legacy host-row route and do not constitute broad speedup claims.

---

## Finding Log

**BLOCKING:** None.

**MEDIUM:** None. (M-1 and M-2 from the pre-patch decision review are both closed by post-patch evidence.)

**LOW (informational, no action required to close goal4618):**

- The float32-compute / float64-output distance precision distinction is recorded in the catalog and in gate metadata, but the L-1 documentation note from the pre-patch review remains relevant for any future user-facing surface description.
- The `V4_POINT_GROUP_POD_CANDIDATE_PARTNERS` and `V4_POINT_GROUP_CANDIDATE_STATUS` constants are not visible in the current catalog source; if they were removed or are not emitted on the measured path, no further action needed. If they remain as dead code, they may confuse future readers but do not affect correctness of this gate.

---

**`accept_goal4618_complete`**

Codex may mark `goal4618` complete and begin `goal4619`.
