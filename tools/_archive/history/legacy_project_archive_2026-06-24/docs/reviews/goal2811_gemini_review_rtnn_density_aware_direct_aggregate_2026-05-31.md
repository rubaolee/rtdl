# Gemini Review of Goal2811 RTNN Density-Aware Direct Aggregate

Date: 2026-05-31
Reviewer: Gemini Agent

## Verdict: accept

## Review Details

This review covers Goal2811, which aims to improve the fixed-radius ranked-neighbor aggregate path by introducing a density-aware selection mechanism. The review included inspection of the main report, associated unit tests, pod artifacts, C++ OptiX implementation, Python runtime bindings, and the harness script.

### 1. Genericity of Goal2811

**Question:** Confirm whether Goal2811 remains a generic fixed-radius ranked-neighbor aggregate improvement, not an RTNN-specific native engine shortcut.
**Answer:** Confirmed. The `docs/reports/goal2811_rtnn_density_aware_direct_aggregate_2026-05-31.md` explicitly states: "This is still a generic fixed-radius neighbor/ranked-summary contract. No RTNN-specific native engine path or app-shaped ABI was added." This is further supported by `src/native/optix/rtdl_optix_workloads.cpp` which uses density signals without naming RTNN or adding app-specific code, as verified by `tests/goal2811_rtnn_direct_aggregate_kernel_test.py` (`self.assertNotIn("rtnn", core.lower())`).

### 2. Reasonableness of Density-Aware Selection

**Question:** Confirm whether the density-aware selection is reasonable: direct one-kernel aggregate for low occupied-cell density and two-step aggregate for dense clustered rows.
**Answer:** Confirmed. The report details the rationale: "Low-density rows benefit from fusing summary and reduction into one kernel. Dense rows can prefer a two-step path because the direct kernel's extra shared-memory reduction can reduce occupancy while the top-k loop is already compute-heavy." The `src/native/optix/rtdl_optix_workloads.cpp` code, as indicated by the test `test_promoted_float32_path_has_density_aware_direct_and_fallback_paths`, implements this logic using `mean_search_points_per_occupied_cell <= 4.0` as the threshold for direct aggregation. The pod artifacts (`rtnn_direct_density_median_f32_32768.json`, `rtnn_direct_density_median_f32_65536.json`) show that 'uniform' and 'shell' distributions use the `_direct` mode, while 'clustered' distributions use the two-step `_f32` mode, aligning with the expected behavior.

### 3. Harness Change to Median Repeat Timing

**Question:** Confirm whether the harness change from last-run timing to median repeat timing is correct and makes the evidence more stable without hiding raw runs.
**Answer:** Confirmed. The `docs/reports/goal2811_rtnn_density_aware_direct_aggregate_2026-05-31.md` notes the change in `scripts/goal2800_rtnn_v25_live_ranked_summary_harness.py` to report median elapsed time. The harness script itself uses a `_median_or_elapsed` function to derive the reported time from multiple `elapsed_runs_sec` values. The raw runs are preserved within the JSON artifacts under `rtdl_elapsed_runs_sec` and `cupy_grid_elapsed_runs_sec`, ensuring transparency. This approach enhances timing stability without obscuring individual run data.

### 4. Clean Pod Artifacts and Agreement with CuPy

**Question:** Confirm whether the clean pod artifacts are valid, clean-provenance, and keep exact candidate-count and aggregate-summary agreement with the CuPy grid opponent.
**Answer:** Confirmed. The "Clean Pod Evidence" section in the report clearly indicates clean commits (`source_dirty: []`). The unit test `test_pod_artifacts_are_clean_and_median_timed` explicitly verifies `status: "pass"`, `source_commit` matching the expected value, no `source_dirty` files, and crucially, `ranked_aggregate_matches_cupy_grid: true` for all rows. The JSON artifacts corroborate these checks, showing all passes and exact matches with the CuPy opponent.

### 5. Honesty in Performance Reporting

**Question:** Confirm whether the report presents the performance honestly, including the small 65K shell regression and the fact that CuPy remains faster on all rows.
**Answer:** Confirmed. The report openly states: "The one small regression is the 65K shell row." and "It does not make RTDL faster than the CuPy grid opponent." This aligns with the provided "Median Timing Results" table, where the 65K shell row shows a `0.977x` improvement (meaning RTDL is slower), and all "CuPy/RTDL" ratios are less than 1.0, indicating CuPy's superior performance. The "Claim Boundary" further reinforces this honesty by explicitly disallowing speedup claims against CuPy.

### 6. Stale Wording, Overclaim, Missing Evidence, or Test/Report Mismatch

**Answer:** No significant instances of stale wording, overclaim, missing evidence, or test/report mismatch were found. The documentation is consistent with the code and test results. The report's claim boundaries are appropriately conservative, reflecting the current state of performance.

---

**Conclusion:** Goal2811 successfully implements a density-aware direct aggregate, demonstrating a reasonable and well-documented approach to performance optimization for fixed-radius ranked-neighbor queries. The solution is generic, and its impact on performance is reported transparently, including regressions and comparisons against external baselines. The provided tests and artifacts validate the implementation and claims effectively.
