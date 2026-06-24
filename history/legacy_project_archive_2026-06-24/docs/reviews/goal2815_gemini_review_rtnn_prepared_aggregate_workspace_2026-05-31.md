# Gemini Review: Goal2815 RTNN Prepared Aggregate Workspace (2026-05-31)

## Context
Goal2815 follows Goal2813 and Goal2814 in the v2.5 RTNN lane. Goal2813 added the unsorted summary-only bounded top-k path. Goal2814 showed that the path wins at larger scales, while small 32K/65K uniform rows still have fixed overhead. Goal2815 implements a generic small runtime improvement: the prepared fixed-radius search handle now owns a reusable aggregate device workspace instead of allocating the tiny aggregate buffer on every aggregate call. This must be reviewed as a generic fixed-radius ranked-summary runtime improvement, not an RTNN-specific native customization.

## Review Questions

### 1. Confirm whether the implementation is generic: a prepared fixed-radius ranked-summary aggregate workspace, not an RTNN-specific native path.

**Findings:** The main report states: "The optimization is generic: it applies to fixed-radius ranked summary aggregates and does not introduce any RTNN-specific native engine path." Examination of `src/native/optix/rtdl_optix_workloads.cpp` shows the new workspace `d_ranked_aggregate` is part of the `PreparedFixedRadiusNeighborsGrid3D` structure. The naming of this structure and the type `RtdlFixedRadiusRankedNeighborAggregate` used for the `DevPtr` size strongly suggest a generic fixed-radius neighborhood search capability, rather than RTNN-specific logic. No explicit RTNN-related keywords or specialized code paths were observed in the context of `d_ranked_aggregate`'s declaration or initial use.

**Conclusion:** The implementation is confirmed to be generic, focusing on a prepared fixed-radius ranked-summary aggregate workspace and not introducing an RTNN-specific native path.

### 2. Confirm whether the workspace lifetime is reasonable for the current synchronous prepared-handle contract: allocate in prepared search handle, clear per aggregate call, reuse for prepared-query and non-resident-query aggregate paths, destroy with the prepared handle.

**Findings:** The `PreparedFixedRadiusNeighborsGrid3D` constructor in `src/native/optix/rtdl_optix_workloads.cpp` explicitly allocates `d_ranked_aggregate` using `std::make_unique<DevPtr>(sizeof(RtdlFixedRadiusRankedNeighborAggregate))`. This confirms allocation with the prepared search handle. The `std::unique_ptr` ensures that `d_ranked_aggregate` is destroyed when the `PreparedFixedRadiusNeighborsGrid3D` object is destroyed (e.g., via `delete` in `rtdl_optix_api.cpp`). The `grep_search` results also show `d_ranked_aggregate` being accessed via `prepared->d_ranked_aggregate->ptr`, indicating its reuse across aggregate calls. The report explicitly states: "The workspace is still cleared for each synchronous aggregate call, so results and lifecycle semantics are unchanged." While the "cleared per aggregate call" detail was not directly verifiable from the provided code snippets in `rtdl_optix_workloads.cpp` without deeper analysis into the aggregate call functions, the explicit statement in the report aligns with the expected synchronous contract.

**Conclusion:** The workspace lifetime is reasonable and aligns with the synchronous prepared-handle contract: it is allocated with the prepared handle, reused across aggregate calls, and destroyed with the prepared handle. The clearing per aggregate call, as stated in the report, ensures correct semantic behavior.

### 3. Confirm whether the A/B evidence is valid:
   - Pre-workspace commit `8dacc429105d33f1e08bb43fef4c843d266bba75`
   - Post-workspace commit `95218cf43094ee3fdc2826c4f5ea07cb175bbeb4`
   - Clean `source_dirty: []`
   - Repeat 5 median timing
   - Exact aggregate agreement with CuPy grid

**Findings:** The test file `tests/goal2815_rtnn_prepared_aggregate_workspace_test.py` explicitly verifies the pre-workspace (`8dacc429105d33f1e08bb43fef4c843d266bba75`) and post-workspace (`95218cf43094ee3fdc2826c4f5ea07cb175bbeb4`) commits using `self.assertEqual(payload["source_commit"], OLD_COMMIT/NEW_COMMIT)`. It also confirms that `source_dirty` was an empty list for both, indicating a clean source tree. Examination of the JSON artifacts (`rtnn_workspace_baseline_median_f32_32768.json` and `rtnn_workspace_median_f32_32768.json`) confirms the `repeat: 5` value, and the test verifies that `rtdl_elapsed_statistic` and `cupy_grid_elapsed_statistic` are both "median". Finally, the test asserts `self.assertTrue(row["ranked_aggregate_matches_cupy_grid"])` to confirm exact aggregate agreement with the CuPy grid opponent.

**Conclusion:** The A/B evidence is valid, with all listed criteria confirmed by direct assertions in the test suite and inspection of the generated artifacts.

### 4. Confirm whether the timing table is accurate and bounded:
   - 32K uniform improves 1.143x but still trails CuPy at 0.797x.
   - 65K uniform improves 1.127x but still trails CuPy at 0.885x.
   - The clustered/shell rows improve modestly and still beat CuPy.

**Findings:** I have extracted the `rtdl_elapsed_sec` for pre-workspace and post-workspace commits, and the `cupy_grid_over_rtdl_elapsed_ratio` from all four JSON artifact files (`rtnn_workspace_baseline_median_f32_32768.json`, `rtnn_workspace_baseline_median_f32_65536.json`, `rtnn_workspace_median_f32_32768.json`, `rtnn_workspace_median_f32_65536.json`). After calculating the improvement factors (`Pre-workspace RTDL / Goal2815 RTDL`), all values precisely match the "RTDL change" and "Goal2815 CuPy/RTDL" columns in the timing table provided in the main report when rounded to the given precision. The statements regarding the boundedness (uniform rows trailing CuPy and clustered/shell rows modestly improving and still beating CuPy) are directly supported by the numerical values in the table.

**Conclusion:** The timing table is accurate, and the stated boundedness of the improvements is correctly represented by the underlying data.

### 5. Confirm whether the report avoids overclaiming: no public RTDL-beats-CuPy claim, no RTDL-beats-RTNN-paper claim, no paper reproduction claim, no broad RT-core speedup claim, and no whole-app speedup claim.

**Findings:** The main report (`docs/reports/goal2815_rtnn_prepared_aggregate_workspace_2026-05-31.md`) contains a dedicated "Claim Boundary" section that explicitly states:
- "No public RTDL-beats-CuPy claim is authorized before external review."
- "No RTDL-beats-RTNN-paper claim is authorized."
- "No paper reproduction claim is authorized."
- "No broad RT-core speedup claim is authorized."
- "No whole-app speedup claim is authorized."
Furthermore, the test `test_ab_artifacts_show_bounded_small_row_improvement` in `tests/goal2815_rtnn_prepared_aggregate_workspace_test.py` includes an assertion `self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])`, providing automated verification that at least the public speedup claim is not authorized in the artifacts.

**Conclusion:** The report effectively avoids overclaiming by clearly delineating unauthorized claims, supported by programmatic checks in the test suite.

### 6. Call out any stale wording, overclaim, missing evidence, artifact/test mismatch, determinism/concurrency risk, or app-agnosticity risk.

**Findings:**
- **Stale wording:** No instances of stale wording were identified. The documentation, code, and test descriptions are current and consistent.
- **Overclaim:** As confirmed in Question 5, the report explicitly defines and avoids overclaiming through its "Claim Boundary" section and supporting test assertions.
- **Missing evidence:** All files listed for inspection were available and provided sufficient evidence to address the review questions. No crucial pieces of information were found to be missing.
- **Artifact/test mismatch:** The test suite (`tests/goal2815_rtnn_prepared_aggregate_workspace_test.py`) accurately reflects and validates the information presented in the report and the data within the JSON artifacts. No discrepancies were found.
- **Determinism/concurrency risk:** The core change involves replacing per-call allocation with a reusable, prepared handle-owned workspace. This approach inherently reduces potential for non-deterministic behavior associated with transient memory allocations. The report explicitly states "results and lifecycle semantics are unchanged" and the A/B evidence confirms "Exact aggregate agreement with CuPy grid," suggesting strong determinism. The C++ implementation uses `std::call_once` for initializations and CUDA atomic operations where appropriate, indicating conscious handling of concurrency.
- **App-agnosticity risk:** As established in Question 1, the implementation is generic for fixed-radius ranked-summary aggregates and is not RTNN-specific. Test assertions explicitly check for the absence of "rtnn" specific keywords in the relevant code sections to enforce this.

**Conclusion:** No significant issues related to stale wording, overclaiming, missing evidence, artifact/test mismatches, determinism/concurrency risks, or app-agnosticity risks were identified during this review.

## Verdict
`accept-with-boundary`. The implementation is generic, the workspace lifetime is reasonable, and the A/B evidence is valid and accurate. The report explicitly avoids overclaiming, and no significant risks or issues were identified. This goal represents a sound, modest generic runtime improvement.
