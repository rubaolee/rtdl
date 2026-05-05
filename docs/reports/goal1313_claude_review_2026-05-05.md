# Goal1313 Claude Review: Native Jaccard Device-Level Plan

Date: 2026-05-05

Reviewer: Claude (claude-sonnet-4-6)

---

## Verdict

**Approved with required fixes.** The plan is structurally sound and correctly scoped. The diagnostic status is enforced throughout the stack, the ABIs are genuinely generic, and the fail-closed Python layer is working and pod-validated. Three issues require fixes before the OptiX native slice begins: a silent-zero gap in the Jaccard scoring fallback, an ABI naming asymmetry, and an unresolved Embree native-wrapper decision that must not be deferred past native OptiX implementation.

---

## Findings

### 1. Diagnostic status and speedup claim boundary — PASS

`polygon_set_jaccard` is correctly held at `diagnostic_blocked` throughout all layers:

- `bounded_collection_contracts.py` enforces `V1_5_BOUNDED_COLLECTION_PUBLIC_WORDING_ALLOWED = False` and raises `ValueError` if `status != "experimental_diagnostic_only"` or `public_wording_allowed is not False`.
- `v1_5_migration_inventory.py` sets `public_wording_authorized: False` for the Jaccard entry and raises if any inventory row authorizes public wording.
- `jaccard_performance_diagnostics.py:82` enforces that the `claim_boundary` field must contain "no positive Jaccard speedup wording" or validation raises.
- The plan's promotion gate requires a separate 3-AI public wording review before exit from `diagnostic_blocked`. That gate is not auto-passable by any code change.

The `run_generic_polygon_set_jaccard_summary` `claim_boundary` string and the Goal1312 diagnostic both use identical language ("not public speedup wording"). The claim boundary is consistent end-to-end.

No overclaim present. No path in the current code can unblock public wording unilaterally.

### 2. Native ABI genericity — PASS with naming note

Both proposed ABIs operate on polygon-pair geometry, not on Jaccard specifically:

- `rtdl_optix_collect_polygon_pair_candidates_bounded` — candidate collection for any polygon-pair use case.
- `rtdl_native_reduce_polygon_pair_exact_area_summary` — area summary reduction for any candidate set.

The plan explicitly lists `rtdl_optix_run_polygon_set_jaccard_fast` as a non-goal and states "The ABI name is polygon-pair candidate collection, not Jaccard." Jaccard computes only the final ratio from the generic area summary plus set areas. This is an acceptable generic split.

One naming inconsistency: the collection ABI is prefixed `rtdl_optix_*` (backend-specific) while the reduction ABI is prefixed `rtdl_native_*` (backend-neutral). If Embree later receives a symmetric collection ABI, the two prefixes will produce a visually asymmetric pair (`rtdl_optix_collect_*` / `rtdl_embree_collect_*`) even though the reduction contract spans both backends. This should be addressed in the ABI naming decision before the OptiX slice ships; see Required Fixes.

### 3. Fail-closed bounded collection and guarded reduction gates — PASS with one gap

The Python/generic layer is correctly fail-closed:

- `collect_k_bounded_candidate_pairs` (`generic_polygon_primitives.py:70`) raises `RuntimeError` before returning pairs on overflow (`emitted > capacity`), and sets `candidate_pairs: ()` in the overflow metadata. Score reduction never receives the pair set.
- `run_generic_polygon_set_jaccard_summary` calls `collect_k_bounded_candidate_pairs` before `exact_score_fn`. If overflow raises, the score function is never reached. This is correct sequencing.
- Pod validation (Goal1311, capacity 1 test) confirmed exit code 1 and the correct `fail_closed_overflow` error message.
- `bounded_collection_contracts.py:86–92` enforces `truncation_allowed is False`, `complete_candidate_coverage_required is True`, `score_reduction_allowed_on_overflow is False` as hard contract invariants.

One gap: `run_generic_polygon_set_jaccard_summary:127–134` falls back to a zero-intersection summary when `rows` is empty (i.e., `exact_score_fn` returns no rows). This fallback is correct when `candidate_pairs` is genuinely empty (no overlapping polygon pairs), but it is also silently triggered if `exact_score_fn` returns an empty tuple when `collection["candidate_pairs"]` is non-empty. In that case the function returns a zero Jaccard similarity without error, which is a silent correctness gap. See Required Fixes.

The promotion gate table is complete and correctly sequenced. It cannot be satisfied by partial evidence.

### 4. Vulkan, HIPRT, Apple RT frozen before v2.1 — PASS

The freeze is code-enforced at two independent layers:

- `generic_polygon_primitives.py:18`: `_validate_backend` raises `ValueError` with message `"{backend} polygon generic primitive is frozen before v2.1"` for any backend in `FROZEN_BEFORE_V2_1_POLYGON_BACKENDS = ("vulkan", "hiprt", "apple_rt")`.
- `v1_5_migration_inventory.py:205`: `validate_v1_5_generic_migration_inventory` checks backend scope against `ACTIVE_V1_5_BACKENDS` only; any frozen backend in a row would raise.

The plan's non-goals re-state this. The code cannot call a frozen backend without raising. No Vulkan, HIPRT, or Apple RT code is referenced in any of the reviewed artifacts.

### 5. Next slice priority: OptiX native bounded collection — AGREE

The recommended next slice (OptiX native bounded collection first) is correct given the evidence:

- Goal1312 shows candidate discovery is the dominant pipeline slowdown at 11.2x vs Embree. Native exact continuation is 1.8x slower. Addressing native device-level bounded collection in OptiX directly targets the dominant phase.
- The Python wrapper is already pod-verified on both Embree and OptiX, so Embree provides a stable correctness baseline during OptiX native development.
- The promotion gate requires native bounded collection for both Embree and OptiX before Jaccard can exit `diagnostic_blocked`. OptiX is the critical path because it is the NVIDIA RT priority and has the larger performance gap. Embree native work can follow in parallel or immediately after, but OptiX native collection is the gating item.

The plan correctly defers native reduction to after native collection is complete and pod-validated.

---

## Risks

**Risk 1 — Silent zero on non-empty candidate set (medium)**
`run_generic_polygon_set_jaccard_summary:127–134` returns `jaccard_similarity: 0.0` silently if `exact_score_fn` returns no rows even when `candidate_pairs` is non-empty. This could mask a scoring regression as a zero similarity result instead of a failure. The risk is medium because pod diagnostics would likely catch it, but the code path itself is not guarded.

**Risk 2 — Embree native bounded wrapper decision is unresolved (medium)**
The plan states "either add an Embree native bounded wrapper or prove the current Embree candidate collection can publish identical fail-closed metadata." This decision has been deferred to after OptiX native implementation. If it is resolved wrongly (e.g., Embree is left on the Python wrapper while OptiX gets a native wrapper), the "Same-contract evidence" gate in the promotion table cannot be satisfied. The decision must be made before, not during, the OptiX native slice.

**Risk 3 — ABI prefix asymmetry locks backend naming (low)**
The `rtdl_optix_collect_*` / `rtdl_native_reduce_*` naming asymmetry will be visible in any multi-backend integration. If Embree gets `rtdl_embree_collect_*`, the naming set becomes inconsistent with the reduction layer. A backend-neutral `rtdl_native_collect_*` prefix for both ABIs would be cleaner. This is low risk now but creates technical debt before v2.0 if not resolved.

**Risk 4 — OptiX candidate count differs from Embree (low, documented)**
Goal1311 and Goal1312 show OptiX emits 256 candidates vs Embree's 384. Both produce the same exact Jaccard score, which means OptiX's smaller candidate set is still a complete positive-candidate superset. This is expected behavior and documented. The risk is that a future regression where OptiX silently drops candidates below the correct superset would still produce the same final score if the missing candidates are non-overlapping. The native bounded collection implementation must preserve the "complete positive-candidate superset" guarantee explicitly.

---

## Required Fixes

**Fix 1 — Guard `exact_score_fn` empty-rows case (required before merge)**

In `generic_polygon_primitives.py:122–134`, add an assertion or raise before the zero fallback when `candidate_pairs` is non-empty:

```python
rows = tuple(exact_score_fn(left, right, frozenset(collection["candidate_pairs"])))
if not rows and collection["candidate_pairs"]:
    raise RuntimeError(
        "exact_score_fn returned no rows for non-empty candidate_pairs; "
        "cannot produce Jaccard summary"
    )
summary = (
    dict(rows[0])
    if rows
    else {
        "intersection_area": 0,
        "left_area": 0,
        "right_area": 0,
        "union_area": 0,
        "jaccard_similarity": 0.0,
    }
)
```

This closes the silent-zero gap without changing behavior for the legitimate empty-candidate-set case.

**Fix 2 — Resolve the Embree native bounded wrapper decision before OptiX native slice (required before slice planning)**

Before implementing `rtdl_optix_collect_polygon_pair_candidates_bounded`, document whether Embree will:

(a) Receive a symmetric `rtdl_embree_collect_polygon_pair_candidates_bounded` wrapper that publishes the same fail-closed metadata, or  
(b) Be demonstrated to already publish equivalent fail-closed metadata through its existing candidate collection path.

This decision gates the "Same-contract evidence" promotion requirement. Deferring it risks reaching the end of the OptiX slice without a clear Embree counterpart, which would block promotion regardless of OptiX correctness.

**Fix 3 — Align collection ABI prefix with reduction ABI (required before native ABI is finalized)**

Either rename the collection ABI to `rtdl_native_collect_polygon_pair_candidates_bounded` (dropping the `optix` prefix, consistent with `rtdl_native_reduce_polygon_pair_exact_area_summary`), or add explicit documentation justifying why the collection ABI is backend-keyed while the reduction ABI is backend-neutral. The current asymmetry is not explained in the plan.

---

## Conclusion

The plan is well-constructed and its constraints are correctly enforced in code. The diagnostic boundary, generic ABI naming, fail-closed collection, and backend freeze are all sound. The three required fixes address a silent-zero correctness gap (Fix 1), an unresolved pre-slice decision that could block promotion (Fix 2), and a naming inconsistency that will compound if not addressed before the ABI is finalized (Fix 3). After those fixes, the OptiX native bounded collection slice is the correct next priority and should proceed.
