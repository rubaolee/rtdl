# Goal 741 - Embree All-App Compact Performance Closure - Gemini Flash Review

Date: 2026-04-21

## Verdict

**ACCEPT**

## Reasons

The Embree all-app compact performance closure is accepted for the following reasons:

1.  **Correctness and Honesty Boundaries:** The documentation (`goal741_embree_all_app_compact_perf_closure_2026-04-21.md`) and the performance data (`goal741_embree_all_app_perf_macos_2026-04-21.json`) are clear and consistent. The explicit declaration that timings are app-level wall-clock and include Python overhead ensures an honest and transparent assessment of performance. The performance harness (`scripts/goal714_embree_app_thread_perf.py`) further reinforces these boundaries by judiciously filtering payload data for canonical hash comparisons, preventing misleading results based on non-performance-critical metadata.

2.  **Effective Avoidance of Python Overhead:** The core objective of fairly characterizing Embree app performance by minimizing Python overhead has been successfully achieved.
    *   For `rtdl_dbscan_clustering_app.py` and `rtdl_outlier_detection_app.py`, the introduction of `--output-mode core_flags` and `--output-mode density_summary` respectively, directs the applications to utilize native Embree fixed-radius threshold counting (`rt.fixed_radius_count_threshold_2d_embree`). This allows for direct computation of compact summaries (core flags, density summaries) without the intermediate generation and Python-side processing of extensive neighbor rows.
    *   For `rtdl_hausdorff_distance_app.py`, the `--embree-result-mode directed_summary` enables native Embree execution of directed Hausdorff distance calculations (`rt.directed_hausdorff_2d_embree`). Crucially, for non-Embree backends when this summary mode is requested, the system leverages a pre-calculated, tiled oracle (`expected_tiled_hausdorff`). This prevents the O(N^2) brute-force Python oracle calculation from distorting performance measurements, ensuring a more accurate representation of Embree's contribution.

3.  **Robust Verification:** The dedicated test suite (`tests/goal741_embree_compact_app_perf_harness_test.py`) thoroughly verifies the intended behavior:
    *   It confirms that the compact modes in the app examples indeed bypass full Python data expansion (e.g., `neighbor_row_count` and `cluster_rows` are empty when expected).
    *   It validates that the `hausdorff_distance` app correctly uses the compact oracle, demonstrating that the harness's methodology is sound.
    *   Crucially, it explicitly checks that the `APP_CASES` within the main performance script (`goal714_embree_app_thread_perf.py`) are correctly configured to employ these new compact summary arguments for scaled applications, ensuring that the performance measurements are conducted as intended.

The changes collectively represent a significant and well-verified improvement in how Embree app performance is characterized, providing a clearer view of its native contributions.

## Linux addendum review

The Linux addendum in `docs/reports/goal741_embree_all_app_compact_perf_closure_2026-04-21.md` and the corresponding JSON data in `docs/reports/goal741_embree_all_app_perf_linux_2026-04-21.json` have been reviewed.

**Consistency Verification:**
All numerical data presented in the "Linux Evidence" table within the markdown report, specifically "CPU/reference sec", "Embree 1-thread sec", "Embree auto sec", and "Auto vs 1-thread", are consistent with the values found in the `goal741_embree_all_app_perf_linux_2026-04-21.json` file when rounded to the precision used in the markdown table.

**Overclaiming Assessment:**
The "Interpretation" section of the markdown report accurately reflects the performance speedups observed in the Linux JSON data for `facility_knn_assignment`, `hausdorff_distance`, and `ann_candidate_search`. The observation that "The Linux run confirms the same pattern with slightly larger absolute times" is also validated by comparing the macOS and Linux performance data.

**Conclusion:**
The Linux addendum is consistent with the provided JSON data and does not contain any overclaims.

**Verdict: ACCEPT**
