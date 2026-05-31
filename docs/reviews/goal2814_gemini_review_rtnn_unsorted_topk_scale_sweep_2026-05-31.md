**Gemini Review of Goal2814 RTNN Unsorted Top-K Scale Sweep**

**Date:** 2026-05-31

**Verdict:** accept-with-boundary

**Summary:**
Goal2814 successfully extends the performance evaluation of the Goal2813 unsorted bounded top-k summary path to larger scales (131K and 262K points). This study confirms that the previously observed weakness of RTDL on small uniform rows was indeed due to small-row overhead rather than a fundamental primitive design flaw. At larger scales, RTDL now outperforms the CuPy grid opponent across all tested distributions (uniform, clustered, and shell), demonstrating excellent scalability of the generic fixed-radius ranked-summary primitive. All artifacts are valid, and the timing data is accurate. The report maintains strict adherence to claim boundaries, preventing any premature public claims. The interpretation of the results is fair and proposes a logical direction for future optimizations focused on reducing small-row overhead rather than application-specific shortcuts.

---

**Review Questions & Answers:**

1.  **Confirm whether Goal2814 is correctly scoped as scale evidence only, not a new implementation goal.**
    *   **Confirmed.** The report explicitly states: "Goal2814 records a larger same-contract RTNN scale sweep for the Goal2813 unsorted bounded top-k summary path" and "Goal2814 does not add new code. It clarifies where the Goal2813 primitive is strong and where the remaining overhead lives." This clearly positions Goal2814 as an evidence-gathering and clarification goal, not an implementation one.

2.  **Confirm whether the artifacts are valid: source commit `8db92cafaf8b054dcaed67a40b9fa6ca31828066`, empty `source_dirty`, status pass, median timing, query-resident `upload_sec: 0.0`, and exact aggregate agreement with the CuPy grid opponent.**
    *   **Confirmed.**
        *   **Source Commit:** The report and both JSON artifacts (`rtnn_unsorted_topk_scale_131072.json`, `rtnn_unsorted_topk_scale_262144.json`) consistently show `source_commit: "8db92cafaf8b054dcaed67a40b9fa6ca31828066"`. The test file also confirms this `EXPECTED_COMMIT`.
        *   **Empty `source_dirty`:** All artifacts and the report indicate `source_dirty: []`.
        *   **Status Pass:** All artifacts and the report show `status: "pass"`.
        *   **Median Timing:** The `rtdl_elapsed_statistic` and `cupy_grid_elapsed_statistic` in both JSON artifacts are consistently "median".
        *   **`upload_sec: 0.0`:** The `rtdl_phase_summary.upload_sec` in all relevant rows of both JSON artifacts is `0.0`.
        *   **Exact Aggregate Agreement:** All rows in both JSON artifacts show `ranked_aggregate_matches_cupy_grid: true`.
        *   The test file `tests/goal2814_rtnn_unsorted_topk_scale_sweep_test.py` programmatically verifies all these conditions.

3.  **Confirm whether the timing table is accurate:**
    *   **Confirmed.** A direct comparison of the "Median Timing Results" table in `docs/reports/goal2814_rtnn_unsorted_topk_scale_sweep_2026-05-31.md` with the corresponding `rtdl_elapsed_sec`, `cupy_grid_elapsed_sec`, and `cupy_grid_over_rtdl_elapsed_ratio` values in `rtnn_unsorted_topk_scale_131072.json` and `rtnn_unsorted_topk_scale_262144.json` shows exact agreement up to the precision reported. All listed ratios and absolute times match the underlying JSON data.

4.  **Confirm whether the interpretation is fair: the earlier small uniform rows were likely limited by fixed small-row overhead, while the generic primitive scales well at larger row counts.**
    *   **Confirmed.** The "Interpretation" section of the report provides a well-reasoned explanation: "At 32K and 65K points, uniform rows are sparse enough that kernel launch, native call overhead, aggregate-buffer setup, and scalar result download are a large share of the total RTDL time. At 131K and 262K points, useful traversal and summary work dominate those fixed costs, and the same generic RTDL path moves ahead of the CuPy grid opponent on uniform data too." This interpretation is supported by the observed data, where uniform rows, which were slower at smaller scales (as per Goal2813), now show speedups at larger scales, suggesting that fixed overheads were indeed the limiting factor previously. The proposed next steps (focusing on lower-overhead small-row execution contract) are also consistent with this interpretation.

5.  **Confirm whether claim boundaries remain closed: no public RTDL-beats-CuPy claim, no RTDL-beats-RTNN-paper claim, no paper reproduction claim, no broad RT-core speedup claim, and no whole-app speedup claim.**
    *   **Confirmed.** The "Claim Boundary" section in the report explicitly lists all these claims as "not authorized". Both JSON artifacts also set the corresponding `claim_boundary` flags to `false`. The test file `tests/goal2814_rtnn_unsorted_topk_scale_sweep_test.py` includes assertions to ensure these specific claims are not authorized, verifying that the boundaries are strictly maintained.

6.  **Call out any stale wording, overclaim, missing evidence, artifact/test mismatch, or app-agnosticity risk.**
    *   No issues identified. The wording is precise and avoids any overclaims. All evidence presented in the report is consistent with the provided artifacts and test results. There is no artifact/test mismatch. The report reaffirms the app-agnosticity principle for future development by emphasizing reusable generic optimizations over application-specific shortcuts.
