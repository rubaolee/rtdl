# Goal2021 External Review: Goal2020 CuPy Extent Device AABB Payload

**Date:** 2026-05-14

**Reviewed Goal:** Goal2020 CuPy Extent Device AABB Payload Perf

**Implementation:** `examples/rtdl_control_apps_cupy_rawkernel.py`
**Test:** `tests/goal2020_cupy_extent_device_aabb_payload_perf_test.py`
**Report:** `docs/reports/goal2020_cupy_extent_device_aabb_payload_perf_2026-05-14.md`
**Pod artifacts:**
- `docs/reports/goal2020_pod_cupy_extent_device_aabb_payload_2048.json`
- `docs/reports/goal2020_pod_cupy_extent_device_aabb_payload_4096.json`
- `docs/reports/goal2020_pod_cupy_extent_device_aabb_payload_8192.json`
**Updated matrix:**
- `docs/reports/goal2015_current_all_app_v18_v2_perf_analysis_after_goal2009_2026-05-14.json`

---

## Review Findings

1.  **Does the implementation really remove the avoidable CuPy GPU-to-Python-set-to-GPU round trip for the `cupy_extent` + `cupy` polygon path?**
    Yes, the implementation successfully removes the GPU-to-Python-set-to-GPU round trip. The `_partner_pair_payload_table_cupy_extent` function in `examples/rtdl_control_apps_cupy_rawkernel.py` creates CuPy arrays directly for candidate indices and box columns, which are then passed to `aabb_pair_overlap_summary_2d_partner_columns` via `_pair_extent_cupy_summary`. This is explicitly confirmed in the Goal2020 report and verified by the test `test_cupy_extent_path_builds_device_payload_without_python_set_roundtrip`.

2.  **Does it preserve the old compatibility path for `cpu_fallback`, `embree`, and `optix` candidate sources?**
    Yes, the compatibility paths are preserved. The `_polygon_summary_inputs` function contains logic to use `_positive_candidate_pairs_embree`, `_positive_candidate_pairs_optix`, or the `cpu_all_pairs` approach when `candidate_backend` is set accordingly or when the `partner` is not `cupy`. The Goal2020 report explicitly states, "Preserved the older host `set` path for `cpu_fallback`, `embree`, `optix`, and compatibility tests."

3.  **Do the artifacts support the claimed ratios and correctness at 2048, 4096, and 8192 copies?**
    Yes, the provided pod artifacts (`.json` files) and the summary table in the Goal2020 report (`.md` file) consistently support the claimed ratios and correctness. For both `polygon_pair_overlap_area_rows` and `polygon_set_jaccard` at all three scales (2048, 4096, 8192 copies), the `v2_vs_v1_8_ratio` is well below 0.25x, indicating significant speedup. Furthermore, `all_match_v1_8_python_rtdl_oracle` is `true` across all artifacts, confirming correctness. The unit test `test_pod_artifacts_record_correct_polygon_speedups_at_multiple_scales` also asserts these conditions.

4.  **Does the report keep the boundary tight: authored axis-aligned extent control rows only, not arbitrary polygon overlay, not an OptiX RT-core claim, and not a v2.0 release authorization?**
    Yes, the report (`docs/reports/goal2020_cupy_extent_device_aabb_payload_perf_2026-05-14.md`) maintains a tight boundary for its claims. It explicitly states that it is "not arbitrary polygon overlay," "not an OptiX RT-core polygon candidate-discovery claim," and that "v2.0 release authorization still depends on the final release audit and required external consensus." The report clearly defines the scope as "the authored axis-aligned extent control contract." The test `test_report_keeps_claim_boundary_tight` confirms these explicit statements.

5.  **Does the matrix update accurately reflect the latest Goal2020 polygon evidence without overclaiming?**
    Yes, the updated matrix (`docs/reports/goal2015_current_all_app_v18_v2_perf_analysis_after_goal2009_2026-05-14.json`) accurately incorporates the Goal2020 evidence. It includes entries for `polygon_pair_overlap_area_rows` and `polygon_set_jaccard` using the 8192 copies data (the largest scale), and the associated `insight` field precisely reiterates the tight boundaries of the claim, matching the statements in the Goal2020 report. The classification "positive-bounded" further reinforces the accurate representation without overclaiming.

## Verdict

`accept`
