# Goal1208 Claude Review: Public Wording Decision After Goal1206

Date: 2026-05-01
Reviewer: Claude (claude-sonnet-4-6)
Verdict: `ACCEPT`

---

## Scope

This review covers the Goal1208 public wording decision packet — its three per-app decisions, the code that generates them, the candidate public wording, and whether the decisions are conservative and technically justified by Goal1206 evidence before any public doc is changed.

Source evidence accepted upstream: Goal1206 two-AI consensus `ACCEPT`, Gemini live-pod merged evidence review `ACCEPT`.

---

## Per-Question Assessment

### Q1. Are the decisions conservative and technically justified by Goal1206?

**Yes.** All three decisions are derived directly from the accepted Goal1206 merged intake data:

- Road hazard ratio 3.53225x is drawn from intake `same_scale_public_positive_candidate: True` plus `ratio_embree_over_optix: 3.53225`, confirmed by the Goal1206 consensus and Gemini review.
- DB ratios 1.12265 and 1.16357 are drawn verbatim from the 100k/300k repair rows in the intake. The code conservatively uses `min()` across all repair rows, yielding 1.12265 as the governing ratio.
- Jaccard status is drawn from `public_safe: True / parity: True` (chunk 512) and `diagnostic_only: True / parity: False` (chunk 64), exact intake fields.

No inference or extrapolation beyond the accepted intake occurs.

### Q2. Is it correct to promote only `road_hazard_screening` to reviewed positive wording?

**Yes.** Road hazard is the only app that satisfies all three promotion gates simultaneously:

1. `same_scale_public_positive_candidate: True` in the intake (floor-safe, same-scale timing confirmed by Goal1206).
2. `ratio_embree_over_optix` (3.53x) ≥ `MIN_PUBLIC_RATIO` (1.2x).
3. Both conditions checked independently in `_road_decision()` — belt-and-suspenders approach is correct.

Neither DB nor Jaccard meets the same gate set, so promoting only road hazard is the right call.

### Q3. Is it correct to keep DB speedup wording blocked despite the repaired OptiX operation?

**Yes.** The block is technically required:

- The code takes `min(ratios)` = 1.12265, which is below the 1.2x public threshold.
- The 1.16357 (300k) ratio also falls below threshold; using the minimum is the conservative choice and prevents a best-case ratio from driving promotion.
- The candidate wording for the blocked state ("repaired at 100k and 300k, but the measured 1.12x-1.16x advantage is below the 1.2x public speedup threshold") is accurate and does not suppress the repair fact — it correctly distinguishes operational repair from speedup-threshold readiness.
- Test `test_database_below_threshold_not_promoted` asserts `raw_ratio_embree_over_optix < min_public_ratio` and validates the wording contains "below the 1.2x public speedup threshold". Both pass.

### Q4. Is the Jaccard correctness-only wording narrow enough?

**Yes.** The wording is narrow on two axes:

1. **Scope axis:** "public-safe chunk correctness evidence at chunk 512" — no speedup claim, no arbitrary-chunk generalization, no whole-app claim.
2. **Exclusion axis:** "no positive RTX speedup wording is authorized because this packet has no same-scale Embree speedup comparison and chunk 64 remains diagnostic-only/parity-failing" — the reason for the speedup block is stated explicitly.

The boundary clause further excludes exact area refinement, Jaccard whole-app speedup, arbitrary chunk sizes, row materialization, and Python postprocess. These exclusions match what the intake data supports and what Goal1206 explicitly limited.

The `_jaccard_decision()` logic correctly requires both the `public_safe/parity=True` row AND the `diagnostic_only/parity=False` row before setting `ready = True`. If either condition were absent from the intake, the decision would fall to `blocked_or_incomplete`.

---

## Code Review

### `_db_decision`

`min(ratios)` as the governing ratio is correct — prevents promotion on a best-case data point when multiple scales are present. Using `min_ratio >= MIN_PUBLIC_RATIO` (strict `>=`) is appropriately conservative. No issue.

### `_road_decision`

Double-guards `positive` with both the intake flag (`same_scale_public_positive_candidate`) and the numeric ratio check. Neither condition alone is sufficient. This is the right design because the intake flag reflects pod-side floor/scale validation that the ratio number alone cannot capture. No issue.

### `_jaccard_decision`

`ready` requires both conditions (safe parity-passing row AND diagnostic parity-failing row). This means the function will not emit a positive correctness state unless the intake actually contains evidence of the parity-failing chunk — it cannot silently omit the negative. No issue.

### `build_packet`

`public_speedup_claim_authorized_count` is hardcoded to `0`. This is correct per the packet boundary: Goal1208 proposes wording states but does not edit public docs or finalize speedup claims. Road hazard appearing in `proposed_public_wording_reviewed_apps` means its wording is reviewed and ready to apply — a downstream step applies it. The count of 0 means this packet itself does not execute that application.

**Semantic note (non-blocking):** The field name `public_speedup_claim_authorized_count` could be misread as "no speedup was found" when a reader sees road hazard promoted. Adding a comment or renaming to `public_speedup_claims_applied_by_this_packet` would eliminate the ambiguity. This does not block acceptance.

### Test suite

Three tests cover the critical invariants:

| Test | What it enforces |
| --- | --- |
| `test_goal1206_decisions_are_bounded` | All three app statuses are correct; speedup count is 0 |
| `test_database_below_threshold_not_promoted` | DB ratio is strictly below threshold; wording references threshold |
| `test_markdown_preserves_no_release_boundary` | Output markdown contains boundary text |

**Gap (non-blocking):** No test verifies that road hazard candidate wording contains the measured values (0.230652 s, 3.53x, 40k copies). A regression that changed the `_fmt_sec`/`_fmt_ratio` output would not be caught. Recommend adding a `test_road_hazard_wording_contains_measured_values` test in a follow-up.

---

## Candidate Public Wording Audit

### `road_hazard_screening`

> RTDL's prepared native road-hazard RTX sub-path measured 0.230652 s and 3.53x versus the reviewed same-scale Embree sub-path at 40k copies.

- Values match intake: OptiX 0.230652s, ratio 3.532x, scale 40k. ✓
- "reviewed same-scale Embree sub-path" correctly attributes the comparison to the accepted recovery run. ✓
- Boundary excludes default app behavior, GIS/routing, row materialization, Python setup, whole-app speedup. ✓

### `database_analytics`

> RTDL's prepared DB compact-summary RTX sub-path is repaired at 100k and 300k, but the measured 1.12x-1.16x advantage is below the 1.2x public speedup threshold.

- Repair status is accurate (both scales repaired per intake). ✓
- Range 1.12x-1.16x matches intake ratios. ✓
- Threshold reference (1.2x) is explicit. ✓

### `polygon_set_jaccard`

> RTDL's polygon-set Jaccard OptiX path has public-safe chunk correctness evidence at chunk 512; no positive RTX speedup wording is authorized because this packet has no same-scale Embree speedup comparison and chunk 64 remains diagnostic-only/parity-failing.

- Positive evidence scoped to chunk 512 only. ✓
- Two distinct reasons for speedup block are stated: no Embree comparison, chunk 64 parity-failing. ✓
- Does not imply arbitrary-chunk generalization. ✓

---

## Findings Summary

| Item | Severity | Status |
| --- | --- | --- |
| All three decisions derive from accepted Goal1206 evidence | — | PASS |
| Road hazard promotion satisfies both intake flag and ratio gate | — | PASS |
| DB blocked because min ratio 1.12x < 1.2x threshold | — | PASS |
| Jaccard limited to correctness; speedup block reason stated | — | PASS |
| `public_speedup_claim_authorized_count = 0` consistent with boundary | — | PASS |
| Candidate wording values match intake data | — | PASS |
| `public_speedup_claim_authorized_count` field name ambiguous | non-blocking | NOTE |
| No test for road hazard wording measured-value preservation | non-blocking | NOTE |

---

## Verdict: `ACCEPT`

The three wording decisions are conservative, technically grounded in accepted Goal1206 evidence, and correctly scoped. No public doc edits are authorized by this packet alone; road hazard positive wording is ready to apply in a downstream step. The two noted gaps are non-blocking and may be addressed as follow-up.
