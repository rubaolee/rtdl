I have now read every controlling artifact, all Goal4639 source/test/evidence files, and the updated release decision. Here is the review.

---

# Goal4639 Scorecard Review Record

**Verdict: `approve_goal4639_scorecard_pass_continue_goal4640`**

---

## Q1 — Did Goal4639 run the frozen Goal4638 scorecard, not a weaker or post-hoc one?

**Yes, unambiguously.**

`evaluate_v4_goal4639_scorecard` calls `validate_v4_goal4638_formal_scorecard_freeze()` as its first act. That validator enforces: exactly 10 unique benchmark families, exactly 8 measured surfaces, exactly 0 candidate surfaces, one floor entry per surface with no placeholder numerics, `requires_external_review_before_goal4639: True`, and all authorization flags false. If the freeze had drifted, the evaluator would raise before scoring anything.

The benchmark families, surface list, and family-to-surface mapping in the evaluator are drawn from `V4_GOAL4638_STRONG_FAMILIES`, `V4_GOAL4638_PARTIAL_CONTROL_FAMILIES`, and `V4_GOAL4638_DEFERRED_EXCLUDED_FAMILIES`. No family was reclassified post-run.

The `summary.json` carries `"freeze_decision": "freeze_v4_release_scorecard_before_goal4639_pod_run"` — the exact decision token from the frozen module. The run.log shows all 11 sub-commands executed with `rc=0` and real elapsed times; `--skip-run` was not used.

---

## Q2 — Are surface/family pass results consistent with the frozen floor table?

All 8 floors verified against evidence:

| Surface | Floor condition | Evidence values | Verdict |
|---|---|---|---|
| fixed_radius_count_threshold | ≥2 sizes with gap ≤100.0 and reduction ≥10.0 | 3 sizes, max_gap=0.589, min_reduction=767.7 | ✓ |
| closest_hit_grouped_argmin | ≥1.0x at all 3 ray counts, correctness pass | min=1.257x, 3 rows, correctness=true | ✓ |
| any_hit_flags | reference ≥1.0x at 8192 row count, no host materialization | ratio=5.671x, hot_path_ok=true | ✓ |
| primitive_grouped_i64_reduction | all 6 rows parity pass and ratio ≥1.0x | min=1.384x, 6 rows, parity=true | ✓ |
| point_group_nearest_witness | parity and ratio ≥1.0x at both sizes | min=389.7x, 4 rows, parity=true | ✓ |
| any_hit_weighted_sum | each shape ≥1.20x and 4-shape geomean ≥1.50x | min=1.482x, geomean=1.780x, parity=true | ✓ |
| fixed_radius_graph_component_union | embree_hot ≥1.20x, embree_wall ≥1.20x, legacy_wall ≥0.98x, signatures match | 1.439x / 1.603x / 1.203x, sigs=match | ✓ |
| aabb_index_all_ops_count | cross-backend count parity, contract family, median ≥10.0x, total ≥10.0x | median=311.4x, total=164.7x, parity=true | ✓ |

Family mapping is identical to the freeze table. The representative ratios in the JSON are consistent with the evaluator's extraction logic (e.g., fixed_radius representative = 1/max_gap = 1/0.589 ≈ 1.697x ✓).

The strong-family geomean of 5.18x is computed from the 4 family-level geomeans (`rt_dbscan≈1.43`, `raydb_style≈2.14`, `triangle_counting≈1.43`, `librts_spatial_index=164.7`), dominated heavily by AABB. The number is arithmetically correct. It is not presented anywhere as a whole-app speedup claim.

**One structural observation (not a blocking issue):** The evaluator's threshold constants (1.20, 1.50, 0.98, 10.0, etc.) are hardcoded in the evaluation functions, not read from `V4_GOAL4638_PERFORMANCE_FLOORS`. The freeze validator confirms structural integrity of the floor table, but does not cross-verify that the evaluator's thresholds match it. For this run the constants match exactly. This is a latent drift risk for future goal cycles, not a defect in Goal4639.

---

## Q3 — Is `release_candidate_possible_pending_3ai` the correct recommendation?

**Yes.** The freeze defines exactly three recommendations:
- `release_candidate_possible_pending_3ai` — all strong rows and all measured surfaces pass
- `performance_preview_only` — any strong row or measured surface fails
- `blocked_incomplete` — environment failures prevent a fair reading

All 4 strong families passed. All 8 measured surfaces passed. Zero failures. Zero blocked rows. The condition in the code is a correct implementation of the freeze definition.

The "pending_3ai" qualifier is not a loophole — it accurately names the remaining gate (Goal4642) that must be cleared before any release claim is possible. The recommendation is carried forward with `release_authorized: False` and `release_candidate_authorized: False` throughout the decision chain.

---

## Q4 — Are partial and deferred rows handled honestly?

**Yes.**

Partial rows (hausdorff_xhd, robot_collision, contact_manifold, rtnn): all 4 pass, all 4 carry `"excluded_from_release_geomean": true` in the JSON, none contribute to the strong geomean. The evaluator iterates them separately from strong rows and never includes their representative ratios in any aggregate.

Deferred rows (spatial_rayjoin, barnes_hut): both have `"passed": null` (not false — correctly reflecting "not attempted, not applicable"), both carry `"excluded_from_release_geomean": true`, and both carry the reason string `"no V4.0 measured generic operator surface in frozen Goal4638 scorecard"`. The deferred count is exactly 2 as required.

Neither deferred family is presented as failing; neither is silently dropped. The decision doc names them explicitly under "Deferred/excluded rows remain."

---

## Q5 — Is the updated `v4_release_decision.py` honest?

**Yes, and it is notably careful.**

G9 (`G9_serious_release_scorecard_pod_gate`) is now `passed_for_release: True` with the correct decision token. G10 (`G10_final_release_authorization`) remains `passed_for_release: False`.

The `release_blockers` tuple includes all of:
- `goal4639_passed_pending_external_review_completion` — honest acknowledgment that this very review is not yet complete when the code was written
- `goal4640_user_docs_cleanup_not_done`
- `goal4641_clean_tree_reproducibility_gate_not_done`
- `goal4642_final_3ai_release_authorization_not_done`
- `external_review_debt_antigravity_goal4638_formal_scorecard_freeze`
- All existing review-debt blockers from Goals 4633–4637

The `validate_v4_goal4632_release_decision` function enforces all of these as required invariants, so they cannot be silently dropped in a future edit. The `public_wording` field reads `"V4 high-performance scorecard passed for documented generic RT-core operator surfaces; final release authorization pending."` — bounded and accurate.

The `allowed_claims` list is bounded to operator-level evidence. The `forbidden_claims` list explicitly includes "V4 release", "V4 release candidate", "broad V4 speedup", "whole-application speedup", "CuPy performance", "Tier-3 callback support", and "C ABI / embedding / non-Python host".

---

## Q6 — Amendments required before Goal4640?

**None required.**

The following observations are noted but do not block Goal4640:

1. **Evaluator–freeze threshold coupling**: The evaluator's pass/fail thresholds are hardcoded rather than read from `V4_GOAL4638_PERFORMANCE_FLOORS`. For Goal4639 the constants are exactly correct. Future releases using a different frozen scorecard would need to update both. This is a maintenance note for Goal4644 (post-release guardrails), not a defect here.

2. **Antigravity review debt for Goal4639 itself**: No Antigravity review artifact exists for Goal4639 (consistent with the pattern for Goals 4633–4638). The release decision records `goal4639_passed_pending_external_review_completion` as an active blocker. That blocker should be updated to distinguish "Claude review complete, Antigravity debt recorded" once this review is accepted. Goal4640 may start under the owner-approved review-debt rule.

3. **Component-union representative ratio margin**: The minimum ratio for this surface is `1.20294x` against a floor of `1.20x`. The margin is ~0.3 percentage points. This is a valid pass by the frozen floor. It is narrow, but the floor was set before results were seen, so there is no post-hoc floor selection.

4. **Weighted-sum minimum ratio shift**: The new run produces `1.4818x` as its minimum (versus Goal4633's `1.2011x`). Both pass the 1.20x floor. The variation is plausible for a fresh POD run and does not indicate score inflation.

---

## Summary

Goal4639 ran the frozen Goal4638 scorecard on the RTX A5000 POD under the correct conditions. All 8 measured surfaces passed their frozen floors. All 4 strong families passed. Partial and deferred rows are honestly recorded and excluded from the geomean. The recommendation `release_candidate_possible_pending_3ai` is correct and does not authorize release or release-candidate wording. The updated `v4_release_decision.py` keeps final release blocked and lists all remaining gates as explicit blockers.

**Verdict: `approve_goal4639_scorecard_pass_continue_goal4640`**

Review debt for Goal4639: Antigravity seat empty (consistent with prior pattern). This debt must be recorded in the release decision before Goal4642 exits.
