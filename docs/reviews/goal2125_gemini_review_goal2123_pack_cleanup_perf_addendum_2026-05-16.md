# Goal2125 Gemini Review: Goal2123 Pack-Cleanup Evidence Addendum

Date: 2026-05-16
Reviewer: Gemini CLI Agent

## Context

This addendum reviews the impact of a Python `Point` tuple construction removal from the reduced Hausdorff path (pack cleanup), following up on the Goal2124 review. The native ABI and app boundary are confirmed to be unchanged, with the focus on refreshed A5000 synthetic sweep timings.

## Files Reviewed

*   `docs/reviews/goal2124_gemini_review_goal2121_2123_xhd_hausdorff_optix_2026-05-16.md`
*   `docs/reports/goal2123_xhd_point_group_nearest_reduction_2026-05-16.md`
*   `docs/reports/goal2123_pod_grouped_reduced_hd_perf_after_pack_cleanup_2026-05-16.json`
*   `examples/rtdl_hausdorff_v2_function.py`
*   `tests/goal2123_xhd_point_group_nearest_reduction_test.py`

## Questions & Answers

### 1. Does the pack cleanup preserve the app-agnostic/native-ABI boundary already accepted in Goal2124?

The Goal2123 report explicitly states that the generic engine boundary is `accept` and that the native surface remains app-agnostic, exposing only generic point group, nearest witness, and max-distance reduction primitives. The new symbol `rtdl_optix_reduce_prepared_point_group_nearest_max_distance_2d` itself avoids domain-specific terms like "Hausdorff" or "X-HD". This is consistent with the findings and verdict of Goal2124 and is further validated by the unit tests (`test_generic_native_reduce_symbol_is_wired_without_app_terms`). The pack cleanup thus preserves the app-agnostic/native-ABI boundary.

**Verdict:** `accept`

### 2. Does the updated report fairly represent the refreshed A5000 timings?

The updated Goal2123 report presents A5000 synthetic timings in a table ("A5000 Synthetic Timing"), and these values are directly consistent with the provided raw JSON data (`docs/reports/goal2123_pod_grouped_reduced_hd_perf_after_pack_cleanup_2026-05-16.json`). The report's interpretation accurately reflects the observed crossover point (131,072 points) and the magnitude of speedup. Given that the pack cleanup was a refinement to the existing reduced path, the report fairly represents these refreshed timings.

**Verdict:** `accept`

### 3. Is it fair to say the reduced RTDL/OptiX path beats CuPy exact all-pairs continuation at 131,072+ synthetic points per set on this run, while the exact X-HD paper dataset claim remains `needs-more-evidence`?

Based on the A5000 synthetic timing data in the Goal2123 report and the corroborating JSON, the reduced RTDL/OptiX path indeed demonstrates superior performance (faster elapsed time) compared to CuPy exact all-pairs continuation for synthetic point sets of 131,072 points and larger. The verdict for "Outperform pure CUDA on large synthetic sets" is `accept-with-boundary` in the Goal2123 report, indicating this specific claim is well-supported. Conversely, both Goal2123 and Goal2124 consistently assign a `needs-more-evidence` verdict for claims regarding performance on the *exact X-HD paper datasets* due to their unavailability. Therefore, it is fair to make both statements.

**Verdict:** `accept`
