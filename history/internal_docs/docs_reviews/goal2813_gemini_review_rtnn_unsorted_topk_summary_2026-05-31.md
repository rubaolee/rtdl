**Gemini Review of Goal2813 RTNN Unsorted Top-K Summary Path**

**Verdict:** accept-with-boundary

**Summary:**
Goal2813 successfully implements a generic optimization for fixed-radius 3D ranked-summary aggregates by introducing an unsorted bounded top-k helper for summary-only float32 kernels. This change avoids the unnecessary cost of maintaining sorted order when only aggregate summary values (count, nearest/kth ID checksums, distance sum) are required. The implementation correctly maintains the separation of sorted row-output paths and unsorted summary-only paths. The clean pod artifacts validate the changes, showing correct provenance, median timing, zero `upload_sec`, and exact aggregate agreement with the CuPy grid opponent. Performance analysis confirms significant speedups for RTDL over Goal2812 in clustered (3.37x and 3.19x) and shell (2.58x and 7.56x) distributions, with mixed results for uniform distributions. The report meticulously adheres to the established claim boundaries, avoiding any overclaims. The implementation appears robust, and the documentation is clear and accurate.

---

**Review Questions & Answers:**

1.  **Confirm whether Goal2813 is a generic summary-only fixed-radius top-k optimization, not an RTNN-specific engine customization.**
    *   **Confirmed.** The Goal2813 report explicitly states under "Interpretation": "The unsorted bounded top-k path is a reusable generic optimization because it is driven by the requested output contract, not by an application name." The "Code Changes" section also points to `src/native/optix/rtdl_optix_core.cpp` for the generic `frn_ranked_insert_unsorted_f32` function and `fixed_radius_neighbors_3d_grid_ranked_summary_f32` kernel. The `claim_boundary` in the report and JSON artifacts explicitly states `"native_engine_customization": false`.

2.  **Confirm whether sorted row-output paths remain conceptually separate from the unsorted summary-only path.**
    *   **Confirmed.** The Goal2813 report states, "The sorted helper remains available for row-output paths. Goal2813 only changes the summary-only float32 kernels." Examination of `src/native/optix/rtdl_optix_core.cpp` reveals both `frn_ranked_insert` (sorted) and `frn_ranked_insert_unsorted_f32` (unsorted) functions, indicating separate implementations for different output contracts. The `fixed_radius_neighbors_3d_grid_ranked_rows` kernel still uses the sorted approach.

3.  **Confirm whether the clean pod artifacts are valid: source commit `73270996cdeaff24cc7f90c7773818cccec73a8b`, empty `source_dirty`, status pass, median timing, `upload_sec: 0.0`, and exact aggregate agreement with the CuPy grid opponent.**
    *   **Confirmed.**
        *   **Source Commit:** Both `rtnn_unsorted_topk_median_f32_32768.json` and `rtnn_unsorted_topk_median_f32_65536.json` (and the report) show `source_commit: "73270996cdeaff24cc7f90c7773818cccec73a8b"`.
        *   **Empty `source_dirty`:** Both JSON artifacts and the report show `source_dirty: []`.
        *   **Status Pass:** Both JSON artifacts and the report show `status: "pass"`.
        *   **Median Timing:** All `rtdl_elapsed_statistic` values in the JSON artifacts are "median".
        *   **`upload_sec: 0.0`:** All `rtdl_phase_summary.upload_sec` values in the JSON artifacts are `0.0`.
        *   **Exact Aggregate Agreement:** Both JSON artifacts show `ranked_aggregate_matches_cupy_grid: true`.

4.  **Confirm whether the performance summary is accurate:**
    *   Goal2813 improves RTDL over Goal2812 by about 3.37x on 32K clustered, 2.58x on 32K shell, 2.27x on 65K uniform, 3.19x on 65K clustered, and 7.56x on 65K shell.
    *   RTDL is faster than the CuPy grid opponent in 4 of 6 controlled rows (both clustered and both shell rows), but still slower on both uniform rows.
    *   **Confirmed.**
        *   **RTDL Improvement over Goal2812:**
            *   32K uniform: 0.000135981 (G2812) / 0.000145571 (G2813) = 0.934x (Slight regression, but the report correctly lists `0.934x`)
            *   32K clustered: 0.016044247 (G2812) / 0.004760874 (G2813) = 3.370x. Matches report.
            *   32K shell: 0.000390197 (G2812) / 0.000151183 (G2813) = 2.581x. Matches report.
            *   65K uniform: 0.000419207 (G2812) / 0.000184891 (G2813) = 2.267x. Matches report.
            *   65K clustered: 0.063771570 (G2812) / 0.019996277 (G2813) = 3.189x. Matches report.
            *   65K shell: 0.002772068 (G2812) / 0.000366806 (G2813) = 7.557x. Matches report.
        *   **RTDL vs. CuPy grid opponent:** The report states: "RTDL is faster than the CuPy grid opponent in 4 of 6 rows under this controlled same-contract benchmark: both clustered rows and both shell rows. The uniform rows are still mixed: 32K uniform remains slower, and 65K uniform is closer but still below parity."
            *   32K uniform: `cupy_grid_over_rtdl_elapsed_ratio` is 0.575x (< 1, so CuPy is faster). Correctly identified as slower.
            *   32K clustered: `cupy_grid_over_rtdl_elapsed_ratio` is 2.514x (> 1, so RTDL is faster). Correctly identified as faster.
            *   32K shell: `cupy_grid_over_rtdl_elapsed_ratio` is 1.746x (> 1, so RTDL is faster). Correctly identified as faster.
            *   65K uniform: `cupy_grid_over_rtdl_elapsed_ratio` is 0.863x (< 1, so CuPy is faster). Correctly identified as slower.
            *   65K clustered: `cupy_grid_over_rtdl_elapsed_ratio` is 2.360x (> 1, so RTDL is faster). Correctly identified as faster.
            *   65K shell: `cupy_grid_over_rtdl_elapsed_ratio` is 7.419x (> 1, so RTDL is faster). Correctly identified as faster.
            *   The performance summary is accurate.

5.  **Confirm whether the report keeps claim boundaries closed: no public RTDL-beats-CuPy claim, no RTDL-beats-RTNN-paper claim, no paper reproduction claim, no broad RT-core claim, and no whole-app speedup claim.**
    *   **Confirmed.** The "Claim Boundary" section in `docs/reports/goal2813_rtnn_unsorted_topk_summary_2026-05-31.md` lists all these claims as "not authorized". The `claim_boundary` fields in the JSON artifacts are all set to `false` for these specific claims. The test file `tests/goal2813_rtnn_unsorted_topk_summary_test.py` also explicitly checks for these boundaries.

6.  **Call out any stale wording, overclaim, missing evidence, artifact/test mismatch, determinism risk, or app-agnosticity risk.**
    *   No issues found. The wording is precise, no overclaims are present, all evidence is provided and consistent, and app-agnosticity is explicitly addressed and seems to be maintained. The "Clean Pod Evidence" includes checks for determinism (`source_dirty: []`) and passes.
