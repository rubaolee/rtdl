Verdict: ACCEPTED after follow-up review.

## Findings:

The Goal990 changes correctly move Hausdorff `directed_threshold_prepared` and Barnes-Hut `node_coverage_prepared` public app paths from count-row materialization to scalar prepared threshold counts.

-   **Code Changes (`examples/rtdl_hausdorff_distance_app.py`, `examples/rtdl_barnes_hut_force_app.py`):**
    -   Both applications correctly implement the use of `prepared.count_threshold_reached` within their respective OptiX summary modes (`directed_threshold_prepared` and `node_coverage_prepared`).
    -   The output payloads for these modes consistently reflect a scalar decision summary, including fields like `covered_source_count`/`covered_body_count`, `within_threshold`/`all_bodies_have_node_candidate`, `summary_mode: scalar_threshold_count`, and `row_count: None`, as specified in the Goal990 report.

-   **Identity/Witness Honesty Boundary:**
    -   The honesty boundary is clearly maintained. In both applications, `violating_source_ids` (Hausdorff) and `uncovered_body_ids` (Barnes-Hut) are correctly set to `None` when operating in scalar mode, regardless of whether the threshold is met or not. This aligns with the principle that scalar decisions do not emit full witness rows and that identity parity is not available in these cases. The `identity_parity_available` flag accurately reflects this.
    -   The `docs/app_engine_support_matrix.md` explicitly reiterates this honesty boundary for both applications, confirming the design intent.

-   **Test Adequacy (`tests/goal879_hausdorff_threshold_rt_core_subpath_test.py`, `tests/goal882_barnes_hut_node_coverage_optix_subpath_test.py`, `tests/goal957_graph_hausdorff_native_continuation_metadata_test.py`):**
    -   The tests successfully verify that the applications enter the new scalar-count path, that the `summary_mode` is correctly reported as `scalar_threshold_count`, and that `row_count` is `None`.
    -   They also confirm that the `rt_core_accelerated` flag is correctly set and that the results match the oracle for a "success" scenario (all points/bodies covered).
    -   The `test_hausdorff_optix_threshold_reports_native_continuation` in `goal957_graph_hausdorff_native_continuation_metadata_test.py` further confirms correct metadata reporting for the new scalar path.

-   **Follow-up on Scalar Failure-Path Tests:**
    -   As recommended in the initial review, explicit failure-path tests were added for the scalar witness boundary.
    -   `tests/goal879_hausdorff_threshold_rt_core_subpath_test.py` now includes `test_optix_threshold_failure_keeps_scalar_identity_boundary`, which correctly asserts that `violating_source_ids` is `None` and `identity_parity_available` is `False` when the Hausdorff threshold is not met in scalar mode.
    -   `tests/goal882_barnes_hut_node_coverage_optix_subpath_test.py` now includes `test_optix_node_coverage_failure_keeps_scalar_identity_boundary`, which correctly asserts that `uncovered_body_ids` is `None` and `identity_parity_available` is `False` when the Barnes-Hut node coverage threshold is not met in scalar mode.
    -   These tests adequately cover the scalar witness-boundary recommendation.

-   **No New Blockers Introduced:**
    -   The changes are focused and well-contained. No new blockers or unintended side effects have been identified. The `run` method (which previously caused row materialization) is correctly bypassed, and attempts to use the old behavior with `require_rt_core=True` are appropriately rejected by new runtime errors.

## Final Verdict:

The implementation successfully addresses the goal of moving to scalar prepared threshold counts for the specified applications while maintaining honesty boundaries and providing adequate test coverage, including the recommended scalar failure-path tests. No new blockers have been introduced. The changes are accepted.
