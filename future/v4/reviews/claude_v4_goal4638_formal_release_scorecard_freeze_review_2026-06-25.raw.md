I now have everything I need. Writing the verdict.

---

## Formal Review: V4 Goal4638 Formal Release Scorecard Freeze

**Date:** 2026-06-25  
**Reviewer:** Claude (claude-sonnet-4-6)  
**Artifacts reviewed:** all six controlling artifacts plus supporting catalog gate

---

### Verdict

**`approve_with_required_amendments_before_goal4639`**

One required amendment must be resolved before Goal4639 may run. Five observations are non-blocking.

---

### Review Question Findings

**Q1. Is the correction accepted: catalog GPU gate demoted to supporting evidence, formal scorecard freeze restored as the controlling Goal4638 exit?**

Yes. The correction is clean and multi-layered:

- `v4_goal4638_formal_release_scorecard_freeze_2026-06-25.md` opens with an explicit Correction Note naming the error and demoting the catalog gate.
- `v4_goal4638_catalog_regression_decision.py` carries a module-level comment: *"The controlling owner-approved Goal4638 exit gate is the formal release scorecard freeze module."*
- `v4_release_decision.py` G8 gate is renamed `G8_formal_release_scorecard_freeze`, points to the freeze doc as primary evidence, and stores the catalog gate decision under the key `catalog_regression_supporting_evidence` — correctly subordinated.
- G8 `passed_for_release=False`. Tested at `v4_goal4632_release_decision_test.py:52-53`.

No remaining artifact implies the catalog GPU gate is the controlling exit. Correction accepted.

---

**Q2. Are the 10 benchmark-family classifications acceptable, or do any look like post-result metric gaming?**

The 4/4/2 split is criterion-driven, not result-driven:

- **Strong (4):** `rt_dbscan`, `raydb_style`, `triangle_counting`, `librts_spatial_index` — each maps to ≥2 V4 measured operators that cover the primary compute bottleneck of the app. The mapping is explicit in the scorecard table.
- **Partial (4):** `hausdorff_xhd`, `robot_collision`, `contact_manifold`, `rtnn` — each maps to only 1 V4 operator (nearest witness or any-hit flags) that partially overlaps the app workflow. Structural reason for partial, not a bad-number retreat.
- **Deferred (2):** `spatial_rayjoin`, `barnes_hut` — listed as "none in V4.0" for operator mappings. Hard structural criterion, not performance-based.

No gaming pattern is detectable from the observable criteria. The partial/deferred rows would only be gaming if they were moved from strong after preliminary numbers came in — the freeze establishes these classifications *before* Goal4639 runs, which is the whole point of the freeze.

The classifications are acceptable. The stronger check — that no classification can change after results are seen — is enforced by the `no_silent_skips` threshold flag and the freeze-doc language *"No benchmark classification, threshold, inclusion rule, or public wording rule may change after Goal4639 results are seen."*

---

**Q3. Are the 8 measured surfaces and zero candidates consistent with the current V4 coverage state?**

Yes, and it is triple-confirmed:

1. `V4_GOAL4638_MEASURED_SURFACES` in the freeze module — 8 entries, validated to be exactly 8 by `validate_v4_goal4638_formal_scorecard_freeze`.
2. `v4_release_decision.py` `measured_surfaces_count: 8`, `candidate_surfaces_count: 0`.
3. The catalog regression gate shows `quickstart_measured_surface_count: 8`, `quickstart_candidate_surface_count: 0` — post-AABB catalog run confirms the count.

The coverage audit breakdown (line 138-141 of `v4_goal4632_release_decision_test.py`) confirms: 4 strong, 4 partial, 0 candidate, 2 deferred — matching the family classifications in Q2.

Consistent.

---

**Q4. Are the Goal4639 thresholds strong enough?**

Structurally, yes. The freeze enforces:
- Correctness/parity required for strong rows (`strong_rows_require_correctness: True`)
- Surface-specific performance floor required for strong rows (`strong_rows_require_surface_specific_performance_floor: True`)
- No silent skips (`no_silent_skips: True`)
- Partial and deferred rows explicitly excluded from release geomean (`partial_rows_excluded_from_release_geomean: True`, `deferred_rows_excluded_from_release_geomean: True`)
- `geomean_must_exclude_partial_and_deferred: True`

All five are verified by `test_freeze_blocks_goal4639_until_external_review`.

**One required amendment follows from this question — see below.**

The structural thresholds are strong. The gap is numeric specificity: the performance floors are defined by reference to existing gate documents, not embedded in the freeze. See Required Amendment.

---

**Q5. Is it correct that Goal4639 remains blocked until this freeze receives at least one substantive external approval and any missing reviewer seat is explicitly tracked as review debt?**

Yes. This is correctly enforced:

- `requires_external_review_before_goal4639: True` in the freeze module, validated by `validate_v4_goal4638_formal_scorecard_freeze`, tested.
- The release decision includes `external_review_debt_remains_for_goal4638_formal_scorecard_freeze` as a named blocker. Tested at `v4_goal4632_release_decision_test.py:83-86`.
- The freeze doc states: *"do not run Goal4639 as a release scorecard until at least one substantive external review approves the frozen scorecard and the missing seat is explicitly tracked."*

This review constitutes the required Claude reviewer seat for Goal4638. Antigravity's absence must be recorded as explicit review debt (joining existing debt for Goals 4633, 4635, 4637) before Goal4639 may proceed.

---

**Q6. Does `v4_release_decision.py` now represent the release path honestly by keeping G8 not passed for release and keeping Goal4639 as a visible blocker?**

Yes. The representation is honest:

- G8 `passed_for_release=False`, note says *"Goal4639 remains blocked until the freeze receives external review."*
- G9 `passed_for_release=False`, decision is `development_state_performance_preview_not_release`.
- `release_authorized=False`, `release_candidate_authorized=False`.
- 11 explicit named blockers, including `goal4639_serious_all_app_scorecard_not_run` and `external_review_debt_remains_for_goal4638_formal_scorecard_freeze`.
- All 12 forbidden-claim flags are False and tested by `test_forbidden_claims_and_flags_stay_false`.

---

### Required Amendment

**The performance floor numerics are not embedded in the freeze document.**

The freeze states: *"every mapped measured surface must either: pass its already frozen surface-specific performance floor, or be recorded as blocked_or_failed with exact failed check."*

The baselines section of the freeze doc names the source documents for each surface but contains no numeric values. A Goal4639 runner or post-run reviewer cannot determine pass/fail from the freeze document alone — they must locate and parse up to 8 upstream gate documents, then exercise judgment about which number in each document constitutes the floor.

This is the V3 failure mode vector: a vague floor defined by reference allows a weaker result to be called "pass" by selective reading of the upstream evidence.

**Required action before Goal4639:** Add a Performance Floor Reference Table to `v4_goal4638_formal_release_scorecard_freeze_2026-06-25.md` and (at minimum) the Python dict in `v4_goal4638_formal_scorecard_freeze.py`. For each of the 8 measured surfaces, state: (1) the minimum acceptable ratio or geomean threshold and (2) the canonical source document. The freeze document must be self-contained enough that an independent Goal4639 reviewer can assess pass/fail without chasing upstream evidence.

Minimum acceptable form — a table appended to the Thresholds section:

| Surface | Minimum floor | Source |
|---|---|---|
| `v4_fixed_radius_count_threshold_2d_device_arrays` | `≥ X.XXx geomean vs. Embree route-D` | Section 8 gate doc |
| … | … | … |

If a surface's floor is *any-pass-from-correctness-only* (no performance floor), that must also be stated explicitly rather than left implicit.

---

### Non-Blocking Observations

1. **Numba scope is accurate.** The catalog regression gate confirms `quickstart_measured_partners: ("numba", "rtdl_native", "torch")` for the 11-example run. The freeze's `measured_scopes: ("torch", "numba", "rtdl_native")` is consistent with actual catalog evidence. No misleading overclaim.

2. **Goal-Level Decision Audit section.** The freeze doc includes a self-critique block ("Was the previous Goal4638 naming stupid? Yes."). This is honest and transparent. Unusual governance style but not a defect.

3. **Accumulated Antigravity review debt.** Goals 4633, 4635, 4637, and 4638 are all pending Antigravity review. The policy permits proceeding on single-reviewer approval with debt recorded — this is consistent with the freeze doc's own stated review requirement. The debt must be named explicitly before Goal4639 starts, not deferred to Goal4642.

4. **`measured_catalog_promotion_authorized`** is `False` in `v4_release_decision.py`. This flag is slightly misnamed (measured catalog promotion already happened for AABB/component-union) — but its meaning in context is clear as "no broader measured catalog promotion is authorized," and the tests pass. Not a defect.

5. **9 tests OK / 153 tests OK** — local sweep reported in the call-for-review. These are necessary but not sufficient for Goal4638 approval. The required amendment concerns document completeness, not test correctness.

---

### Summary

Goal4638's structural logic is correct: the freeze genuinely blocks Goal4639, the classifications are criterion-driven, the non-authorization flags are exhaustive and tested, and the catalog gate demotion is properly executed. The one required amendment — embedding or summarizing the numeric performance floors in the freeze document — closes the remaining V3 failure mode gap before the POD run.

**`approve_with_required_amendments_before_goal4639`**
