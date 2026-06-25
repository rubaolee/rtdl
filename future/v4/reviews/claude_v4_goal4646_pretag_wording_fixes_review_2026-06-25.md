I now have everything I need for the review. Let me write it.

---

# Claude Review — V4 Goal4646 Pre-Tag Wording Fixes

**Date:** 2026-06-25
**Reviewer:** Claude (Sonnet 4.6, independent review seat)
**Sources reviewed:** All files listed in the call for review, plus primary sources `docs/reviews/claude_v4_0_0_release_review_2026-06-25.md` and `future/v4/v4_goal4646_pretag_mandatory_wording_fixes_2026-06-25.md`.

---

## Verdict

```text
verdict: accept_goal4646_wording_fixes_tag_unblocked
```

Fix 1, Fix 2, and Fix 3 are all genuinely implemented. The public tag is unblocked by wording. The V4.1 obligation (A4: hand-written OptiX baseline for a low-ratio operator) remains correctly deferred and is not re-opened here.

---

## Findings by Severity

### No blockers

### Low — old label survives in historical review archives (expected, acceptable)

The string `RTDL v4.0.0 formal high-performance generic RT-core operator release` still appears in `future/v4/reviews/antigravity_v4_goal4642_*`, `future/v4/reviews/codex_*`, `future/v4/reviews/goal4642_*`, and in my own prior Goal4644 guardrails review. These are historical external review records, written when the old label was the proposed label. The completion record explicitly chose to preserve them rather than retroactively rewrite them. This is the correct approach — historical external review artifacts should not be edited after the fact. The test suite (`PUBLIC_TAG_DOCS`) correctly excludes review archives from the no-old-label assertion.

The string also appears in `future/v4/rtdl_v4_0_three_tier_fused_architecture_design_2026-06-24.md` ("near-OptiX performance from Python") and in `future/v4/v4_0_current_status_and_next_steps_2026-06-25.md` (mentions `5.185x geomean`). Neither file is in the tested public-doc scope. These are internal/historical planning artifacts, not public-facing release docs. Acceptable.

### Observation — `docs/current_v4_status.md` header says "formal V4.0.0 bounded operator release authorized"

The word "formal" remains. This is not the same string as the old unqualified label and carries no "high-performance" or "near-OptiX" implication. Not a problem.

---

## Question-by-Question Answers

**Q1. Are Fix 1, Fix 2, and Fix 3 genuinely completed?**

Yes.

- **Fix 1:** The machine constant `V4_AUTHORIZED_RELEASE_LABEL` is `"RTDL v4.0.0 bounded operator release: 8 generic RT-core operators faster than brute-force partner/CPU baselines"` in `src/rtdsl/v4.py:51-54`, `src/rtdsl/v4_scope.py:8-10`, and `src/rtdsl/v4_release_decision.py:24-27`. All three agree. The catalog gate and quickstart both emit this label verbatim. All public-facing docs use it.

- **Fix 2:** `README.md` reports the honest distribution: "most measured operators are 1.2x-1.7x… point-group nearest witness (389.707x) and AABB all-ops (164.716x) are large scale-dependent algorithmic-complexity wins" with explicit instruction "Do not use the raw geomean as a headline." `docs/current_v4_status.md`, `future/v4/README.md`, and `future/v4/v4_goal4643_publication_decision_2026-06-25.md` all repeat the distribution and explicitly label the geomean as "internal scorecard math" not suitable for the public headline.

- **Fix 3:** `src/rtdsl/v4_goal4639_release_scorecard_decision.py:23-63` defines `V4_GOAL4639_SURFACE_DENOMINATORS` for all 8 surfaces, each with `baseline`, `scale`, and `presentation_class`. All four doc tables (`docs/current_v4_status.md`, `future/v4/README.md`, `future/v4/tier2_operator_catalog.md`, `future/v4/v4_goal4639_serious_release_scorecard_pod_gate_decision_2026-06-25.md`, and `future/v4/evidence/.../summary.md`) include explicit `Baseline / denominator` and `Scale` columns.

**Q2. Does current public wording avoid the old unqualified high-performance label?**

Yes. The grep for `formal high-performance generic RT-core operator release`, `near-OptiX performance from Python`, and `Representative operator geomean` returns zero matches in the public docs scope: `README.md`, `docs/current_v4_status.md`, `docs/learn/performance_wording.md`, `future/v4/README.md`, `future/v4/tier2_operator_catalog.md`, `future/v4/v4_goal4642_*`, `future/v4/v4_goal4643_*`, `future/v4/v4_goal4644_*`, `scripts/v4_catalog_regression_gate.py`, and `src/rtdsl/v4*.py`. `docs/learn/performance_wording.md` explicitly lists "unqualified 'high-performance' or 'near-OptiX' wording" as not allowed.

**Q3. Is the raw 5.185x geomean demoted from public headline to internal scorecard math?**

Yes. Every location that mentions the geomean value now labels it "internal" or pairs it with an explicit prohibition on using it as the public headline:
- `src/rtdsl/v4_goal4639_release_scorecard_decision.py:89`: field is `strong_representative_ratio_geomean`; `headline_rule` string is `"Do not headline the 5.185x geomean"`.
- `future/v4/v4_goal4639_serious_release_scorecard_pod_gate_decision_2026-06-25.md` scorecard table row: "Internal strong representative ratio geomean | 5.1848…".
- `future/v4/evidence/.../summary.md:19`: "The raw geomean above is retained as scorecard math, not as public headline wording."
- `future/v4/v4_goal4643_publication_decision_2026-06-25.md:32`: "The raw 5.185x operator-scorecard geomean is retained as internal scorecard math, but it must not be used as the public headline."

**Q4. Are point-nearest and AABB clearly labeled as scale-dependent algorithmic-complexity wins, not kernel-quality or near-OptiX wins?**

Yes. Both the human-readable and machine-readable layers are consistent:
- `V4_GOAL4639_SURFACE_DENOMINATORS` assigns `presentation_class: algorithmic_complexity_outlier_o_n2_vs_bvh` (point-nearest) and `algorithmic_complexity_outlier_indexed_bvh_vs_slower_control` (AABB).
- `future/v4/tier2_operator_catalog.md:29`: "Point-group nearest witness and AABB all-ops are large scale-dependent algorithmic-complexity wins, not evidence of near-hand-written-OptiX kernel quality."
- `future/v4/evidence/.../summary.md`: "algorithmic-complexity outlier" and "algorithmic-complexity/indexed-control outlier" in the Presentation column.
- Test `test_outliers_are_labeled_as_scale_dependent_complexity_wins` asserts the exact presentation_class strings and the headline_rule.

**Q5. Does every representative ratio have a baseline/denominator and scale?**

Yes. All 8 surfaces have explicit denominator entries in `V4_GOAL4639_SURFACE_DENOMINATORS`. The validate function (`validate_v4_goal4639_release_scorecard_decision`) asserts this: for every surface in `surface_representative_ratios`, it checks that a non-empty `denominator` with non-empty `baseline` and `scale` fields exists. Test `test_each_scorecard_surface_has_denominator_and_scale` asserts 8 surfaces, all keys match, all have baseline/scale/presentation_class.

**Q6. Did the changes preserve V4.0 scope boundaries and forbidden claims?**

Yes. All scope-boundary flags are unchanged:
- `release_claim_authorized: False`, `broad_v4_speedup_claim_authorized: False`, etc. across `v4.py:74-83`, `v4_scope.py:59-66`, `v4_goal4639_release_scorecard_decision.py:94-106`, `v4_release_decision.py:255-265`.
- The `FORBIDDEN_CLAIM_FLAGS` list in `scripts/v4_catalog_regression_gate.py:19-31` is unchanged. The validator recursively walks all payloads and fails if any of those flags is not `False`.
- All doc `Non-Authorization` / `Non-Claims` sections retain the full forbidden list verbatim.
- `V4_0_CANDIDATE_SURFACES = ()` is unchanged; the quickstart reports `candidate_surface_count: 0`. No scope expansion.

**Q7. Is the public tag unblocked by wording, or are amendments still required?**

The tag is unblocked. All three conditions from my prior review (A1/A2/A3) are met. The A4 deferral (hand-written OptiX baseline for a low-ratio operator) is correctly recorded as a V4.1 obligation in `future/v4/v4_goal4646_pretag_mandatory_wording_fixes_2026-06-25.md:60-64` and is not a tag blocker.

---

## Test Coverage Assessment

The 39-test targeted group covers the exact conditions required:
1. `test_public_label_is_bounded_to_stated_baselines` — label identity against machine constant.
2. `test_public_docs_do_not_use_old_unqualified_label` — per-file assertion on the 7 public docs.
3. `test_current_release_docs_report_distribution_not_geomean_headline` — distribution language in 4 docs.
4. `test_each_scorecard_surface_has_denominator_and_scale` — all 8 denominators complete.
5. `test_outliers_are_labeled_as_scale_dependent_complexity_wins` — exact presentation_class strings + headline_rule.

The 185-test full V4 group provides regression coverage that the scope boundaries and machine constants were not inadvertently altered.

---

## Tag-Blocker Disposition

| Blocker | Status |
| --- | --- |
| A1: qualify label; state baseline | Closed — label is bounded/brute-force in all public surfaces |
| A2: report distribution; demote geomean headline | Closed — distribution is the public presentation; geomean labeled internal |
| A3: state denominator and scale for every ratio | Closed — all 8 surfaces have explicit baseline/scale/presentation_class |
| A4 (V4.1): hand-written OptiX baseline for low-ratio operator | Deferred — correctly not a tag gate |

---

## Non-Authorization

This review authorizes only the unblocking of the public wording/tag gate for the V4.0.0 bounded operator release with corrected label `RTDL v4.0.0 bounded operator release: 8 generic RT-core operators faster than brute-force partner/CPU baselines`.

This review does **not** authorize: broad V4 speedup, whole-application speedup, all-benchmark speedup, near-handwritten-OptiX performance claims, public true-zero-copy, Tier-3 callback support, raw OptiX callback support, CuPy performance, C ABI, embedding, non-Python host bindings, app-specific native kernels, Barnes-Hut coverage, Spatial RayJoin coverage, or LibRTS paper reproduction.
