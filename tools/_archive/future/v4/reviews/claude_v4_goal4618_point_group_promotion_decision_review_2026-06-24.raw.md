I have the information I need. Here is the formal external review.

---

## External Review: `goal4618` Point-Group Nearest-Witness Promotion Decision

**Reviewer:** Claude Sonnet 4.6 (external)
**Date:** 2026-06-24
**Subject:** `v4_point_group_nearest_witness_2d_device_arrays` — promotion-decision packet

---

## Verdict

**`authorize_point_group_promotion_patch`**

The evidence chain is complete and internally consistent. All three prior amendments are confirmed closed. The new mixed6 gate closes the outstanding non-axis no-hit coverage concern. Claim boundaries are correctly enforced throughout. Promotion to the measured catalog is authorized subject to the post-patch gates listed below.

---

## Findings by Severity

### BLOCKING — None

No blocking findings. Authorization proceeds without required pre-patch amendments.

---

### MEDIUM — Verify Before Marking Gate Green

**M-1: operator_callback_planning_tier2 gate set may need updating**

The catalog regression gate at `scripts/v4_catalog_regression_gate.py:191–195` validates the tier2 planner against a hardcoded set of three surfaces:

```
v4_fixed_radius_count_threshold_2d_device_arrays
v4_closest_hit_grouped_argmin_3d_device_arrays
v4_ray_triangle_any_hit_flags_2d_device_arrays
```

`v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays` (goal4617, already measured) is not in this set, and the existing gate passes — which suggests the planner test selects a deterministic example, not a random measured surface. The patch's `--include-candidates` → measured promotion does not affect the `operator_callback_planning_tier2` example command, and this is likely safe. However: **the post-patch GPU gate run must confirm this validator still passes at 5 measured surfaces**. If the planner's example can randomly select the new 5th surface and return `v4_point_group_nearest_witness_2d_device_arrays`, the gate will fail because that surface is not in the allowed set. Resolve by either adding point-group to the set or confirming the planner example is fixture-pinned.

**M-2: Claim boundary function must cleanly remove candidate fields on promotion**

`v4_point_group.py:37–45` currently emits:
```python
"measured_partner": False,
"measured_partners": (),
"pod_candidate_partners": V4_POINT_GROUP_POD_CANDIDATE_PARTNERS,
"partner_claim_status": V4_POINT_GROUP_CANDIDATE_STATUS  # "candidate_pod_repeat_gate..."
```

After the patch, Torch must be `measured_partner: True`, `measured_partners: ("torch",)`, and the `partner_claim_status` for Torch must not retain the `candidate_pod_repeat_gate_passed_requires_external_review_before_release_scope` string. This string would be self-contradicting in measured status. The patch must either remove `partner_claim_status` for Torch or replace it with a correctly scoped measured-status string. Verify the post-patch claim boundary output does not retain candidate-status language for Torch. CuPy may retain its `declared_unmeasured_not_performance_ready` status string.

---

### LOW — Wording and Documentation

**L-1: float32/float64 distance dtype gap should appear in scope statement**

The evidence JSON records the distance output column as `dtype: float64` at both sizes. The native OptiX computation is float32. The oracle fix (first mixed6 attempt used float64 math; corrected to float32) is appropriate and well-disclosed, but the scope statement in the packet does not note that the distance output buffer is float64-typed while the underlying computed distances are float32-precision values. If this surface is ever described in user-facing documentation, the precision contract must be explicit: distance values are float32-precision regardless of the output column dtype.

**L-2: `pod_candidate_partners` field will become dead metadata after promotion**

The constant `V4_POINT_GROUP_POD_CANDIDATE_PARTNERS = ("torch",)` and the constant `V4_POINT_GROUP_CANDIDATE_STATUS` will be orphaned dead code after the patch if Torch moves fully to the measured set. Either remove the constants or keep them clearly annotated as historical evidence anchors. Orphaned constants with `candidate` in the name on a measured surface will confuse future readers.

---

### INFO — No Action Required

**I-1: First mixed6 attempt failure is honestly disclosed and appropriately excluded**

The failed oracle run is clearly documented as "not used as promotion evidence." Both device outputs and legacy rows agreed with each other on that run; only the float64 oracle's expected values were wrong. This is a harness correction, not a native-path defect. The disclosure is honest and the handling is correct.

**I-2: Antigravity peer review file is empty**

`future/v4/reviews/antigravity_v4_goal4618_point_group_promotion_decision_review_2026-06-24.raw.md` is 1 line (effectively empty). This review proceeds as a single-AI external review. The 3-AI completion review remains a required post-patch gate. This is not a blocker for the promotion patch itself, which requires only external reviewer consensus, not multi-AI consensus at this stage.

**I-3: Performance ratio is slightly lower on mixed6 than on the original fixture (509x vs 663x at 32K)**

This is expected: the mixed6 fixture has 1/3 no-hit rows (which produce sentinel values immediately without full traversal) and mixed diagonal/axis geometry. The 1863x ratio at 131K is consistent with the original 1868x. No concern.

---

## Explicit Answers to the Seven Reviewer Questions

**Q1. Should point-group nearest-witness be authorized for the atomic measured-catalog promotion patch, or kept as candidate?**

**Authorize.** The original 4-pattern POD gate and the new 6-pattern mixed6 POD gate both pass parity at 32K and 131K. Claim boundaries are correctly enforced. All three prior amendments are verifiably closed. No blocking finding was identified. The operator is correctly generic and app-name-free throughout.

**Q2. Does the new mixed6 POD evidence close the non-axis no-hit coverage concern?**

**Yes.** The prior amendment closure review (I-3) flagged that the original fixture tested no-hit only via a y-axis offset against a y=0 plane. The mixed6 fixture adds `diagonal_no_hit` rows (5,461 at 32K, 21,845 at 131K) with the pattern `diagonal_hit/diagonal_no_hit`, covering off-axis geometry. Combined with the y-axis no-hit rows, both axis-aligned and non-axis no-hit cases are now exercised. The concern is closed.

**Q3. Is the narrower prepared-search/groups boundary acceptable for a measured surface if the hot query/output path is direct device-array?**

**Yes.** The boundary is clearly defined and consistently enforced throughout the stack: RTDL owns and prepares the native scene, caller supplies and receives Torch CUDA device columns in the hot path. This is the same architectural pattern used by other measured Tier-2 surfaces. The claim boundary metadata (all four `_in_hot_path: false` flags), the wording rules (no "true zero-copy," no "all inputs caller-owned"), and the scope statement all accurately represent this split. A measured surface at this boundary is appropriate.

**Q4. Is the OptiX 8.0 maximum-validated ABI scope acceptable, or must OptiX 9.1 be tested first?**

**Acceptable.** The grouped_i64_reduction surface (goal4617) already entered the measured catalog with `validated_optix_abi: "8.0"` and `optix_9_1_validated: False`, and that precedent was accepted by reviewers. Point-group should carry the same explicit scope annotation. OptiX 9.1 remains unmeasured and must not be claimed. The proposed scope statement correctly records this.

**Q5. Are the proposed patch steps sufficient without claim drift?**

**Yes, with one caveat.** The 8 patch steps are structurally complete and correctly enumerate what must change. The caveat is M-2 above: the claim boundary function update must not leave `V4_POINT_GROUP_CANDIDATE_STATUS` language on Torch after promotion. The patch description says to update the claim boundary "so Torch reports measured and CuPy reports declared-unmeasured" — this is the right intent, and if correctly implemented, claim drift is avoided. Verify the post-patch claim boundary output for Torch explicitly before finalizing.

**Q6. Are any additional correctness or performance gates required before the patch may be applied?**

**No additional pre-patch gates are required.** The two independent POD gates (7 repeats, 2 warmups each) at two query counts provide sufficient evidence. Post-patch, the GPU catalog gate at the new measured count of 5 is required (see below). No additional standalone correctness gate beyond that is required before goal4618 completion.

**Q7. If promotion is authorized and the post-patch GPU gate passes, may goal4618 proceed to 3-AI completion review?**

**Yes.** Provided all post-patch gates pass (listed below), goal4618 may proceed to the 3-AI completion review. That review must independently verify the claim boundary state after promotion, confirm no forbidden flags, and confirm no release or broad-speedup wording has been introduced.

---

## Required Post-Patch Gates Before Goal4618 Completion

The following gates are required after the atomic promotion patch is applied, before goal4618 may proceed to 3-AI completion review:

1. **Local test suite passes.** All tests in `tests/v4_operator_catalog_test.py`, `tests/v4_catalog_regression_gate_test.py`, `tests/v4_frontdoor_test.py`, and any point-group-specific tests pass without modification of expected measured/candidate counts.

2. **GPU catalog gate passes with `measured_surface_count == 5` and `candidate_surface_count == 0`.** The gate must execute successfully in GPU mode (not dry-run), point-group must be in the measured block, and the front-door quickstart must report `measured_surface_count == 5`.

3. **Point-group measured surface passes correctness check in GPU gate.** The catalog gate's `correctness_passed` field for the point-group surface must be `true` in the post-patch GPU run, using the standard (not include-candidates) path.

4. **No forbidden claim flags in any post-patch surface output.** The `_forbidden_claim_true_paths` scanner in the catalog regression gate must report zero violations across all measured surfaces.

5. **`operator_callback_planning_tier2` gate still passes.** Confirm the tier2 planner gate is not broken by the addition of the 5th measured surface (see M-1). If the planner can return point-group and the gate's allowed set does not include it, the gate must be updated before marking the run green.

6. **Post-patch claim boundary output for Torch does not retain candidate-status language.** Spot-check the live `point_group_nearest_witness_2d_device_array_claim_boundary_v4(partner="torch")` output after the patch; confirm `measured_partner: True`, `measured_partners: ("torch",)`, and no `candidate_pod_repeat_gate_...` string in any field (see M-2).

---

## Non-Authorization Block

This review:
- **Does not authorize V4 release** of any surface
- **Does not authorize broad V4 speedup wording** or whole-application speedup wording
- **Does not authorize true-zero-copy public wording**; `true_zero_copy_authorized: false` stands
- **Does not authorize CuPy performance claims**; CuPy remains declared-unmeasured
- **Does not authorize OptiX 9.1 scope**; OptiX 9.1 remains unmeasured
- **Does not authorize Tier-3 callback, C ABI, non-Python host bindings, or app-specific native kernels**
- **Does not constitute 3-AI completion review**; that review is a separate required gate
