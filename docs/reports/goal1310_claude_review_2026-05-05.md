# Goal1310 Claude Review: v1.5 Jaccard `COLLECT_K_BOUNDED`

Date: 2026-05-05
Reviewer: Claude (claude-sonnet-4-6)

---

## Verdict

**Pass — all five review criteria are met.**

`COLLECT_K_BOUNDED` is correctly held at `experimental_diagnostic_only`. The policy fails closed on overflow, rejects silent truncation, blocks score reduction unless complete coverage is proven, blocks public speedup wording, and the inventory accurately records the boundary between what is defined and what remains unimplemented.

---

## Findings

### 1. COLLECT_K_BOUNDED kept experimental/diagnostic

Confirmed. The contract in `bounded_collection_contracts.py:17` sets `"status": "experimental_diagnostic_only"` and the validator at line 80–81 raises if the status is anything else. `primitive_contract_schema.py:89–90` independently enforces the same constraint on the embedded `bounded_collection_policy` inside the Jaccard contract. The migration inventory entry at `v1_5_migration_inventory.py:173` carries `"status": "diagnostic_blocked"`. No path through any validator or schema check permits promotion to a stable v1.5 primitive.

### 2. Fail-closed on overflow; silent truncation rejected

Confirmed. Three independent enforcement layers are active:

- `bounded_collection_contracts.py` declares `"overflow_policy": "no_silent_truncation"`, `"failure_mode": "fail_closed_overflow"`, and `"truncation_allowed": False`, and the `validate_v1_5_collect_k_bounded_contracts()` function checks each explicitly (lines 84–87).
- `primitive_contract_schema.py:92–96` re-checks all three fields on the embedded `bounded_collection_policy` whenever `app_row == "polygon_set_jaccard"`.
- `V1_5_BOUNDED_COLLECTION_FAILURE_MODES = ("fail_closed_overflow",)` at `bounded_collection_contracts.py:7` means no alternative failure mode can pass validation.

The enforcement is correct and defense-in-depth.

### 3. Score reduction blocked without complete coverage

Confirmed. `bounded_collection_contracts.py:28–29` sets `"complete_candidate_coverage_required": True` and `"score_reduction_allowed_on_overflow": False`. Both are validated at lines 88–91. `primitive_contract_schema.py:97–100` independently enforces both flags on the embedded policy in the Jaccard contract. No test or code path emits a Jaccard score after an overflow condition.

### 4. Public speedup wording blocked

Confirmed and enforced at four separate sites:

- `bounded_collection_contracts.py:8`: module-level constant `V1_5_BOUNDED_COLLECTION_PUBLIC_WORDING_ALLOWED = False`, referenced by each contract and validated at line 92–93.
- `polygon_primitives.py:126`: `"public_wording_allowed": False` hardcoded in `polygon_jaccard_diagnostic_contract`.
- `primitive_contract_schema.py:79–80`: schema rejects any Jaccard contract where `public_wording_allowed is not False`.
- `v1_5_migration_inventory.py:183,229–230`: inventory entry has `"public_wording_authorized": False`, and the inventory validator rejects any row that sets this to `True`.

### 5. Inventory accurately reflects defined-but-unfinished state

Confirmed. The `polygon_set_jaccard/chunked_candidate_scoring` inventory row at `v1_5_migration_inventory.py:170–184` records:

- `"status": "diagnostic_blocked"` — policy is defined, but the primitive is not promoted.
- `"remaining_app_specific_work"` lists exactly the three outstanding items: native fail-closed bounded collection implementation, score reduction after complete candidate coverage, and `optix_still_slower_with_reason`.
- The boundary string explicitly says "no silent truncation and no public wording promotion."

The policy report at `docs/reports/goal1310_v1_5_jaccard_collect_k_bounded_policy_2026-05-05.md` confirms the same three work items as "not done."

---

## Risks

### R1 — Fail-closed is policy-declared, not yet runtime-enforced

The most significant residual risk. All fail-closed guarantees currently live in Python contract metadata and validators. There is no native C++/CUDA implementation that actually catches a bounded-collection overflow and halts score reduction at runtime. The `remaining_app_specific_work` field records this gap correctly, but until native enforcement exists, a production deployment could silently emit a wrong score if the collection layer overflows without raising a Python-visible error. The diagnostic-only status mitigates this for now, but the gap should be closed before any promotion discussion.

### R2 — `REDUCE_FLOAT(SUM)` tolerance contract is still deferred

`polygon_primitives.py:101` records `"future_score_primitive_status": "deferred_until_generic_float_reduction_contract"`. Score parity between Embree and OptiX cannot be validated without a tolerance and result-shape contract for `REDUCE_FLOAT(SUM)`. This is a required promotion gate and is currently open.

### R3 — OptiX-slower-than-Embree explanation remains outstanding

The inventory lists `"optix_still_slower_with_reason"` as a remaining work item and the Jaccard diagnostic contract status is set to `"optix_still_slower_with_reason"`. An explanation for why OptiX is slower than Embree in this path has not been documented. Public wording is correctly blocked on this, but the absence of a recorded reason is also a documentation risk: if the performance relationship changes, there is no baseline rationale to compare against.

### R4 — `bounded_collection_policy` validation is Jaccard-scoped only

`primitive_contract_schema.py:76` gates the `bounded_collection_policy` checks on `app_row == "polygon_set_jaccard"`. If `COLLECT_K_BOUNDED` is ever referenced in a contract for a different `app_row`, the schema will not check the embedded policy fields. This is not a current defect (only one contract uses `COLLECT_K_BOUNDED`), but it is an architectural gap to be aware of if the primitive is extended.

---

## Required Fixes

None are required to pass this review. The five stated criteria are all correctly implemented. The following items are tracked open work, not defects introduced by Goal1310:

| Item | Owner | Status |
|---|---|---|
| Native fail-closed bounded collection implementation (C++/CUDA) | Goal1310 follow-on | Not started |
| `REDUCE_FLOAT(SUM)` tolerance and result-shape contract | Goal1310 follow-on | Not started |
| Document OptiX-slower-than-Embree reason | Goal1310 follow-on | Not started |

---

## Conclusion

Goal1310 correctly defines the `COLLECT_K_BOUNDED` overflow policy without promoting `polygon_set_jaccard` to a stable v1.5 primitive. The Python-layer contracts and validators enforce all five review criteria: experimental status, fail-closed overflow, no silent truncation, blocked score reduction on overflow, and blocked public wording. The inventory is an accurate snapshot: policy is defined, runtime enforcement is not yet implemented.

The open residual risk is R1 — fail-closed behavior exists only in metadata today. This is accurately recorded as unfinished work and is the correct blocker for any future promotion. No source code changes are required as a result of this review.
