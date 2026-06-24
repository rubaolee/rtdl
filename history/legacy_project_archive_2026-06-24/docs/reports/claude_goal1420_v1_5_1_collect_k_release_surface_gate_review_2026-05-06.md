Having read all eight referenced files, I can now produce the review.

---

## Verdict

**ACCEPT**

The v1.5.1 `COLLECT_K_BOUNDED` release-surface gate and candidate docs are suitable for the measured `documented_experimental_public_candidate` scope. All structural invariants are satisfied; no forbidden overclaims are present.

---

## Accepted Evidence

**Code layer (`src/rtdsl/v1_5_1_collect_k_bounded.py`)**

- `V1_5_1_COLLECT_K_BOUNDED_RELEASE_GATE_REQUIRED_PHRASES` (11 phrases) and `V1_5_1_COLLECT_K_BOUNDED_RELEASE_GATE_FORBIDDEN_PHRASES` (7 phrases) are correctly defined and mechanically scanned across the combined candidate docs in `v1_5_1_collect_k_bounded_release_surface_gate()`.
- All six authorization flags (`public_docs_change_authorized_by_this_gate`, `stable_promotion_authorized_by_this_gate`, `public_speedup_wording_authorized_by_this_gate`, `zero_copy_wording_authorized_by_this_gate`, `whole_app_speedup_claim_authorized_by_this_gate`, `release_tag_action_authorized_by_this_gate`) are set to `False` and each is individually enforced by the validator loop in `validate_v1_5_1_collect_k_bounded_release_surface_gate()`.
- `explicit_release_approval_required = True` is enforced.
- The claim boundary text contains all eight required guard phrases verified by the validator.
- The gate chains through `validate_v1_5_1_collect_k_bounded_release_surface_proposal()` → `validate_v1_5_1_collect_k_bounded_readiness_gate()` → `validate_v1_5_1_collect_k_bounded_contract()`, so every prior layer's invariants are re-checked on every gate call.

**Doc layer (`docs/release_reports/v1_5_1/`)**

All three candidate docs together satisfy the 11 required phrases (distributed: most in `collect_k_bounded.md` and `release_surface_gate.md`, including `"fail-closed"`, `"Embree and OptiX"`, `"Python+RTDL"`, `"PYTHONPATH=src:. python"`, and all five caution markers). No forbidden phrase appears in any of the three docs.

**Test layer (`tests/goal1420_v1_5_1_collect_k_release_surface_gate_test.py`)**

Five test methods cover: gate validation, required-doc filesystem existence, all six authorization flags being `False`, claim boundary phrase membership, and `allowed_next_actions` exact equality. Coverage is complete for the gate's behavioral contract.

**Process layer**

The gate correctly references the accepted 3-AI proposal consensus (`three_ai_goal1419_v1_5_1_collect_k_release_surface_proposal_consensus_2026-05-06.md`), which itself shows Codex (internal), Claude, and Gemini all returning `ACCEPT` with no blockers on the proposal. The gate builds on that accepted prior step without expanding its scope.

**Public-API export (`src/rtdsl/__init__.py`)**

All v1.5.1 gate symbols are exported and listed in `__all__`. No v1.5.1 gate symbol is missing from the public surface.

**Allowed next actions** are appropriately limited to three items: requesting external review, preparing a public-doc link patch *after* review accepts, and requesting an explicit release action *if* the user wants a release. None of the three permitted actions is self-authorizing.

---

## Blockers

None.

---

## Notes

1. **Evidence registry gap (non-blocking).** `V1_5_1_COLLECT_K_BOUNDED_READINESS_EVIDENCE` lists only three of the six required gates (`contract_foundation`, `native_embree_optix_parity`, `same_contract_benchmarks`). The remaining three (`bounds_tests`, `external_3_ai_parity_consensus`, `external_3_ai_benchmark_consensus`) have no evidence file pointer in that tuple. The gate does not fail because `gate_results` is set directly and the validator checks that all six pass via `passed_gates`. This is a documentation gap in the evidence registry but does not affect gate correctness or the authorization surface. A future hardening pass could add the missing evidence file references.

2. **`validate_collect_k_bounded_result` capacity fallback (non-blocking).** At line 642, if a result dict omits both `"capacity"` and `"valid_count"`, `capacity` defaults to `0`, and any non-empty `candidate_id_rows` will then trigger a fail-closed overflow. This is safe (fail-closed is the correct policy) but the silent default could be surprising to a caller. This is not a gate issue; it is a minor hardening opportunity in the reference validator.

3. **This review does not authorize public promotion, speedup wording, zero-copy wording, or release tag action.** The gate status `candidate_docs_ready_pending_explicit_release_action` and the explicit-release-approval-required flag remain the binding boundary.
