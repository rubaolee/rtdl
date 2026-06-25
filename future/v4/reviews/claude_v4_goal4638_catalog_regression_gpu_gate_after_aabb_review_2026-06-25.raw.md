Now I have all the material. Let me do the analysis.

---

## Review: V4 Goal4638 Catalog Regression GPU Gate After AABB

**Verdict: `approve_goal4638_catalog_regression_gpu_gate`**

---

### Q1 — Is the gate a meaningful release-hardening gate, or too weak?

The gate is appropriately scoped and not too weak for what it claims to be. It explicitly defines itself as a front-door runnable health check and correctly does not claim to be an all-application benchmark or release gate. Six of the 11 examples run with `correctness_passed=True` enforced (`scripts/v4_catalog_regression_gate.py:192`). The `--backend optix` flag is correctly appended for the AABB example in GPU mode (`v4_catalog_regression_gate.py:163-167`), so the new surface is exercised on the actual RT hardware.

One structural note: the AABB fixture in `aabb_index_all_ops_count.py` is very small (2 boxes, 2 point queries, 2 box queries). This is fine for a regression gate — the purpose is runability and correctness, not stress — but readers should not infer performance characterization from it.

---

### Q2 — Does the gate correctly include 11 examples including AABB and quickstart/planner paths?

Yes, count is correct. The 11 examples in `_example_commands` are:

| # | Name | Role |
|---|------|------|
| 1 | `fixed_radius` | measured |
| 2 | `closest_hit_grouped_argmin` | measured |
| 3 | `ray_triangle_any_hit_flags` | measured |
| 4 | `primitive_grouped_i64_reduction` | measured |
| 5 | `point_group_nearest_witness` | measured |
| 6 | `ray_triangle_any_hit_weighted_sum` | measured |
| 7 | `aabb_index_all_ops_count` | measured (new) |
| 8 | `v4_frontdoor_quickstart` | ok |
| 9 | `operator_callback_planning_tier2` | tier2_measured_ready |
| 10 | `operator_callback_planning_scalar_callback` | tier3_spike_only_not_v4_0_release_surface |
| 11 | `operator_callback_planning_complex_callback` | rejected_action_shaped_callback_deferred |

The evidence JSON confirms all 11 ran, all `"passed": true`, zero `failures`. The test in `v4_catalog_regression_gate_test.py:55` explicitly asserts `len(payload["examples"]) == 11`. The quickstart result shows 8 measured surfaces and `aabb_plan_status: "tier2_measured_ready"`, which is internally consistent with the surface count.

---

### Q3 — Is it acceptable that this gate confirms catalog/front-door health but does not count as an all-application benchmark or release gate?

Yes. The scope limitation is stated clearly and repeatedly in the gate document, the evidence MD, and the decision module's non-authorization section. The status is `goal4638_catalog_regression_gpu_after_aabb_passed_not_release` — the "not_release" is in the status token itself. The gate document explicitly says: "It is release-hardening evidence, not release authorization and not an all-application benchmark." Nothing in the evidence or code contradicts this.

---

### Q4 — Are claim boundaries enforced for nested example payloads, including `all_benchmark_speedup_claim_authorized`?

Yes, the enforcement is correct and recursive. `FORBIDDEN_CLAIM_FLAGS` at `v4_catalog_regression_gate.py:14-26` includes `all_benchmark_speedup_claim_authorized`. The `_forbidden_claim_true_paths` function at lines 58-69 recurses into all nested dicts and lists, not just the top level. The test `test_gate_rejects_forbidden_claim_flags_even_when_nested` (`v4_catalog_regression_gate_test.py:128`) validates this behavior explicitly — it plants `cupy_performance_claim_authorized: True` in `payload.metadata.nested` and confirms the gate catches it.

For the AABB evidence payload specifically: `all_benchmark_speedup_claim_authorized: false` appears at the top level and the payload has no deep nesting with live claim flags. The AABB example lacks the `metadata` subdict present in other examples — meaning less structural depth to audit, but also fewer claim leaks possible.

One flag worth noting: the AABB example carries `all_benchmark_speedup_claim_authorized` at the top level, which is appropriate since AABB produces counts across 3 op types and could be mistaken for a benchmark surface. Its explicit `false` value here is correct.

---

### Q5 — Is the release-decision update correct: G8 passes, final release still false, review debt visible?

Yes, all three conditions are met and verified by tests.

- **G8 passes**: `v4_release_decision.py:129-135` sets `G8_catalog_regression_gpu_after_aabb` with `passed_for_release=True`. `v4_goal4632_release_decision_test.py:51` asserts this.
- **Final release false**: `release_authorized=False` and `release_candidate_authorized=False` are hardcoded in both `v4_release_decision.py:161-162` and `v4_goal4638_catalog_regression_decision.py:29-30`. G9 (`G9_final_release_decision`) is `passed_for_release=False`. The test at line 53 verifies G9 is False.
- **Review debt visible**: `external_review_debt_remains_for_goal4638_catalog_regression_completion` is in `release_blockers` at `v4_release_decision.py:151`. The test at line 82 asserts this blocker is present and cannot be absent.

The `passed_for_release=True` on G8 means "this gate did not independently block release," not "this gate authorizes release" — that semantic is reinforced by G9's False and the overall `release_authorized=False`. The naming is slightly ambiguous but the behavior is correct and the tests nail it down.

---

### Additional Observations

**Non-issues:**
- Dry-run mode uses cpu backend for AABB (no `--backend optix`). This is correct; dry-run exists for CI without GPU. The GPU run is what matters and does pass `--backend optix`.
- `--include-candidates` is a no-op (`if include_candidates: pass`) because there are 0 current candidates. The test confirms 11 examples remain. This is intentional, not a bug.
- `v4_goal4638_catalog_regression_decision.py` hardcodes the evidence file paths and example count rather than re-reading the JSON. This is a static snapshot pattern consistent with how other goal decisions are structured in this codebase.

**Correctly held boundaries:**
- The `operator_callback_planning_scalar_callback` case is `tier3_spike_only_not_v4_0_release_surface` with `tier3_spike_authorized=True` and no `api_surface`. This is correct — it documents the Tier-3 path without promoting it.
- The `operator_callback_planning_complex_callback` case is `rejected_action_shaped_callback_deferred` with no `api_surface`. This is correct.
- The `weighted_sum_example_status` field in `v4_goal4638_catalog_regression_decision.py:28` records `"measured"` which matches the evidence payload's `surface_status: "tier2_measured_pod_validated_not_release"`. These are consistent.
