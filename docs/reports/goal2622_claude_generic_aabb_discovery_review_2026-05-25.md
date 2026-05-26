All files read. Here is the review:

---

## Goal2622 Review — Contact-Manifold Generic AABB Discovery

**Verdict: block**

---

### Findings

#### 1. Missing 3-AI consensus file — test suite broken as shipped (BLOCKER)

`tests/goal2622_contact_manifold_generic_aabb_discovery_test.py:99` reads:

```
docs/reports/goal2622_contact_manifold_generic_aabb_discovery_3ai_consensus_2026-05-25.md
```

That file does not exist. Only these three are present:

- `goal2622_contact_manifold_generic_aabb_discovery_2026-05-25.md` ✓
- `goal2622_claude_generic_aabb_discovery_review_2026-05-25.md` ✓
- `goal2622_gemini_generic_aabb_discovery_review_2026-05-25.md` ✓

The test does a plain `.read_text()` on the missing path before any assertions run, so `test_docs_record_goal2622_boundary_and_consensus` will raise `FileNotFoundError` unconditionally. This is a hard shipping defect — the committed test suite cannot pass.

#### 2. Core concern honestly addressed — full-Python all-pairs discovery removed (PASS)

The original Goal2621 concern was that the optimized contact path called Python exact triangle intersection over every query/scene pair before exercising `COLLECT_K_BOUNDED`. Goal2622 introduces `aabb_intersection_pair_rows_2d` (exported at `src/rtdsl/__init__.py:868,1306`) and wires it into `aabb_broadphase_collect_k_payload`. The new optimized path is:

```
AABB_INDEX_QUERY_2D candidate rows → Python exact refinement (candidates only) → COLLECT_K_BOUNDED
```

`test_grid_broadphase_removes_full_python_all_pairs_discovery` enforces that `exact_refinement_checks < all_pairs_count // 8` for a 256-cell grid (256² = 65536 pairs, checking only 256). This is a meaningful regression gate, not a smoke assertion.

#### 3. Engine remains app-agnostic, no collision-specific native logic (PASS)

- `aabb_intersection_pair_rows_2d` emits generic `(query_id, indexed_id)` rows, carrying no collision/contact vocabulary anywhere in the contract, output dict, or `claim_boundary` fields.
- `native_engine_customization=False` is enforced in both `AabbIndex2D.count()` and `aabb_broadphase_witness_rows()`.
- `scope_payload()["engine_boundary"]["native_collision_logic_allowed"]` is `False`, and `test_contact_app_aabb_broadphase_matches_tiny_reference` asserts on it.
- `test_app_uses_generic_aabb_discovery_without_shape_pair_native_collector` does a source-text audit, confirming absence of `collect_shape_pair_candidates_bounded`, `rtdl_embree_collect_shape_pair_candidates_bounded`, and `rtdl_optix_collect_shape_pair_candidates_bounded`.
- Exact triangle-intersection refinement and all contact summaries remain in Python app code (`triangles_intersect`, `app_owned_contact_summaries`).

#### 4. No performance overclaiming (PASS)

Every timing-bearing function carries an explicit `claim_boundary` string: "Local CPU timing is a correctness/overhead smoke only." The goal report correctly attributes the wall-clock improvement to removing full Python all-pairs loops, not RT-core acceleration. OptiX count-only limitation is documented in `AABB_INDEX_2D_CONTRACT["backend_status"]`, in `aabb_intersection_pair_rows_2d` itself (raises on `backend != "cpu"`), and in the primitive catalog. No "speedup" wording appears anywhere in docs or code.

#### 5. Primitive catalog and application catalog accurate (PASS)

`docs/rtdl_primitive_catalog.md:153` correctly records `AABB_INDEX_QUERY_2D` range intersection rows as "Internal generic row path" (not a stable primitive), with the explicit caveat that OptiX is still count-only and exact app refinement remains outside the engine. `docs/application_catalog.md:43` echoes the same boundary.

#### 6. Test coverage otherwise adequate (PASS with note)

Five of six tests are sound:
- Generic API correctness + correct row schema (test 1)
- Tiny-fixture reference match + boundary flags (test 2)
- Grid pruning enforcement (test 3)
- Overflow fails closed end-to-end through `COLLECT_K_BOUNDED` (test 4)
- Source audit for forbidden native symbols (test 5)

Test 6 (doc integrity) is the broken one. Once the consensus file exists, the two asserted strings (`"3-AI Consensus"` and `"no collision-specific native engine logic"`) need to be present in it — verify they are when the file is drafted.

---

### Required Follow-up

| Priority | Action |
|---|---|
| **Block** | Create `docs/reports/goal2622_contact_manifold_generic_aabb_discovery_3ai_consensus_2026-05-25.md` containing at minimum the strings `"3-AI Consensus"` and `"no collision-specific native engine logic"` so `test_docs_record_goal2622_boundary_and_consensus` can pass. |
| Required | Run the full test file after the consensus doc is added to confirm no remaining `FileNotFoundError` or assertion failures. |
| Recommended | Add a check to CI that every `*_3ai_consensus_*.md` file referenced in tests exists at test-collection time, to prevent recurrence. |

---

### Consensus Statement

Goal2622 correctly and honestly removes the app-owned full Python all-pairs discovery from the contact benchmark's optimized path by introducing a generic, collision-vocabulary-free `AABB_INDEX_QUERY_2D` broadphase row primitive. The engine boundary, no-speedup-claim posture, and primitive catalog entries are all accurate. However, the goal cannot be merged as-is: the committed test file references a 3-AI consensus report that does not exist in the repository, causing an unconditional `FileNotFoundError` in the test suite. No other design or correctness issue was found.
