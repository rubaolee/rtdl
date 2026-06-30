# Goal978 Claude Review

**Date:** 2026-04-26
**Reviewer:** Claude (claude-sonnet-4-6)
**Verdict:** ACCEPT

---

## Scope

Reviewed:
- `scripts/goal978_rtx_speedup_claim_candidate_audit.py`
- `tests/goal978_rtx_speedup_claim_candidate_audit_test.py`
- `docs/reports/goal978_rtx_speedup_claim_candidate_audit_2026-04-26.json`
- `docs/reports/goal978_rtx_speedup_claim_candidate_audit_2026-04-26.md`
- Source package: `docs/reports/goal971_post_goal969_baseline_speedup_review_package_2026-04-26.json`
- Selected upstream baseline artifacts (segment_polygon_anyhit_rows OptiX baseline; hausdorff_distance cpu_oracle baseline)

---

## Arithmetic Verification

All 17 ratio values in the output JSON were independently verified as `fastest_non_optix_baseline_sec / rtx_sec`. Every classification matches the computed ratio under the stated thresholds. Spot-checks:

| Row | RTX (s) | Fastest baseline (s) | Computed ratio | Output ratio | Match |
|---|---|---|---|---|---|
| robot_collision_screening / prepared_pose_flags | 0.000367 | 0.5819 (embree) | 1585.1 | 1585.07 | ✓ |
| database_analytics / prepared_db_session_sales_risk | 0.10017 | 0.06159 (embree) | 0.615 | 0.6149 | ✓ |
| service_coverage_gaps / prepared_gap_summary | 0.21513 | 0.22005 (embree) | 1.023 | 1.0229 | ✓ |
| road_hazard_screening / road_hazard_native_summary_gate | 0.18234 | 0.003571 (embree) | 0.0196 | 0.01959 | ✓ |
| hausdorff_distance / directed_threshold_prepared | 0.001217 | 2.5067 (embree) | 2059.7 | 2059.65 | ✓ |

---

## Classification Logic

**Threshold (20% speedup for candidate):** The `ratio >= 1.20` requirement for `candidate_for_separate_2ai_public_claim_review` is a meaningful bar. The 6 candidates all exceed it (ratios 1.54x to 1585x). This is conservative — a 1.05x advantage earns only `internal_only_margin_or_scale`.

**Missing-baseline penalty:** When any required non-OptiX baseline lacks a positive comparable phase, the script caps the outcome at `internal_only` even if the timed evidence is overwhelming. This fires on 3 rows with extreme ratios:

- `hausdorff_distance`: 2059x against embree, but `cpu_oracle` records `native_query: 0.0` — correctly treated as missing → `internal_only`
- `ann_candidate_search`: 95974x against embree, same cpu_oracle timing gap → `internal_only`
- `barnes_hut_force_app`: 7.3x against embree, same gap → `internal_only`

These three are the most conservative calls in the audit. Demoting 95974x evidence to `internal_only` because one oracle field is zero is strict; it is also the right call until timing is repaired.

**OptiX self-comparison exclusion:** `_baseline_rows` skips any baseline with `source_backend == "optix"`. This is verified by `segment_polygon_anyhit_rows`, which has a valid `optix_prepared_bounded_pair_rows` baseline (`source_backend: "optix"`) in the source package. That artifact is correctly absent from the timed or untimed baseline lists in the Goal978 output; the speedup comparison is made only against the cpu_python_reference and PostGIS baselines.

**`graph_analytics` / `graph_visibility_edges_gate`:** All four non-OptiX baselines have null timing → `needs_timing_baseline_repair`. This is correct. The RTX time of 1.583s is present but there is nothing valid to compare it against.

**Reject decisions:** All 6 rejected rows have ratio < 1.0 (RTX is slower). The two polygon rows (`polygon_pair_overlap_area_rows`, `polygon_set_jaccard`) show RTX roughly 2000x–4000x slower than the fastest non-OptiX baseline on the candidate-discovery phase — these are honest rejections, not close calls.

---

## Public Claim Authorization

**`public_speedup_claim_authorized`** is `False` for every row in the output JSON. **`public_speedup_claim_authorized_count`** is hardcoded to `0` at the artifact level. The boundary field reads: *"It does not authorize public speedup claims; it only selects rows for later 2-AI claim review..."*

No public RTX speedup claims are authorized by this artifact.

---

## Warnings

Five of the six candidate rows carry the sub-10ms warning:

> RTX phase is shorter than 10 ms; public wording needs larger-scale repeat evidence.

RTX phases on these rows range from 0.37 ms to 5.1 ms. Single-shot sub-millisecond measurements are dominated by timer resolution and OS jitter. The warning is correct and appropriately gates further claim review.

---

## Test Coverage

Three tests cover the key invariants:

1. **`test_audit_covers_all_rows_without_authorizing_public_claims`** — asserts row_count == 17, `public_speedup_claim_authorized_count == 0`, `candidate_count > 0`, boundary text present, every row has `public_speedup_claim_authorized == False`.

2. **`test_decisions_are_conservative_for_known_rows`** — asserts five specific classifications by (app, path_name) key, including one candidate, one reject, one needs_timing, one reject (polygon), and one internal_only with warnings.

3. **`test_cli_writes_json_and_markdown`** — end-to-end CLI test verifying JSON and markdown outputs, row count, and stdout header.

Coverage is adequate for the invariants that matter: no public claim, 17 rows, conservative known-row decisions.

---

## Minor Observations (non-blocking)

**Phase key naming:** `optix_query` and `optix_query_sec` appear in `COMPARABLE_PHASE_KEYS` and are used to read timing from non-OptiX baseline artifacts (e.g., embree and CPU baselines for `service_coverage_gaps`). The name reflects the field name chosen in those upstream baseline JSON files, not that the measurement was taken with OptiX. Goal978 correctly excludes baselines by `source_backend`, not by field name. This is an upstream naming convention issue and not a Goal978 defect.

**`cpu_oracle` zero-timing for hausdorff/ann/barnes_hut:** These cpu_oracle baselines record `native_query: 0.0`. The zero may indicate the oracle performs its work in the `input_build` phase rather than a separate query phase, or that timing was not captured. Goal978 treats 0.0 as missing (not a positive number), which is correct and conservative. The root cause should be tracked as an upstream baseline repair item.

---

## Summary

The script logic, output JSON, and output markdown are mutually consistent. Arithmetic is correct on all verified rows. Classifications are conservative: the 20% threshold, the missing-timing penalty, and the OptiX self-exclusion rule all push borderline cases toward `internal_only` or `needs_timing_baseline_repair` rather than `candidate`. No public RTX speedup claim is authorized. The boundary text is honest.

**ACCEPT.**
