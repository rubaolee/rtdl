I have all the information needed. Here is the full review.

---

## Review: V4 Goal4629 Weighted-Sum Candidate Decision

**Verdict: `accept_with_required_amendments`**

---

### Q1 — Is `keep_candidate_not_promoted` the right decision from the existing evidence?

**Yes.** The Goal4620 completion consensus (two external seats + one internal, one Antigravity debt) explicitly authorized `accept_goal4620_complete_candidate_not_promoted` and did not authorize measured-catalog promotion. The current evidence is two shapes only, five repeats after two warmups, Torch CUDA partner only. The ratios are positive (2.047×, 1.557×) but neither the size matrix nor the repeat count nor the partner coverage reaches promotion-gate standards. `keep_candidate_not_promoted` is the only defensible decision from this evidence.

---

### Q2 — Does the document correctly preserve the positive candidate value without hiding it as a failure?

**Yes.** The document has a dedicated "Why This Is Not A Rejection" section that explicitly records all three positive results: parity passed at both sizes, device-output path beat host-scalar at both sizes, hot path avoided host scalar read and row materialization. The code sets `candidate_gate_passed: True` and `candidate_evidence_is_positive: True`. The decision string is `"keep_candidate_not_promoted"`, not a rejection label. The surface remains `tier2_candidate_goal4620_not_measured` — its candidate status is preserved as a future promotion target.

---

### Q3 — Does the document correctly prevent measured-catalog and release-surface overclaiming?

**Yes.** The document has a "Why This Is Not A Promotion" section listing six blockers. The code enforces:
- `measured_catalog_promotion_authorized: False`
- `weighted_sum_can_count_as_measured_release_surface: False`
- `release_scorecard_slot_closed_as: "explicit_candidate_kept_not_promoted"`
- All nine claim-authorization flags `False`

The `validate_v4_goal4629_weighted_sum_candidate_decision()` function raises on any violation of these invariants.

---

### Q4 — Does the decision preserve Goal4627's `triangle_counting` classification as candidate-bound?

**Yes.** The document records `triangle_counting_release_coverage_after_goal4629: candidate_not_measured_release_coverage`. The code includes this key in the returned dict. Test `test_triangle_counting_remains_candidate_bound` cross-checks Goal4627's live coverage rows directly, verifying `rows_by_app["triangle_counting"].coverage_status == V4_COVERAGE_CANDIDATE` and that `V4_GOAL4629_SURFACE` is in its `mapped_v4_operators`. This is the right defense layer.

---

### Q5 — Are the listed future promotion requirements sufficient for a later measured-catalog attempt?

**No. This is the amendment-bearing gap.**

The `promotion_blockers` tuple lists six blockers. The `future_promotion_requirements` tuple lists only five items. Three blockers are not mirrored as requirements:

| Blocker in `promotion_blockers` | Missing from `future_promotion_requirements` |
|---|---|
| `repeat_count_is_candidate_gate_level_not_release_promotion_level` | No requirement to increase repeat count |
| `cupy_and_non_torch_partner_performance_unmeasured` | No requirement to measure CuPy / non-Torch partners |
| `triangle_counting_whole_app_or_primary_route_release_coverage_not_proven` | No requirement to prove triangle_counting primary route coverage |

A future promotion gate that satisfies only the five listed requirements could still have five candidate-level repeats, only Torch CUDA measured, and triangle_counting still unproven — yet claim all requirements met. The requirements list must mirror all six blockers.

---

### Q6 — Are the tests and code-level scorecard adequate to prevent Goal4632 from miscounting this surface?

**Yes, with the caveat that Goal4632 must honor the contract.** The existing tests check `weighted_sum_can_count_as_measured_release_surface: False` directly, and `test_triangle_counting_remains_candidate_bound` verifies the Goal4627 coverage rows at the live-import level. The validate function makes the invariants machine-checkable. The defense is structural: Goal4632 would need to import these modules and respect their flags. The current artifacts create a clear, importable contract that is as strong as this pattern allows before Goal4632 is written.

---

### Q7 — Are all non-authorization boundaries preserved?

**Yes.** The `validate_*` function enforces all nine non-authorization flags programmatically. The document's Non-Authorization section lists 11 items — covering all eight from the call-for-review plus raw OptiX callback support and CuPy performance claims. The code records `partner_scope: ("torch_cuda",)` and `cupy_performance_claim_authorized: False` explicitly. No boundary from the call-for-review is absent or softened. V4 release, measured-catalog promotion, broad speedup claims, true-zero-copy, Tier-3 callback, C ABI/embedding, and app-specific native kernels are all explicitly not authorized.

---

### Required Amendments

**A1 — Expand `future_promotion_requirements` to mirror all promotion blockers (document + code + tests)**

In `future/v4/v4_goal4629_weighted_sum_candidate_decision_2026-06-24.md`, "Future Promotion Requirements" section — add:
- `increase_repeat_count_to_release_gate_level_beyond_5_candidate_repeats`
- `measure_cupy_and_non_torch_partner_performance`
- `prove_triangle_counting_primary_route_release_coverage`

In `src/rtdsl/v4_weighted_sum_candidate_decision.py`, `future_promotion_requirements` tuple — add the same three items.

In `tests/v4_goal4629_weighted_sum_candidate_decision_test.py`, `test_decision_preserves_device_output_metadata_and_promotion_blockers` — add `assertIn` checks for all three new requirement strings in `decision["future_promotion_requirements"]`.

No other amendments are required. The core decision, non-authorization architecture, triangle_counting preservation, and candidate-value framing are all correct.
