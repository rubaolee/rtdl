Now I have full context across all four documents. Here is the review.

---

## Review: Phoenix V3 AABB Prepare-Reuse Contract Packet

### Q1 — M7 Promotion Avoidance

**Clear and consistent.** The `.md` header block, the JSON `m7_qualified_release_rows_added: 0`, and the work-queue `active candidate status: aabb_prepare_reuse_contract_candidate_not_m7` are all aligned. The "Forbidden Shortcuts" section explicitly blocks `contact_manifold` promotion. The `failed_checks: []` array is verifiable against the checks dict: every check (`contact_boundary_not_m7`, `contact_wall_is_slower`, `prepare_cost_blocker_present`, etc.) is consistent with the stated gap ratios. **Pass.**

---

### Q2 — Genericity of Prepared-Session Metadata

**Substantially generic, with one observation.**

The metadata uses `aabb_index_query_2d` as the primitive name, `prepare_aabb_index_2d` / `emit_aabb_intersection_pair_rows_2d` as phase names, and generic cache-key field names (`indexed_aabbs`, `query_aabbs`, `operation`, `resolution`, `row_capacity`, `row_contract`). None of these are contact vocabulary. `app_specific_native_engine_logic_allowed: false` is enforced in both the JSON policy and the Python code path.

**Observation (P2):** The Python function `describe_aabb_broadphase_prepared_session_residency` accepts a `CollisionWitnessFixture` as its input type. The function itself uses only `len(fixture.scene_triangles)` and `len(fixture.query_triangles)` — shape counts, no contact vocabulary. But the signature leaks the contact type. This does not affect the emitted metadata's genericity, but if this function is ever lifted into a shared utility, the coupling is unnecessary. **Not a blocker for this packet.**

---

### Q3 — Forbidden Claim Avoidance

**All forbidden claim categories are blocked.** Verified:

| Claim category | Guard present? |
|---|---|
| Broad V3-over-V2 AABB/contact speedup | `broad_v3_faster_than_v2_claim_authorized: false` |
| Full contact solver / physics throughput | Forbidden shortcut + `engine_boundary.native_collision_logic_allowed: false` |
| Paper or authors-code comparison | Not present in any file |
| Automatic partner selection | `automatic_partner_selection_authorized: false` in policy + Python |
| Device-buffer interop / true zero-copy | `true_zero_copy_claim_authorized: false` in policy + Python |
| 1.235x query ratio as wall speedup | Explicitly named in forbidden shortcuts |

One marginal item: `rt_core_accelerated: normalized_discovery_backend == "optix"` appears in the broadphase dict at `aabb_broadphase_witness_rows()` line 402. This is a factual boolean, not a speedup wording, and it is counteracted by `broad_rt_core_claim_authorized: false` in the policy. It is not a P0, but see P2 list below.

---

### Q4 — POD Evidence Specificity

**Adequately specific for actionability, with one gap.**

The six Future M7 requirements name the exact primitive (`aabb_index_query_2d`), the exact pattern (prepare-once, explicit session, repeated query), the exact metric table (prepare/query/collect/wall phases plus cold-plus-repeat wall), the correctness oracle (CPU-reference parity), and the review gate (2-AI + Codex consensus). The work queue echoes this with the same wording.

**P1 gap — minimum scale not specified.** The existing M7 count-only row is at scale 32768. The Future M7 requirements do not state a floor scene count or fixture type. A POD run over the `tiny` fixture (3 scene triangles) would technically satisfy every written requirement but would be a trivial, unrepresentative result. The requirement should anchor to at least the existing M7 scale or state that the fixture must be at a scale where the prepare phase materially dominates a single cold query.

**P2 gap — "material" wall win is undefined.** The requirement says "Show material OptiX wall win after prepare reuse." The work queue doc states "A 1.01x-style result cannot qualify." This principle is not carried forward into the Future M7 requirements language. Adding a minimum threshold (e.g., "≥ 1.1x after repeated-session amortization, above measurement noise floor") would make the gate unambiguous.

---

### Q5 — Blockers and Improvements

**P0 Blockers (must fix before treating as valid queue advancement):**

None. All claim boundaries hold, M7 count is defended at 0, all JSON checks are self-consistent, the three documents are mutually consistent.

---

**P1 Improvements (should fix before this packet is cited in a POD run):**

1. **Scale floor missing from Future M7 requirements.** Add a minimum fixture scale or explicitly tie it to the existing M7 row's 32768 scene-count floor. Without this, a tiny-fixture POD could pass the written gate.

2. **`query_reuse_observed_within_payload: false` by default.** The Python function always emits the metadata, but the actual `rt.prepare_aabb_index_2d()` code path is only exercised when `discovery_backend` is Embree/OptiX *and* `warmup_count > 0` or `repeat_count > 1`. Under all other conditions the `else` branch runs `rt.aabb_intersection_pair_rows_2d()` — no prepare call. The packet's claim is "contract visibility, not performance promotion," which is honest. But the `.md` should explicitly state that the metadata describes the *contract for* prepare-reuse, not an observed execution of it in the current packet. Without this clarification, a future reviewer may treat the metadata as evidence the prepare path ran.

---

**P2 Improvements (clean-up, no impact on validity):**

3. **Cache-key duplication in JSON.** The `cache_key` structure appears identically under both `prepared_session_residency.cache_key` and `prepared_session_residency.policy.cache_key`. This is redundant in the current snapshot but will silently diverge if one copy is updated. The top-level `cache_key` under `prepared_session_residency` should reference the policy's copy or be removed.

4. **`rt_core_accelerated` field naming.** In `aabb_broadphase_witness_rows()` the field `"rt_core_accelerated": normalized_discovery_backend == "optix"` appears in the broadphase dict. The name implies an active acceleration claim. Consider `"backend_uses_rt_pipeline"` or gating the field behind the `broad_rt_core_claim_authorized: false` guard explicitly.

5. **`contract_version` absent from `.md`.** The version `rtdl.v2_10.prepared_session_residency.goal3873.v1` is the canonical identifier for this contract generation but appears only in the JSON. It should appear in the `.md`'s "Runtime Contract Smoke" section so human reviewers can cross-reference the version without parsing JSON.

6. **`promoted_performance_path=True` for Embree/OptiX in `aabb_broadphase_collect_k_payload()` line 730.** The field name could be read as "performance promotion is authorized" in this path. Verify the downstream `v2_4_phase_timing_metadata` uses this field only to describe the backend tier, not to authorize speedup wording.

---

## Verdict

**`approve_with_amendments`**

The packet is a valid non-M7 Phoenix queue advancement. The M7 boundary is defended, all forbidden claims are blocked, the next-step evidence requirements are specific enough to generate a concrete POD run, and the three documents are internally consistent. No P0 blockers exist.

The two P1 items — the scale floor gap in Future M7 requirements, and the missing prose clarification that the prepared-session metadata describes the contract rather than an observed execution — should be patched before this packet is cited as evidence in a future POD attempt. The P2 items can be addressed in the same patch.
