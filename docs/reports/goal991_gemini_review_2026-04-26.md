Verdict: ACCEPT

## Findings

The review confirms that the four public OptiX prepared claim paths now avoid `prepared.run` row materialization and use scalar `count_threshold_reached`, that witness/identity boundaries are honest, and that tests/docs are adequate.

1.  **Avoid `prepared.run` row materialization and use scalar `count_threshold_reached`:**
    *   **Code Review:** For all four applications (`examples/rtdl_ann_candidate_app.py`, `examples/rtdl_facility_knn_assignment.py`, `examples/rtdl_service_coverage_gaps.py`, `examples/rtdl_event_hotspot_screening.py`), the OptiX prepared summary modes correctly utilize `prepared.count_threshold_reached` and the output dictionaries are structured to return scalar values, explicitly setting row-based outputs to `None`.
    *   **Test Verification:** The relevant test files (`tests/goal810_spatial_apps_optix_summary_surface_test.py`, `tests/goal880_ann_candidate_threshold_rt_core_subpath_test.py`, `tests/goal881_facility_coverage_optix_subpath_test.py`, `tests/goal955_spatial_prepared_native_continuation_test.py`) contain mock objects that would raise an `AssertionError` if `prepared.run` were invoked, confirming that only `count_threshold_reached` is used. Threshold values (e.g., `HOTSPOT_THRESHOLD + 1` for hotspot screening) are also correctly asserted.

2.  **Witness/identity boundaries are honest:**
    *   **Code Review:** In the OptiX prepared summary modes for all four applications, fields related to identity (e.g., `uncovered_query_ids`, `uncovered_customer_ids`, `uncovered_household_ids`, `hotspots`) are consistently set to `None`, aligning with the stated intention of limiting these paths to scalar decisions.
    *   **Test Verification:** Tests explicitly assert that these identity-related fields are `None` when `identity_parity_available` is false, confirming adherence to the honesty boundaries.

3.  **Tests/docs are adequate:**
    *   **Tests:** The test suite provides good coverage, verifying the correct usage of `count_threshold_reached`, validating scalar outputs, and ensuring honesty boundaries are maintained through explicit assertions for `None` values where identities are not claimed.
    *   **Documentation:**
        *   `docs/reports/goal991_public_scalar_prepared_decision_paths_2026-04-26.md` clearly outlines the scope, changes, honesty boundaries, and testing procedures for Goal991.
        *   `docs/app_engine_support_matrix.md`, `docs/application_catalog.md`, and `docs/v1_0_rtx_app_status.md` have all been updated to reflect the scalar-only nature of these OptiX prepared paths and reiterate the honesty boundaries, including specific mentions of Goal991's impact.

## Required Fixes

None. The implementation, testing, and documentation are all in alignment with the requirements of Goal991.
