# Goal2810 Gemini Review: RTNN Ranked-Summary Aggregate

Date: 2026-05-31

Verdict: accept-with-boundary

## Review Findings

This independent review confirms the implementation and documentation of Goal2810, "RTNN Ranked-Summary Aggregate," as described.

### 1. Generic Prepared Fixed-Radius Ranked-Neighbor Aggregate Path

**Confirmed.** Goal2810 explicitly introduces a generic prepared fixed-radius ranked-neighbor aggregate path for OptiX, rather than an RTNN-specific native engine shortcut.
*   The `docs/reports/goal2810_rtnn_ranked_summary_aggregate_2026-05-31.md` report states: "Goal2810 improves the RTNN benchmark path by adding a generic prepared fixed-radius ranked-neighbor aggregate for OptiX," and "This is not an RTNN-specific native engine path. The native surface remains a generic fixed-radius neighbor/ranked-summary contract."
*   Code changes in `src/native/optix/rtdl_optix_core.cpp` are described as adding "generic ranked-summary aggregate CUDA kernels."
*   The `tests/goal2810_rtnn_ranked_summary_aggregate_test.py` validates this by asserting the presence of generic function names (`fixed_radius_neighbors_3d_grid_ranked_summary_aggregate`, `rtdl_optix_aggregate_prepared_ranked_fixed_radius_neighbor_summaries_3d`, `aggregate_ranked_summary`) and specifically asserting that "rtnn_aggregate" is *not* found in `rtdl_optix_core.cpp`.

### 2. Clean Pod Artifacts Validity and Agreement

**Confirmed.** The clean pod artifacts (`rtnn_aggregate_f32_32768.json`, `rtnn_aggregate_f32_65536.json`) are valid, show clean-provenance, and demonstrate exact candidate-count and aggregate-summary agreement with the CuPy grid opponent.
*   Both JSON artifacts explicitly show `"status": "pass"`, `"source_commit": "734488a92f7a2a8e9c3fa18598c621558f6a1630"`, and `"source_dirty": []`.
*   Within each artifact's rows, `"candidate_count_matches_cupy_grid": true`, `"candidate_count_within_tolerance": true`, and `"ranked_aggregate_matches_cupy_grid": true` are consistently reported.
*   The `tests/goal2810_rtnn_ranked_summary_aggregate_test.py` includes assertions to verify these exact fields in the `test_clean_pod_artifacts_pass_and_keep_claims_closed` method.

### 3. Correct Performance Result Presentation and Claim Authorization

**Confirmed.** The report correctly presents the performance results, indicating material improvement over the previous ranked-row path for RTDL, but acknowledges that CuPy remains faster, thus authorizing no public speedup claim.
*   The performance tables in the report clearly show "RTDL improvement" factors (e.g., 1.52x - 1.95x) over the Goal2808/Goal2800 RTDL paths, while the "CuPy/RTDL" ratios (e.g., 0.135x - 0.909x) indicate CuPy's superior performance.
*   The "Claim Boundary" section explicitly states: "No public speedup claim is authorized." and "No RTDL-beats-CuPy claim is authorized."
*   The test `test_goal2810_improves_rtdl_path_without_claiming_cupy_win` verifies both the RTDL improvement and the fact that CuPy remains faster (`cupy_grid_over_rtdl_elapsed_ratio < 1.0`).

### 4. Explicit and Fair Float32 Comparison Boundary

**Confirmed.** The float32 comparison boundary is explicit and fair, used because the promoted CuPy grid opponent operates in float32, while the exact-double aggregate path remains available.
*   The report explicitly mentions: "...adds an explicit float32 same-precision mode for the CuPy grid comparison," and "The exact-double aggregate path remains available... the promoted RTNN benchmark row uses `precision="float32"` because the same-contract CuPy grid opponent is float32."
*   The pod artifact filenames (`_f32_`) and their internal `contract` fields (`"precision": "float32"`) reflect this.
*   `src/rtdsl/optix_runtime.py` shows `aggregate_ranked_summary` accepting a `precision` argument, and `src/native/optix/rtdl_optix_api.cpp` and `src/native/optix/rtdl_optix_prelude.h` define distinct float32 (`..._f32`) and double versions of the aggregate functions and structures.
*   `scripts/goal2800_rtnn_v25_live_ranked_summary_harness.py` calls the RTDL batched 3D neighbors with `result_mode="ranked-summary-aggregate-float32"` and the CuPy grid summary with `dtype="float32"`, ensuring a fair comparison.

### 5. Test Coverage

**Confirmed.** The tests adequately cover the native/Python surfaces, pod artifacts, claim boundary, and remaining-work explanation.
*   `tests/goal2810_rtnn_ranked_summary_aggregate_test.py` contains dedicated tests for:
    *   `test_native_and_python_surfaces_are_generic_aggregate_paths` (native/Python surfaces).
    *   `test_clean_pod_artifacts_pass_and_keep_claims_closed` (pod artifacts and claim boundary from artifacts).
    *   `test_goal2810_improves_rtdl_path_without_claiming_cupy_win` (performance comparisons).
    *   `test_report_records_boundary_and_remaining_work` (explicitly checking the report for claim boundaries and remaining work sections).

### 6. Stale Wording, Overclaim, Missing Evidence, or Test/Report Mismatch

No instances of stale wording, overclaim, missing evidence, or test/report mismatches were found. The documentation, code changes, tests, and artifacts are consistent and mutually reinforcing. The report is clear about the achievements and limitations, explicitly outlining the claim boundaries.
