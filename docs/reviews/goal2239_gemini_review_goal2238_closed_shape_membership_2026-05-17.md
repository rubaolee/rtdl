# Independent Gemini Review: Goal2238 Closed-Shape Membership Primitive

**Date:** 2026-05-17

**Goal:** Independent Gemini review of Goal2238.

**Verdict:** `accept-with-boundary`

**Reviewer:** Gemini Agent

**Note:** This is an independent Gemini review, distinct from any Codex review.

## Review Requirements and Findings:

1.  **Confirm the future-version to-do list exists and is appropriate for catching deferred ideas without making them release commitments.**
    *   **Finding:** Confirmed. The file `docs/research/future_version_to_do_list.md` exists and clearly outlines future ideas, explicitly stating that it "Do not treat this file as release authorization. Promotion still needs the normal report/review/consensus process." Each item includes a boundary statement reinforcing this.

2.  **Confirm Goal2238 exposes a generic app-agnostic closed-shape membership surface:**
    *   `rtdl_optix_run_point_closed_shape_membership_2d`
    *   `closed_shape_membership_2d_optix`
    *   row fields `point_id`, `shape_id`, `membership`
    *   **Finding:** Confirmed.
        *   `src/native/optix/rtdl_optix_prelude.h` defines `struct RtdlPointClosedShapeMembershipRow` with `point_id`, `shape_id`, and `membership`, and declares `int rtdl_optix_run_point_closed_shape_membership_2d`.
        *   `src/native/optix/rtdl_optix_api.cpp` includes the `extern "C"` declaration for `rtdl_optix_run_point_closed_shape_membership_2d`.
        *   `src/rtdsl/optix_runtime.py` defines `class _RtdlPointClosedShapeMembershipRow` with the specified fields and exposes `def closed_shape_membership_2d_optix`.
        *   `tests/goal2238_closed_shape_membership_primitive_test.py` contains tests that explicitly verify the presence and structure of these elements.

3.  **Confirm the new public vocabulary avoids RayJoin/PIP/polygon/county/map/spatial-join naming.**
    *   **Finding:** Confirmed. The `docs/reports/goal2238_closed_shape_membership_primitive_2026-05-17.md` explicitly states the use of generic terms and avoidance of these specific names. Code review of `rtdl_optix_prelude.h` and `optix_runtime.py` shows the use of `ClosedShapeRef` and `PointClosedShapeMembershipRow`, `closed_shape_membership_2d_optix` which are generic. `tests/goal2238_closed_shape_membership_primitive_test.py` includes a dedicated test to ensure these forbidden terms are not used in the primary public symbol.

4.  **Confirm the implementation honestly wraps the existing optimized closed-boundary path and converts legacy internal rows into generic public rows, without claiming the old internal implementation has been fully rewritten.**
    *   **Finding:** Confirmed. The report `docs/reports/goal2238_closed_shape_membership_primitive_2026-05-17.md` clearly states this approach. The `tests/goal2238_closed_shape_membership_primitive_test.py::test_workload_wraps_existing_optimized_path_but_exports_generic_rows` verifies that `run_pip_optix` (an existing internal function) is called and that legacy fields (`polygon_id`, `contains`) are mapped to the new public fields (`shape_id`, `membership`) within `src/native/optix/rtdl_optix_workloads.cpp`.

5.  **Verify the pod evidence:**
    *   functional rows: point 1 -> shape 10 and point 3 -> shape 11
    *   RayJoin-style 10,000-query probe row match: true
    *   generic closed-shape median: `0.03738784417510033`
    *   legacy optimized median: `0.03850874863564968`
    *   ratio: `0.9708922128019587`
    *   row count: 879
    *   **Finding:** Confirmed. All specified pod evidence values were found to match exactly in `docs/reports/goal2238_closed_shape_membership_primitive_2026-05-17.md`.

6.  **Check the boundary: no v2.0 release claim, no broad RayJoin/PIP speedup claim, no full RayJoin reproduction claim.**
    *   **Finding:** Confirmed. The "Boundary" section of `docs/reports/goal2238_closed_shape_membership_primitive_2026-05-17.md` explicitly disclaims all the specified items. The `test_report_keeps_release_and_perf_boundary` in the test file also verifies the presence of these disclaimers.

## Conclusion:

Goal2238 successfully introduces a generic app-agnostic closed-shape membership primitive, adhering to the specified vocabulary and implementation honesty. The pod evidence validates its functional correctness and performance characteristics relative to the existing optimized path. The documentation appropriately sets boundaries for its claims and avoids premature release or broad performance statements.
