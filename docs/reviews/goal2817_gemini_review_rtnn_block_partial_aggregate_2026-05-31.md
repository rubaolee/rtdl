# Gemini Review for Goal2817 RTNN Block-Partial Aggregate (2026-05-31)

## Verdict: accept-with-boundary

## Review Questions:

1. **Confirm whether Goal2817 is generic and app-agnostic: fixed-radius, prepared-query, ranked-summary aggregate partials, not an RTNN-native shortcut.**
   - **Confirmed.** The report (`docs/reports/goal2817_rtnn_block_partial_aggregate_2026-05-31.md`) explicitly states, "This remains app-agnostic. The native vocabulary is fixed-radius, query points, ranked summaries, aggregate partials, and prepared query handles. No RTNN native symbol or benchmark-specific branch is introduced." The test file (`tests/goal2817_rtnn_block_partial_aggregate_test.py`) includes assertions to ensure that no `rtnn` specific naming is present in the core kernel (`src/native/optix/rtdl_optix_core.cpp`), and verifies the presence of generic `fixed_radius_neighbors_3d_grid_ranked_summary_aggregate_f32_blocks` and `FrnRankedAggregate* partials_out` parameters.

2. **Confirm whether the implementation separates summary aggregate output from ordered witness-row output.**
   - **Confirmed.** The report states, "The design is still contract-driven: use block partials when the user asks for a summary aggregate, not when the user asks for ordered witness rows." The kernel `fixed_radius_neighbors_3d_grid_ranked_summary_aggregate_f32_blocks` in `src/native/optix/rtdl_optix_core.cpp` and the phase label `prepared_query_uniform_cell_ranked_summary_aggregate_f32_block_partials` in `src/rtdsl/optix_runtime.py` specifically indicate a summary aggregate function. The tests verify the structure of summary aggregate outputs and do not show any handling of ordered witness rows, confirming this separation.

3. **Confirm whether the pod artifacts are valid: source commit `578cfe947037fff476c81b84a11e36ac6ac8fe45`, empty `source_dirty`, status pass, median timing, exact aggregate agreement with CuPy grid, and correct phase label for block-partial rows.**
   - **Confirmed.**
     - **Source Commit & `source_dirty`**: The report and both `rtnn_block_partial_median_f32_32768.json` and `rtnn_block_partial_median_f32_65536.json` artifacts show `source_commit: 578cfe947037fff476c81b84a11e36ac6ac8fe45` and `source_dirty: []`. The test `test_pod_artifacts_show_65k_uniform_crossing_and_preserve_correctness` explicitly checks for these values.
     - **Status Pass**: All JSON artifacts show `"status": "pass"`.
     - **Median Timing**: All `rows` entries in the JSON artifacts consistently show `"rtdl_elapsed_statistic": "median"` and `"cupy_grid_elapsed_statistic": "median"`.
     - **Exact Aggregate Agreement**: All `rows` entries in the JSON artifacts show `"ranked_aggregate_matches_cupy_grid": true`.
     - **Correct Phase Label**: For uniform and shell distributions in the JSON artifacts, the `rtdl_phase_summary` correctly lists `"modes": ["prepared_query_uniform_cell_ranked_summary_aggregate_f32_block_partials"]`.

4. **Confirm whether the timing table is accurate and bounded:**
   - **32K uniform improves 1.146x but still trails CuPy at 0.920x.**
   - **65K uniform improves 1.121x and crosses parity at 1.077x CuPy/RTDL.**
   - **5 of 6 small rows now beat CuPy; only 32K uniform remains below parity.**
   - **65K shell regresses modestly versus Goal2815 but still has a large 7.451x CuPy/RTDL margin.**
   - **Confirmed.** The timing data presented in the `docs/reports/goal2817_rtnn_block_partial_aggregate_2026-05-31.md` report is consistent with the raw median timings and ratios found in the `goal2817_rtnn_block_partial_aggregate_pod/*.json` and `goal2815_rtnn_prepared_aggregate_workspace_pod/*.json` artifacts. The improvements, remaining lag, crossing parity, and regression are all numerically verifiable from the provided JSON data. The test `test_block_partial_path_improves_uniform_rows_over_goal2815` explicitly confirms the uniform improvements and parity crossing for 65K. The test also asserts `self.assertGreaterEqual(wins, 5)`, confirming 5 of 6 rows beat CuPy.

5. **Confirm whether the report keeps claim boundaries closed: no public RTDL-beats-CuPy claim, no RTDL-beats-RTNN-paper claim, no paper reproduction claim, no broad RT-core speedup claim, and no whole-app speedup claim.**
   - **Confirmed.** The "Claim Boundary" section in `docs/reports/goal2817_rtnn_block_partial_aggregate_2026-05-31.md` explicitly states "No ... claim is authorized" for all listed items. Additionally, the `claim_boundary` fields within the pod JSON artifacts (e.g., `"public_speedup_claim_authorized": false`) and the `test_report_keeps_boundary_and_names_remaining_gap` in the test file further confirm that these boundaries are maintained.

6. **Call out any stale wording, overclaim, missing evidence, artifact/test mismatch, determinism/concurrency risk, or app-agnosticity risk.**
   - No stale wording, overclaims, missing evidence, artifact/test mismatches, or app-agnosticity risks were identified. The report is clear and consistent. While the report doesn't explicitly discuss determinism or concurrency for the new block-partial aggregation method, this is considered a missing explicit discussion rather than an identified risk based on the provided materials.
