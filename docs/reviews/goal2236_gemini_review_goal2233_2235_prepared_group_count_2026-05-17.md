# Goal2236: Independent Gemini Review of Goal2233 and Goal2235

## Review Verdict

`accept-with-boundary`

## Summary

This is an independent Gemini review, distinct from any Codex review.

Goal2233 and Goal2235 collectively introduce prepared scene reuse and compact odd-parity output for ray/segment group-count primitives within the OptiX backend. The implementation adheres to app-agnostic vocabulary and strict boundary conditions, avoiding premature claims of broad performance improvements or feature completeness for higher-level applications like RayJoin.

## Verified Facts

1.  **Goal2233 adds prepared scene reuse:**
    *   The native ABI in `src/native/optix/rtdl_optix_prelude.h` and `src/native/optix/rtdl_optix_api.cpp` explicitly exposes `rtdl_optix_prepare_ray_segment_group_count_2d`, `rtdl_optix_run_prepared_ray_segment_group_count_2d`, and `rtdl_optix_destroy_prepared_ray_segment_group_count_2d`.
    *   `src/rtdsl/optix_runtime.py` provides `PreparedOptixRaySegmentGroupCount2D` as a context manager, utilizing these native functions.
    *   The report `docs/reports/goal2233_prepared_ray_segment_group_count_2026-05-17.md` confirms this purpose, and `tests/goal2233_prepared_ray_segment_group_count_test.py` validates their presence and structure.

2.  **Goal2235 adds compact odd-parity output:**
    *   The native ABI in `src/native/optix/rtdl_optix_prelude.h` and `src/native/optix/rtdl_optix_api.cpp` includes `rtdl_optix_run_prepared_ray_segment_group_odd_parity_2d`.
    *   `src/native/optix/rtdl_optix_workloads.cpp` contains the logic for filtering out even-parity rows.
    *   `src/rtdsl/optix_runtime.py` exposes `PreparedOptixRaySegmentGroupCount2D.run_odd_parity`.
    *   The report `docs/reports/goal2235_prepared_ray_segment_odd_parity_2026-05-17.md` details this functionality, and `tests/goal2235_prepared_ray_segment_odd_parity_test.py` confirms its implementation and app-agnostic nature.

3.  **The API vocabulary is app-agnostic:**
    *   Across all reviewed C++ and Python source files (`src/native/optix/rtdl_optix_prelude.h`, `src/native/optix/rtdl_optix_api.cpp`, `src/native/optix/rtdl_optix_workloads.cpp`, `src/rtdsl/optix_runtime.py`), the new functions and Python bindings consistently use generic terms like "rays," "segments," "group ids," "counts," and "parity."
    *   Explicit checks in both `docs/reports/goal2233_prepared_ray_segment_group_count_2026-05-17.md` (App-Agnostic Check) and `docs/reports/goal2235_prepared_ray_segment_odd_parity_2026-05-17.md` (Design) confirm the absence of application-specific terms such as RayJoin, PIP, polygon, county, map, or spatial-join logic in the API.

4.  **Pod evidence:**
    *   **Goal2233 prepared full-count median:** `0.820912s` (`new_prepared_median_sec` from `docs/reports/goal2233_prepared_ray_segment_group_count_2026-05-17.md`).
    *   **Goal2235 compact odd-parity median:** `0.282348s` (`odd_median_sec` from `docs/reports/goal2235_prepared_ray_segment_odd_parity_2026-05-17.md`).
    *   **Legacy optimized PIP median in Goal2235 probe:** `0.031503s` (`old_median_sec` from `docs/reports/goal2235_prepared_ray_segment_odd_parity_2026-05-17.md`).
    *   **Compact odd-parity matched legacy positive rows exactly:** `879 rows` (`odd_rows` and `old_positive_rows` from `docs/reports/goal2235_prepared_ray_segment_odd_parity_2026-05-17.md`).

5.  **Boundary conditions:**
    *   Both `docs/reports/goal2233_prepared_ray_segment_group_count_2026-05-17.md` and `docs/reports/goal2235_prepared_ray_segment_odd_parity_2026-05-17.md` explicitly state that these goals **do not authorize** v2.0 release, broad RayJoin/PIP speedup claims, claims of fully device-resident grouped reduction, nor do they claim a completed RayJoin reproduction project.
    *   The reports consistently conclude that a more generic closed-shape membership or predicate primitive is still required for RayJoin-style PIP performance.

## Conclusion

The work for Goal2233 and Goal2235 has been implemented and validated according to the stated objectives and constraints. The code is well-tested and the reports clearly articulate the progress made and the remaining limitations, particularly regarding performance relative to optimized legacy paths and the need for further generic primitives. The app-agnostic design is maintained. The boundaries set for these goals are clearly defined and upheld throughout the documentation and implementation.