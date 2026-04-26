# Goal1005 External Review — Claude (claude-sonnet-4-6)

**Date:** 2026-04-26
**Verdict: ACCEPT**

---

## Summary

Goal1005 correctly replaces the stale Goal978/Goal969-derived audit with one based directly on the final Goal1003 RTX A5000 v2 artifact bundle. All four review questions are satisfied. No blocker found.

---

## Review Question 1 — Does Goal1005 read the final A5000 v2 artifacts?

**PASS.**

The script hard-codes paths to:
- `docs/reports/cloud_2026_04_26/goal1003_rtx_a5000_final_merged_summary_2026-04-26.json`
- `docs/reports/cloud_2026_04_26/goal1003_rtx_a5000_artifacts_with_report_2026-04-26-v2.tgz`

The `build_audit()` function verifies provenance via a five-condition gate:
1. `summary.status == "ok"`
2. `failed_count == 0`
3. `entry_count == 17`
4. `dry_run is False`
5. `"NVIDIA RTX A5000"` present in `nvidia_smi`

All five conditions are satisfied in the merged summary (`source_is_final_a5000_v2: true`, `source_commit: 914122ecd2f2c73f6a51ec2d5b04ca3d575d5681`). The script imports helper constants and baseline-package logic from Goal978/Goal971 but does not read Goal969 group report files for RTX timing — RTX phase data is extracted live from the v2 bundle via `_load_bundle_json`. The test enforces the exact commit hash.

---

## Review Question 2 — Are phase extractions reasonable?

**PASS.** All eight app families are handled correctly by the `_rtx_phase_seconds` cascade:

| Family | Key extracted | Reasoning |
|---|---|---|
| Robot | `phases.prepared_pose_flags_warm_query_sec.median_sec` | Outer artifact `phases` dict; test confirms 0.000493 s |
| Fixed-radius (outlier, dbscan) | `selected.prepared_optix_warm_query_sec.median_sec` | Per-app result via `_find_result`; shared artifact correctly differentiated |
| DB compact summaries | `selected.prepared_session_warm_query_sec.median_sec` | Session result object; stdout_tail confirms 0.103 s and 0.144 s |
| Spatial summaries | `scenario.timings_sec.optix_query` | Scenario envelope for summary profiler |
| Prepared-decision paths | `scenario.timings_sec.optix_query_sec` | Same envelope; facility, Hausdorff, ANN, Barnes-Hut |
| Segment/polygon | `timings_sec.optix_query_sec` | Top-level timings dict in road-hazard and segment-polygon artifacts |
| Graph | `records.optix_visibility_anyhit.sec` | Preferred-label lookup; test confirms 2.584 s |
| Polygon native-assisted | `phases.optix_candidate_discovery_sec` | Candidate-discovery sub-phase; matches stated claim scope |

The cascade is ordered most-specific-first with a safe `("unavailable", None)` terminal. No phase conflation was found.

One minor concern: `_find_result` falls back to `results[0]` when no app-label match is found in the list. This is safe for the current bundle (the DB artifacts contain a single-item results list) but could silently pick a wrong result for a future multi-app artifact that lacks app labels. Not a blocker; worth noting for future hardening.

---

## Review Question 3 — Are recommendations conservative?

**PASS.**

**8 REJECTS** (ratio < 1.0 — RTX slower than fastest same-semantics baseline):

| App / Path | RTX (s) | Fastest baseline (s) | Ratio |
|---|---:|---:|---:|
| database_analytics / prepared_db_session_sales_risk | 0.1034 | 0.0616 embree | 0.596 |
| database_analytics / prepared_db_session_regional_dashboard | 0.1440 | 0.1272 embree | 0.884 |
| road_hazard_screening / road_hazard_native_summary_gate | 0.1720 | 0.00357 embree | 0.021 |
| graph_analytics / graph_visibility_edges_gate | 2.584 | 0.567 embree | 0.219 |
| hausdorff_distance / directed_threshold_prepared | 0.001364 | 0.0000225 cpu | 0.016 |
| barnes_hut_force_app / node_coverage_prepared | 0.004754 | 0.000699 cpu | 0.147 |
| polygon_pair_overlap_area_rows / polygon_pair_overlap_optix_native_assisted_phase_gate | 10.053 | 0.00147 postgis | 0.000146 |
| polygon_set_jaccard / polygon_set_jaccard_optix_native_assisted_phase_gate | 4.153 | 0.01321 embree | 0.003 |

All eight are correctly rejected on current evidence.

**1 INTERNAL-ONLY** (ratio 1.0–1.20, below candidate threshold):
- `event_hotspot_screening / prepared_count_summary`: ratio 1.011. RTX is marginally faster than embree (0.2539 s vs 0.2566 s) but the margin does not clear the 20% threshold. Correctly held at `internal_only_margin_or_scale`.

**8 CANDIDATES** (ratio ≥ 1.20, complete baselines, no authorized claim):
- All 8 have `public_speedup_claim_authorized: false`.
- Five of eight have RTX phases < 10 ms and carry the warning: "RTX phase is shorter than 10 ms; public wording needs larger-scale repeat evidence." This is conservative and appropriate.
- The robot path (ratio 1180x) and facility path (ratio 22.8x) are the strongest candidates, both carrying the sub-10 ms warning.
- The 20% threshold (`ratio >= 1.20`) as the candidacy gate is the right conservatism level: it screens out noise (event_hotspot passes the 1.0 floor but correctly fails the 1.20 gate).

The classification logic in `_classify` is correctly conditioned on both `artifact_status == "ok"` and `baseline_complete_for_speedup_review` before issuing any candidate or reject verdict. An incomplete or failed artifact yields `not_ready`, which is more conservative than a rejection.

---

## Review Question 4 — Does the report preserve the no-public-speedup boundary?

**PASS.**

- `public_speedup_claim_authorized_count: 0` hard-coded in `build_audit()` output.
- Every row sets `"public_speedup_claim_authorized": False` unconditionally.
- The `boundary` key is present in both the JSON report and repeated twice in the Markdown: "It does not authorize public speedup claims; it only identifies rows that may deserve later 2-AI public-claim review or rows that should be rejected/kept internal under current evidence."
- The test `test_audit_uses_final_a5000_v2_artifacts_without_authorizing_claims` asserts `payload["public_speedup_claim_authorized_count"] == 0` and checks every row's `public_speedup_claim_authorized` field.
- The `main()` exit code is `0` only when `source_is_final_a5000_v2` is `True`, so a non-A5000 run cannot silently pass.

The no-public-speedup boundary is intact and machine-enforced.

---

## Minor Non-Blocking Findings

1. **Unused import**: `_comparable_phase_seconds` is imported from `goal978_rtx_speedup_claim_candidate_audit` but never called. Cosmetic.
2. **`_find_result` fallback**: If a future artifact's `results` list has no entry with a matching `app` label, the function silently returns `results[0]`. Currently validated by test values and counts; consider adding an explicit error for the `len(results) > 1` / no-match case in future work.
3. **`dbscan_clustering` shares artifact with `outlier_detection`**: Both reference `goal759_outlier_dbscan_fixed_radius_rtx.json`. The current implementation correctly differentiates via `_find_result` (confirmed by different extracted phase values), but the shared-artifact pattern is worth documenting.

---

## Final Verdict

**ACCEPT.**

Goal1005 reads the correct final A5000 v2 artifacts, extracts phases cleanly across all eight app families, produces conservative recommendations with a hard `public_speedup_claim_authorized: False` on every row, and does not authorize any public speedup claims. The audit is fit for its stated purpose: identifying candidates for later 2-AI review and blocking premature public claims.
