# Goal979 Claude Review

Date: 2026-04-26

Verdict: **ACCEPT**

---

## Scope

This review covers:

1. Whether Goal979's `native_query` timing repair for Hausdorff, ANN, and Barnes-Hut is methodologically correct.
2. Whether the regenerated Goal978 classifications are conservative given the repaired timings.
3. Whether public RTX speedup claims remain unauthorized after both goals complete.

---

## Goal979 Timing Repair

**Methodology is sound.**

The repair script reads each target baseline artifact, extracts the original benchmark scale parameters (`copies` / `body_count` / `iterations`), re-runs the identical CPU oracle computation at identical scale using `time.perf_counter()` with the same repeat count, and stores the median elapsed time as `phase_seconds.native_query`. The old value was `0.0` in all three cases (a deferred measurement that was never filled in). The key correctness check is `summary_matches_existing`, which compares the re-run output to the summary already recorded in the artifact.

| App | Old native_query | New native_query | Summary Match |
| --- | ---: | ---: | --- |
| `hausdorff_distance` | 0.0 | 22 μs | True |
| `ann_candidate_search` | 0.0 | 3.67 ms | True |
| `barnes_hut_force_app` | 0.0 | 699 μs | True |

`summary_matches_existing: True` for all three confirms that the rerun function, scale, and parameters exactly replicate the original oracle semantics. No correctness regression was introduced.

**Boundary compliance is correct.** The `boundary` field in the report is narrow and accurate: the goal only repairs zero CPU oracle timing in deferred decision baselines; it does not collect cloud data, repair graph same-scale timing, or authorize public RTX speedup claims. The `write: True` result in the JSON report confirms the repairs were committed back to the Goal835 baseline artifacts, and the test suite (`goal979_deferred_cpu_timing_repair_test.py`) verifies all three on-disk artifacts now have `native_query > 0`, `goal979_timing_repair` validation keys, and `authorizes_public_speedup_claim: False`.

**Minor note:** `_time_hausdorff` hardcodes `radius=0.4` in the reconstructed summary dict. This is correct for the known baseline but would silently produce `summary_matches_existing: False` if the radius ever differed, which would block the repair from reporting status `ok`. The True outcome confirms the constant is right.

---

## Goal978 Post-Repair Classifications

**All three repaired rows are classified correctly and conservatively.**

### Hausdorff — `reject_current_public_speedup_claim`

CPU oracle `native_query` = 22 μs; RTX phase = 1.22 ms. Ratio = 0.018 — RTX is roughly **54× slower** than the CPU oracle at this scale. Rejection is unambiguous and correct. The pre-repair state (zero timing → untimed baseline) was already blocking a claim; the post-repair state is strictly harder to claim from.

### Barnes-Hut — `reject_current_public_speedup_claim`

CPU oracle `native_query` = 699 μs; RTX phase = 1.54 ms. Ratio = 0.454 — RTX is **~2.2× slower**. Rejection is correct. Again, post-repair is more conservative than pre-repair.

### ANN — `candidate_for_separate_2ai_public_claim_review`

CPU oracle `native_query` = 3.67 ms; RTX phase = 0.63 ms. Ratio = 5.8 — RTX is faster, exceeding the 20% threshold. The candidate classification is correct. The RTX phase is below 10 ms, so the `warning` ("public wording needs larger-scale repeat evidence") is correctly triggered. This promotion is **not** an authorization — it only flags the row for a subsequent 2-AI claim review.

**All other 14 rows are unaffected by Goal979 and were already correctly classified.** Key checks:

- `robot_collision_screening` ratio 1585× → candidate: correct (Embree 582 ms vs RTX 0.37 ms; sub-10ms warning flagged).
- `service_coverage_gaps` ratio 1.02× → `internal_only_margin_or_scale`: correct conservative treatment at below-20% margin.
- `graph_analytics` → `needs_timing_baseline_repair`: correct; all four non-OptiX baselines have null phase_sec.
- `polygon_pair_overlap_area_rows` ratio 0.00042× and `polygon_set_jaccard` ratio 0.0036× → both rejected: RTX is thousands of times slower; correct.
- `database_analytics` both paths → rejected: RTX is slower than Embree in both cases; correct.

**Recommendation count audit:**

| Recommendation | Count | Arithmetically Correct |
| --- | ---: | --- |
| `candidate_for_separate_2ai_public_claim_review` | 7 | Yes |
| `reject_current_public_speedup_claim` | 8 | Yes |
| `internal_only_margin_or_scale` | 1 | Yes |
| `needs_timing_baseline_repair` | 1 | Yes |
| Total | 17 | Yes |

---

## Public RTX Speedup Claim Status

`public_speedup_claim_authorized_count: 0`. Every row in the Goal978 JSON has `"public_speedup_claim_authorized": false`. No claim was promoted by Goal979. The 7 candidate rows are forwarded for a separate 2-AI claim review; they are not authorized here.

The two-AI consensus document (`goal978_two_ai_consensus_2026-04-26.md`) records both Codex ACCEPT and a prior Claude ACCEPT (pre-Goal979 run) and correctly summarizes the post-repair delta: Hausdorff and Barnes-Hut are rejected; ANN is promoted to candidate. That consensus document's characterization is accurate and consistent with this review.

---

## Summary

- Goal979 repair methodology is technically correct; all three summary-match checks pass.
- Post-repair Hausdorff and Barnes-Hut rejections are correct and more conservative than before.
- Post-repair ANN candidate promotion is correct; the sub-10ms warning is properly emitted.
- All 17 Goal978 rows have `public_speedup_claim_authorized: false`; zero public claims are authorized.
- No boundary violations in either goal.

**ACCEPT**
