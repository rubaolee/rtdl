# Goal1936 Claude Review - Goal1933/1935 Large-Scale v2 Pod Performance Packet

Reviewer: Claude (independent)
Date: 2026-05-13
Artifacts reviewed: see Primary Files list in handoff

---

## Overall Verdict: `accept-with-boundary`

The packet is internally sound and all five release-boundary categories are correctly maintained. Three methodological caveats noted below; none are blockers, but they should be recorded against future re-runs and Gemini's review missed two of them.

---

## Q1 — Fixed-Radius Family at 524288 × 524288 Scale

**Verdict: `accept-with-boundary`**

The data in `fixed_radius_524288.json` unambiguously supports the narrow claim. All 12 rows pass parity (`counts_match: true`, `summary_match: true`), all v1.8 medians are in the 1.14 s – 1.87 s range, and all v2 medians are in the 0.000444 s – 0.00216 s range, yielding ratios of 0.000444x – 0.001153x (~0.04 % – 0.12 % of v1.8 prepared time). The claim scope is correctly bounded to `partner_owned_fixed_radius_count_threshold_columns` and the report explicitly names the excluded outputs (ranked KNN, exact Hausdorff ranking, full DBSCAN expansion, full Barnes-Hut force vectors).

**Boundary to record:** `fixed_radius_524288.json` uses `repeat: 1` for every row, so `min_s == median_s == max_s` throughout — each entry is a single-sample point estimate with no variance information. The 65536-scale companion file uses `repeat: 3` and shows variance, confirming the signal holds at smaller scale. The 3-orders-of-magnitude advantage makes the single-sample limitation a methodological note rather than a blocker, but any future re-run at 524288 scale should use at least 3 repeats to establish stable median/IQR.

---

## Q2 — Robot Collision and Segment/Polygon Any-Hit Overclaim Avoidance

**Verdict: `accept`**

Robot collision (`robot_collision_16384x1024.json`): v1.8 median 1.0 ms, v2 median 0.67 ms (CuPy) / 0.58 ms (Torch). Both values are sub-millisecond, well below the seconds-scale threshold for broad performance claims. The JSON enforces `rt_core_speedup_claim_authorized: false`, `whole_app_speedup_claim_authorized: false`, `broad_rt_core_speedup_claim_authorized: false`, `package_install_claim_authorized: false`. The report's interpretation ("not yet a seconds-scale whole-robot workload") is accurate.

Segment/polygon any-hit (`segment_anyhit_rows_4096.json`): v1.8 median 14.5 ms, v2 CuPy median 4.3 ms, Torch median 6.2 ms. All sub-second. The report correctly notes 4096 pairs is insufficient for final claims and that compact flag/count rows remain the stronger v2 story.

One provenance note (not a blocker): `segment_anyhit_rows_4096.json` carries `"goal": "Goal1856"` and `robot_collision_16384x1024.json` carries `"goal": "Goal1928"`. Both files reside in the `goal1933_large_scale_v2_pod_batch/` directory but were generated under earlier goals, not re-run in Goal1933. The report implies they are Goal1933 batch evidence without this qualification. The claim boundaries in those artifacts remain correct regardless of origin, so this is a filing/provenance note rather than an evidence quality issue.

---

## Q3 — Polygon Exact Metrics, DB Analytics, and Graph Analytics as Control Rows

**Verdict: `accept`**

**Polygon overlap / Jaccard:** Both `control_polygon_pair_overlap_8192.json` and `control_polygon_jaccard_8192.json` show `optix_candidate_discovery_sec` of 1.88 s and 1.59 s respectively, and `native_exact_continuation_sec` of 0.93 s and 1.42 s. Both carry `boundary` text stating they do not authorize full RTX speedup claims. Both carry `non_claim` fields. The report correctly describes them as control rows requiring a future partner tensor continuation before a clean v2 speedup claim is possible. Note: `optix_metadata.rt_core_accelerated: false` in both artifacts — RT cores are not active for the candidate discovery step. The report does not call this out explicitly but does not claim RT-core speedup for these rows, so no overclaim.

**DB analytics:** `one_shot_total_sec: 8.60 s`, `prepared_session_prepare_total_sec: 5.57 s`, `prepared_session_warm_query_sec.median_sec: 1.26 s`. All seconds-scale and phase-clean. The `non_claim` field explicitly excludes SQL, DBMS, and v2 partner columnar scan. One internal data anomaly: `reported_native_db_phase_totals_sec` shows all-zero aggregates (`traversal_sec: 0.0`, `exact_filter_sec: 0.0`, etc.) while the per-section `native_db_phases` blocks show non-zero values (e.g., traversal 0.20 s – 0.22 s per operation). This appears to be a totals-aggregation schema issue in the artifact, not a data quality problem — the per-section phases are the primary evidence. The report's summary numbers are sourced from the correct prepared warm-query fields and are accurate.

**Graph analytics:** `phase_seconds.native_query: 13.35 s`. `public_speedup_claim_authorized: false`. Correct. Note: `control_graph_analytics_100000.json` carries `"goal": "Goal982 graph same-scale timing repair"` and `"date": "2026-04-26"` — this is an April artifact from an earlier goal, not fresh from the May 13 pod run. The report treats it as Goal1933 evidence. The timing and correctness are unaffected, but this is a second provenance discrepancy.

---

## Q4 — Gemini Goal1935 Review as Distinct External Review

**Verdict: `accept-with-boundary`**

The Gemini review is structurally valid as an independent assessment: it identifies and cites specific artifact values, it does not upgrade any claim beyond the report's scope, and it consistently recognizes control rows as control rows. All four of its verdicts are `accept` and each is grounded in the JSON artifact fields.

**Caveats Gemini missed:**

1. **Single-repeat timing at 524288 scale.** Gemini correctly notes the numerical ranges in `fixed_radius_524288.json` but does not observe that `min_s == median_s == max_s` for every row, which is the signature of `repeat: 1`. This is the most substantive gap in the Gemini review.

2. **Artifact provenance discrepancies.** Gemini accepts `robot_collision_16384x1024.json` and `segment_anyhit_rows_4096.json` as Goal1933 batch evidence without noting that their internal `goal` fields point to Goal1928 and Goal1856 respectively. Similarly, `control_graph_analytics_100000.json` is a Goal982 / April 2026 artifact. None of these invalidate the claims, but an external review that cited provenance would be stronger.

3. **DB totals aggregation anomaly.** Gemini references the DB artifact's claim boundary fields accurately but does not note the all-zero `reported_native_db_phase_totals_sec` aggregates.

4. **`rt_core_accelerated: false` for polygon overlap.** Gemini accepts the polygon control classification correctly but does not note that RT cores are inactive for that workload, which is an additional reason the artifact is a control row rather than an acceleration row.

None of these gaps invalidate Gemini's review or change its verdicts. The review is acceptable as a distinct external review for this packet, subject to the single-repeat boundary being carried forward.

---

## Q5 — Release Boundaries

**Verdict: `accept`**

The report's "What We Learned" section contains an explicit negative-authorization statement:

> "This packet improves the evidence quality, but it does not authorize v2.0 release, whole-app speedup wording, arbitrary PyTorch/CuPy acceleration, or package-install claims."

The report status line reads `large-scale-evidence-collected-release-still-blocked`. All five boundary categories are covered:

| Boundary | Report text | JSON enforcement |
| --- | --- | --- |
| v2.0 release authorization | explicit deny in "What We Learned" | `v2_0_release_authorized: false` in robot, segment, fixed-radius JSONs |
| Broad RT-core speedup | not claimed anywhere | `broad_rt_core_speedup_claim_authorized: false` in robot, segment; `rt_core_accelerated: false` in polygon JSONs |
| Whole-app speedup | explicit deny | `whole_app_speedup_claim_authorized: false` in all quantitative JSONs |
| Arbitrary PyTorch/CuPy acceleration | explicit deny in "What We Learned" | `partner_owned_fixed_radius_count_threshold_columns` output contract limits scope |
| Package-install claim | explicit deny | `package_install_claim_authorized: false` in robot, segment JSONs |

Minor incompleteness: `fixed_radius_524288.json` and `fixed_radius_65536.json` `claim_boundary` objects contain only `v2_0_release_authorized` and `whole_app_speedup_claim_authorized`, omitting `broad_rt_core_speedup_claim_authorized` and `package_install_claim_authorized`. The report's text covers these cases and the narrowness of the `output_contract` field in every fixed-radius row already precludes broader claims. Not a blocker.

---

## Summary of Blockers

None. The packet is accepted with the following boundary notes to carry forward:

1. **Fixed-radius 524288 re-run should use `repeat >= 3`** to replace single-sample point estimates with variance-backed medians.
2. **Artifact provenance in `goal1933_large_scale_v2_pod_batch/`** should be clarified: robot collision (Goal1928), segment/anyhit (Goal1856), and graph analytics (Goal982) are reused artifacts from earlier goals, not freshly run in Goal1933. Future packets should re-run these at Goal1933 scale or explicitly label them as archived baselines.
3. **DB phase totals schema issue** (`reported_native_db_phase_totals_sec` all-zero aggregates) should be investigated before the next DB evidence generation; it does not affect the current summary numbers.
4. **Gemini review** is acceptable as a distinct external review but should record the single-repeat caveat in a follow-up annotation.
