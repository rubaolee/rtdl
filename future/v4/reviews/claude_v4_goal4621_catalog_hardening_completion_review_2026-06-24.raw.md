**`accept_goal4621_complete_not_release`**

---

## Findings

### Verified correct

**1. Catalog rows — all 17 fields present on all 6 rows**
`measured_v4_tier2_operator_catalog()` and `candidate_v4_tier2_operator_catalog()` both populate the full field set claimed in the packet. `test_catalog_rows_have_goal4621_hardened_status_fields` exhaustively asserts all 17 required fields on all 6 rows and confirms every authorization flag is `False`. `catalog_class` cleanly partitions `"measured"` (5) vs `"candidate"` (1).

**2. Candidate row status fields are consistent**
`surface_status: "tier2_candidate_goal4620_not_measured"` and `partner_claim_status: "candidate_goal4620_gate_passed_not_measured"` are present and correctly distinguish this surface from the measured 5. The candidate row correctly sets `direct_device_output_columns: False` and `direct_device_output_scalar: True`.

**3. Front door is explicit**
`claim_boundary_v4()` in `v4.py` exposes exactly 5 measured surfaces + 1 candidate tuple, with all 10 authorization flags hard-coded `False`. `V4OperatorPlan` defaults all authorization fields to `False`. Both are verified by `test_claim_boundary_lists_measured_surfaces_without_release_claims` and `test_quickstart_runs_without_cuda`.

**4. True-zero sanitizer — correct placement and logic**
`_clear_public_true_zero_copy_authorizations()` is applied in all 6 session `run()` paths:
- `v4_fixed_radius.py:148`
- `v4_point_group.py:198`
- `v4_ray_triangle.py:389, 507, 580, 685`

The `_FakeAnyHitScene` in the test deliberately returns several `true_zero_copy_authorized: True` fields (including nested `ray_columns_true_zero_copy_authorized`, `output_flags_true_zero_copy_authorized`, `triangle_scene_true_zero_copy_authorized`), and `test_any_hit_session_run_uses_device_flags_hot_path` asserts `metadata["true_zero_copy_authorized"]` is `False` while `metadata["native_direct_device_output_columns"]` remains `True`. The distinction between direct-device facts and authorization claims is correctly enforced.

**5. Gate recursive rejection**
`FORBIDDEN_CLAIM_FLAGS` now includes `"true_zero_copy_authorized"` and `"raw_optix_callback_claim_authorized"`. `_forbidden_claim_true_paths()` traverses nested dicts and lists recursively. Combined with `_validate_payload()` checking `release_claim_authorized` and `tier3_callback_claim_authorized` explicitly, the gate has no partial-check gaps.

**6. Docs are clean current-state**
README: states 5 measured / 1 candidate, `release authorization: false`, "not a release announcement", no "Current candidate packet" or stale RC wording. `test_readme_points_users_at_unified_frontdoor` asserts absence of both stale phrases and presence of "candidate POD\ngate and completion consensus are closed" language. `tier2_operator_catalog.md` correctly distinguishes measured from candidate tables and carries a Non-Authorization section.

**7. POD evidence**
10/10 examples pass at `--copies 32768 --ray-count 32768 --include-candidates`. Gate header confirms `release_authorized: False`.

---

### Non-blocking observations (not amendment-requiring)

**O1. Sanitizer helper is defined three times.** `_clear_public_true_zero_copy_authorizations` is copy-pasted into `v4_fixed_radius.py`, `v4_point_group.py`, and `v4_ray_triangle.py`. No correctness issue — all three copies are identical and correctly wired — but it is a future maintenance surface. Not a `goal4621` scope item.

**O2. Candidate row has a redundant `"status"` key.** `candidate_v4_tier2_operator_catalog()` inserts both `"surface_status"` (line 376) and `"status"` (line 383) from the same source field. Both are `"tier2_candidate_goal4620_not_measured"`. Harmless redundancy; test assertions cover only `surface_status`. Not a blocking issue.

---

### Scope check

No new operators, no new native workloads, no performance claims, no release language, no CuPy performance path, no Tier-3 callback surface, no C ABI work. Implementation is strictly catalog/front-door metadata hardening and gate extension as scoped.

---

**This packet may proceed to 3-AI consensus or explicit review debt to close `goal4621`.**
