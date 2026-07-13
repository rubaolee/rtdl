# Review of Goal4949: RayJoin Hot-Path Remeasure

- **Date:** 2026-07-04
- **Reviewer:** Antigravity (AI Coding Assistant)
- **Verdict:** `approve_goal4949_measurement_current_layer2_helper_not_promoted`

---

## Verdict Summary

The measurement details and artifact data in [goal4949_rayjoin_hot_path_remeasure_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4949_rayjoin_hot_path_remeasure_2026-07-04.md) and [goal4949_rayjoin_hot_path_remeasure_artifact_2026-07-04.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4949_rayjoin_hot_path_remeasure_artifact_2026-07-04.json) are approved with the verdict **`approve_goal4949_measurement_current_layer2_helper_not_promoted`**.

The remeasurement succeeded in running a real public-sample workload under strict byte-equality validation, and correctly concluded that the current Numba-based application-layer helper is a performance regression and must be rejected rather than promoted. Furthermore, no broad or unauthorized performance claims are made or authorized.

---

## Answers to Review Questions

### 1. Did Goal4949 use a real RayJoin Section 5.7 public-sample workload rather than a toy connector probe?
**Yes.** Goal4949 executed the actual baseline `section57_overlay.py` and the Numba variant `section57_overlay_numba.py` using the real RayJoin public County x Soil datasets (`br_county_clean_25_odyssey_final.txt` and `br_soil_ascii_odyssey_final.txt`). This represents a real end-to-end hot-path workload rather than the synthetic/toy operators used in Goal4947/4948.

### 2. Do the artifacts prove both baseline and Numba variant remained byte-equal to the author answer?
**Yes.** The JSON artifact confirms that both runs achieved byte-equality (`baseline_byte_equal: true` and `numba_byte_equal: true`) against the reference author answer (`br_countyXbr_soil_answer.txt`), yielding the correct SHA256 checksum:
`464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`

### 3. Is the conclusion correct that the current Numba app-layer helper is not a performance win?
**Yes.** The data shows a clear performance degradation when using the current Numba wrapper path:
* **First Full Run:** Baseline elapsed time was `6.784s` vs Numba variant elapsed time of `8.601s` (a **26.8% slowdown**).
* **Hot Rerun:** Baseline elapsed time was `6.305s` vs Numba variant elapsed time of `8.034s` (a **27.4% slowdown**).

The current implementation is therefore not a performance win.

### 4. Does the phase table justify saying prepared-hot PIP traversal is not the bottleneck on this sample?
**Yes.** The phase timings for vertex-in-polygon (PIP) traversal are:
* **Baseline:** `vertex_pip_map0_in_map1_sec` (0.0125s) + `vertex_pip_map1_in_map0_sec` (0.0077s) = **0.0202s** total.
* **Numba:** `vertex_pip_map0_in_map1_sec` (0.0120s) + `vertex_pip_map1_in_map0_sec` (0.0078s) = **0.0198s** total.

Out of a total execution time of over 6 seconds, PIP traversal consumes less than 0.33% of the budget. It is not the performance bottleneck on this public sample.

### 5. Does the evidence justify rejecting the current Numba writer path as an optimization candidate?
**Yes.** The Numba writer variant is significantly slower than the baseline (taking `4.237s - 4.521s` compared to the baseline's `2.063s - 2.615s`).
Looking at the sub-phase timings, the overhead comes from Python-side formatting and materialization:
* `path_split_materialize_map0_sec`: 1.356s
* `path_split_materialize_map1_sec`: 1.039s
* `path_split_format_map0_sec`: 0.751s
* `path_split_format_map1_sec`: 0.610s
* `bulk_writelines_sec`: 4.163s

This confirms that the Numba writer path creates extensive materialization and serialization overhead, justifying its rejection as an optimization candidate.

### 6. Is it correct that the next Layer 2 target, if continued, must be reprojection/sort rather than demo operators or the current writer wrapper?
**Yes.** Reprojection (`intersection_reprojection_sec` ~0.73–0.75s) and sorting (`sort_map0_sec` + `sort_map1_sec` ~0.80s) consume ~1.5s total. This represents the next major candidate for optimizations since PIP traversal is already optimized. Any future Layer 2 work must target these phases directly with native numeric continuations, and avoid demo operators or the rejected writer wrapper.

### 7. Is the report careful not to claim broad RayJoin / whole-app / full Section 5.7 speedup?
**Yes.** Under **"Authorized Claim"**, the report explicitly restricts claims to this specific public sample and clearly lists what is **Not authorized**:
* No broad RayJoin speedup claim.
* No whole-app RTDL speedup claim.
* No claim that Layer 1/2 has moved the RayJoin hot path yet.
* No claim that current Numba writer assembly should be kept as an optimized path.
* No full eight-pair Section 5.7 claim.

### 8. Should Goal4949 close with label `completed_measurement__current_layer2_helper_not_performance_win__next_target_reprojection_sort_or_layer3`?
**Yes.** This label accurately summarizes the results (the measurement is complete, the helper is not a win, and the next target is identified).

---

## Conclusion & Action Items

* **Verdict:** Approved.
* **Next Steps:**
  1. Record the exit label `completed_measurement__current_layer2_helper_not_performance_win__next_target_reprojection_sort_or_layer3`.
  2. Reject promotion of the current Numba writer/overlay wrapper.
  3. Re-orient future optimization efforts towards reprojection (`intersection_reprojection_sec`) and sorting (`sort_map*_sec`) using generic numeric continuations.
