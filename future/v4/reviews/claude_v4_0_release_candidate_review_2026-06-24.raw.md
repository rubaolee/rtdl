Now I have everything needed. Let me compose the review.

---

## External Review: RTDL V4.0 Release Candidate Packet

**Date:** 2026-06-24
**Reviewer:** External (Claude Sonnet 4.6)
**Branch reviewed:** `codex/v4-tier2-section8`
**Runtime commit under review:** `7e38a8e8dee36a951f1f41bc33f367d468b9d1b5`

---

## Verdict

**`approve_with_required_amendments`**

The engineering candidate packet is coherently constructed and does not overclaim. All three Tier-2 surfaces pass GPU gate at serious sizes. All prohibited authorization flags are `False` in code, JSON evidence, and documentation. The Tier-3 boundary is clearly established with two layers of spike evidence (PTX generation passed; `optixModuleCreate` on bare PTX blocked). Non-authorization language appears in every artifact reviewed.

Three amendments are required before release authorization can be sought, detailed below.

---

## Findings by Severity

### CRITICAL (blocks release authorization)

**C-1 — `v4_review_debt_open` blocking reason is uncharacterized.**
`v4_scope.py:37` and `v4_scope_gate_2026-06-24.json` both list `"v4_review_debt_open"` as a release blocker. No document in the packet describes what this debt is, how much there is, where it is tracked, or what "waived" means in this context. The blocking reason correctly prevents release, but it is a phantom blocker — it cannot be resolved if no one knows what it refers to. Before any release authorization review can close this item, the debt must be enumerated and linked to a tracker.

**C-2 — No continuous CI gate; evidence is a snapshot run from a single POD worktree.**
The GPU catalog gate is tied to one worktree path (`/root/rtdl_v4_section8/worktrees/v4_final_validation_20260624_1354/`) at one point in time. The local test sweep ran against a working-tree delta (documentation edits were uncommitted at sweep time). This is acceptable for an engineering RC but must not be presented as an ongoing quality gate. Before release authorization, a re-run protocol or CI gate must be established so the claim can be reproduced from a clean commit state.

### MEDIUM (should be addressed before public release)

**M-1 — `closest_hit_grouped_argmin` shows `true_zero_copy_authorized: false` in claim boundary; no user-facing explanation.**
The GPU gate JSON (`v4_final_release_scope_catalog_gate_gpu_32768_2026-06-24.json`, line 130) shows `"true_zero_copy_authorized": false` for the grouped-argmin surface's claim boundary while both other surfaces show `true`. This is a correct and honest disclosure, but it is not documented in user-facing artifacts (`README.md`, the callback/operator docs). If this surface moves toward a public release, users need to understand this distinction.

**M-2 — CuPy unmeasured-partner routing produces a plan rather than an error.**
`v4_operator_catalog.py:123–129` — the planner accepts `partner="cupy"` and returns `status="tier2_declared_unmeasured_partner"` with a valid `api_surface`. A caller could read `api_surface` and use it as if the surface were supported. The disclosure is in the status string and guidance text, but there is no API-level guard (no exception, no `None` api_surface). The operator catalog is correctly labeled as development-not-release, but the planner should be hardened before public exposure.

### LOW (documentation gap; does not affect correctness of claims)

**L-1 — `_validate_payload` in gate script checks `cupy_performance_claim_authorized` indirectly.**
`scripts/v4_catalog_regression_gate.py:100–109` — the validator checks `release_claim_authorized`, `broad_v4_speedup_claim_authorized`, `tier3_callback_claim_authorized`, `whole_app_speedup_claim_authorized`, `app_specific_native_kernel_authorized`, but does not check `cupy_performance_claim_authorized`, `embedding_c_abi_claim_authorized`, or `non_python_host_binding_claim_authorized` in the per-example payload. The outer result hardcodes these `False`, so the gate cannot emit `True` at the result level. However, an example that started emitting `cupy_performance_claim_authorized: true` in its payload would pass per-example validation undetected.

**L-2 — Tier-3 spike documents are correctly bounded; interpretation of the OptiX block is accurate.**
`tier3_optix_module_link_spike.md` correctly identifies "No functions with semantic types found" as requiring a wrapper/direct-callable ABI, not just PTX composition. This is technically sound. No action required, noted as a positive finding.

---

## Answers to the Five Review Questions

**Q1. Is V4.0 correctly scoped to the three measured Torch CUDA Tier-2 surfaces?**

Yes. The three surfaces (`v4_fixed_radius_count_threshold_2d_device_arrays`, `v4_closest_hit_grouped_argmin_3d_device_arrays`, `v4_ray_triangle_any_hit_flags_2d_device_arrays`) are listed consistently in `v4_scope.py:8–12`, the scope gate JSON, the candidate packet, the README, and the GPU catalog gate. CuPy is correctly labeled `declared_unmeasured_partners` in the operator catalog, not omitted. No additional surfaces are being slipped in through aliases or planner routing. The `__all__` export list in `v4.py` is bounded to the three sessions, three claim boundaries, three allocate/prepare pairs, and the planner — nothing else.

**Q2. Does the final GPU catalog gate support the engineering release-candidate status?**

Yes, with the snapshot caveat noted in C-2. The serious-size GPU gate (`copies=32768` / `262144` points for fixed-radius; `32768` rays and triangles for ray/triangle surfaces) shows `correctness_passed: true` for all three Tier-2 examples. The planner examples all returned the expected status codes (`tier2_measured_ready`, `tier3_spike_only_not_v4_0_release_surface`, `rejected_action_shaped_callback_deferred`). The git commit is consistent across both gate files and the local sweep. The gate script itself correctly hardcodes `release_authorized: False` in its output regardless of example results.

**Q3. Are V4.x deferred items fenced clearly enough, especially Tier-3 callbacks and raw OptiX callback APIs?**

Yes — three distinct fence layers exist. First, `V4_X_DEFERRED_CAPABILITIES` in `v4_scope.py:23–31` enumerates eight deferred items including `tier3_numba_ptx_generation_spike_only`, `tier3_numba_bare_ptx_direct_optix_module_link_blocked`, `tier3_wrapper_direct_callable_abi`, and `raw_optix_callback_public_api`. Second, all authorization flags for these items are `False` in code and are validated by `validate_v4_0_scope_gate`. Third, the two spike documents correctly document the exact technical blocker: `optixModuleCreate` requires semantic OptiX entry functions; bare Numba helper PTX does not qualify. The conclusion that a wrapper/direct-callable ABI spike is the required next step is technically accurate.

**Q4. Are user-facing docs/examples coherent and safe for a future release front door?**

Mostly yes. The README, candidate packet, and front door all carry explicit "not a release" labels and non-authorization blocks. Every example file checked in the gate runs and returns correct status codes. The planner is documented in the README with code examples that demonstrate Tier-2 routing, Tier-3 spike classification, and complex-callback rejection. One gap: the README does not state what happens when `partner="cupy"` is passed to `plan_operator_request_v4` — a user who reads only the README and calls `plan.api_surface` on the result of a CuPy plan will get a non-`None` surface string that appears to be a valid route. See M-2.

**Q5. What must change before release authorization can be granted?**

Beyond the packet's own three blockers (external release review, release decision record, review debt closure), the following amendments are required:

1. **(C-1)** Enumerate and link the `v4_review_debt_open` items. The blocking reason must be resolvable.
2. **(C-2)** Establish a reproducible re-run protocol from a clean commit state. The current evidence is a one-time POD snapshot.
3. **(M-1)** Document in user-facing materials that the grouped-argmin surface does not carry a `true_zero_copy_authorized` claim, and why.
4. **(M-2)** Harden the planner's CuPy path: either return `api_surface=None` for an unmeasured partner or raise `ValueError` at the API boundary, so callers cannot accidentally treat an unmeasured plan as a routing confirmation.
5. **(L-1)** Extend `_validate_payload` in the catalog regression gate to check `cupy_performance_claim_authorized`, `embedding_c_abi_claim_authorized`, and `non_python_host_binding_claim_authorized` in per-example payloads.

---

## Non-Authorization Block

This review does **not** authorize any of the following:

- V4 release or any public release announcement
- Broad V4 speedup wording of any kind
- Whole-application speedup wording
- Tier-3 Numba/PTX callback support claims
- Raw OptiX callback public API support claims
- CuPy performance claims (measured or otherwise)
- Embedding/C-ABI claims
- Non-Python host binding claims
- App-specific native engine kernels

This review is an external readiness assessment of the engineering release-candidate packet only. It satisfies the first of the three blocking conditions listed in the packet (`external_release_review_not_obtained`). The remaining two blockers (`release_decision_record_not_obtained`, `v4_review_debt_open`) remain open. Release authorization requires a separate release decision record that addresses all blockers, including the amendments identified above.
