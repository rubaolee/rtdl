# Goal983 Claude Review

**Date:** 2026-04-26
**Reviewer:** Claude (claude-sonnet-4-6)
**Source documents:**
- `docs/reports/goal983_post_goal982_rtx_optimization_queue_2026-04-26.md`
- `docs/reports/goal978_rtx_speedup_claim_candidate_audit_2026-04-26.json`

---

## Verdict: ACCEPT

---

## Checks Performed

### 1. Count Parity — PASS

Every count in Goal983 matches the `recommendation_counts` fields in the Goal978 JSON exactly:

| Category | Goal978 JSON | Goal983 MD |
|---|---|---|
| `public_speedup_claim_authorized_count` | 0 | 0 |
| `candidate_for_separate_2ai_public_claim_review` | 7 | 7 |
| `internal_only_margin_or_scale` | 1 | 1 |
| `reject_current_public_speedup_claim` | 9 | 9 |
| `needs_timing_repair_count` | 0 | 0 |
| Graph-correctness-repair | 0 (implicit) | 0 |
| **Total rows** | **17** | **7 + 1 + 9 = 17** |

### 2. Candidate Ratios — PASS

All seven candidate rows were spot-checked against `fastest_ratio_baseline_over_rtx` in the JSON. Each value in the Goal983 table is a correct 6-decimal truncation/round of the JSON value:

| App | JSON ratio | Goal983 ratio | OK? |
|---|---|---|---|
| `robot_collision_screening` | 1585.0663680... | 1585.066368 | ✓ |
| `outlier_detection` | 5.3258159... | 5.325816 | ✓ |
| `dbscan_clustering` | 29.1280636... | 29.128064 | ✓ |
| `facility_knn_assignment` | 121.9805019... | 121.980502 | ✓ |
| `segment_polygon_hitcount` | 1.5362809... | 1.536281 | ✓ |
| `segment_polygon_anyhit_rows` | 3.9304700... | 3.930470 | ✓ |
| `ann_candidate_search` | 5.8055033... | 5.805503 | ✓ |

### 3. Rejected Row Ratios — PASS

All nine rejected rows were verified against the JSON:

| App / path | JSON ratio | Goal983 ratio | OK? |
|---|---|---|---|
| `database_analytics / sales_risk` | 0.6148809... | 0.614881 | ✓ |
| `database_analytics / regional_dashboard` | 0.9382990... | 0.938299 | ✓ |
| `event_hotspot_screening` | 0.7868617... | 0.786862 | ✓ |
| `road_hazard_screening` | 0.0195864... | 0.019586 | ✓ |
| `graph_analytics` | 0.3583056... | 0.358306 | ✓ |
| `hausdorff_distance` | 0.0184524... | 0.018452 | ✓ |
| `barnes_hut_force_app` | 0.4539075... | 0.453908 | ✓ |
| `polygon_pair_overlap_area_rows` | 0.0004188... | 0.000419 | ✓ |
| `polygon_set_jaccard` | 0.0036272... | 0.003627 | ✓ |

### 4. Public Speedup Overclaim Check — PASS

Goal983 makes no public speedup claims anywhere in the document. It explicitly states:
- "Public RTX speedup claims authorized: 0"
- Candidates are labeled "not public claims" and require "separate larger-scale repeat evidence and 2-AI claim review before promotion"
- Rejected rows are described as requiring "new implementation or performance evidence" before entering speedup review

No candidate ratio (however large, e.g. 1585× for `robot_collision_screening`) is presented as a public speedup figure. Claim scopes and non-claim language from the Goal978 JSON are respected implicitly throughout.

### 5. Coding Priority Conservatism — PASS

The four-item priority list is appropriately conservative:

- **`graph_analytics`** (ratio 0.358): Correctness is repaired per Goal978; calling for profiling rather than a claim is correct.
- **`road_hazard_screening`** (ratio 0.020): The 51× underperformance against Embree is a severe rejection; directing attention to setup/transfer overhead is a reasonable diagnosis.
- **`polygon_pair_overlap_area_rows` and `polygon_set_jaccard`** (ratios 0.000419 and 0.003627): RTX paths run ~3.5 s and ~3.6 s vs. sub-millisecond baselines. Flagging these for redesign before any marketing is correct.
- **`database_analytics` and `event_hotspot_screening`** (ratios 0.615–0.938): Near-miss rejection; kernel-overhead investigation is the right level of caution.

The seven candidates are explicitly kept separate from the coding queue ("they need claim-review scale hardening, not immediate broad redesign"), which avoids conflating performance work with promotion to public claims.

Note: `hausdorff_distance` (ratio 0.018) has severity comparable to `road_hazard_screening` but is not listed as a top coding priority. This omission is not a block; the CPU oracle baseline (22.5 µs) suggests the workload may be too small for RTX to amortize launch overhead at current scale, which might make it lower-leverage to redesign than the polygon or road-hazard paths.

---

## Minor Observation (Non-Blocking)

The `service_coverage_gaps / prepared_gap_summary` row (internal_only_margin_or_scale, ratio 1.023) is correctly counted as 1 internal-only row but does not appear in either the candidate or rejected table. A reader verifying the total row count (7 + 1 + 9 = 17) must infer which row fills the internal-only slot from the Goal978 JSON. Recommend adding a one-row "Internal-Only Rows" table in a future revision for completeness, but this does not affect correctness of the current document.

---

## Summary

Goal983 accurately reflects the Goal978 audit. All category counts are exact. All tabled ratios are numerically verified against the JSON source. No public speedup claims are made or implied. The next coding priority list is conservative, operationally concrete, and does not conflate performance improvement work with claim promotion. The document is ready to serve as the post-Goal982 optimization queue.
