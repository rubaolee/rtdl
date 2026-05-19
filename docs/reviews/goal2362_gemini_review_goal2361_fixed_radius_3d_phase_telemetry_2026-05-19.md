# Independent Gemini Review: Goal2361 Fixed-Radius 3D Phase Telemetry

**Reviewer:** Gemini (Independent AI Agent)
**Date:** 2026-05-19
**Verdict:** accept

This is an independent Gemini review, distinct from any Codex review.

## Review Questions and Answers

### 1. Does Goal2361 remain app-agnostic and avoid RTNN-specific native ABI or benchmark-specific continuation?
**Answer:** Yes, Goal2361 remains app-agnostic and successfully avoids RTNN-specific native ABI or benchmark-specific continuation.
*   **Evidence:** The telemetry is implemented directly within the generic `fixed_radius_neighbors_3d` OptiX primitive in `src/native/optix/rtdl_optix_workloads.cpp` and exposed via a generic C ABI (`rtdl_optix_fixed_radius_neighbors_3d_get_last_phase_timings`) in `src/native/optix/rtdl_optix_prelude.h`. The naming conventions (`fixed_radius_3d`) are generic and do not refer to RTNN. The `test_modes_are_generic_and_cover_current_execution_paths` in `tests/goal2361_fixed_radius_3d_phase_telemetry_test.py` explicitly asserts `self.assertNotIn("RTNN", workloads)`. Furthermore, the report `docs/reports/goal2361_fixed_radius_3d_phase_telemetry_2026-05-19.md` explicitly states: "This is not RTNN-specific: it instruments the generic `fixed_radius_neighbors_3d` OptiX primitive." and "This goal does not authorize: RTNN parity; a broad RT-core speedup claim; a claim that the default path is RT-core accelerated; a v2.2 release claim." The `scripts/goal2348_rtnn_v2_2_external_runner.py` also uses the `get_last_fixed_radius_neighbors_3d_phase_timings` for a generic 3D neighbors smoke test, with claim boundaries preventing RTNN-specific or broad speedup claims.

### 2. Are the new phase timing fields generic and useful for the current `fixed_radius_neighbors_3d` OptiX paths?
**Answer:** Yes, the new phase timing fields are generic and useful for the current `fixed_radius_neighbors_3d` OptiX paths.
*   **Evidence:** The C++ implementation in `src/native/optix/rtdl_optix_workloads.cpp` defines `thread_local` variables (e.g., `g_optix_last_fixed_radius_3d_prepare_s`, `g_optix_last_fixed_radius_3d_upload_s`) that correspond to logical stages of a fixed-radius neighbor search, including `mode` to indicate execution strategies (e.g., `all_pairs_cuda`, `uniform_cell_compact`, `simple_rt_traversal`). These fields are exposed through a dedicated Python helper `rt.get_last_fixed_radius_neighbors_3d_phase_timings()`. The report `docs/reports/goal2361_fixed_radius_3d_phase_telemetry_2026-05-19.md` uses these specific timings to analyze performance and identify bottlenecks, validating their usefulness for diagnostic purposes across different execution paths of `fixed_radius_neighbors_3d`. The `test_modes_are_generic_and_cover_current_execution_paths` test also confirms the different modes.

### 3. Are the pod artifacts consistent with the report, especially the signal that native count/write phases are milliseconds while full harness wall time remains seconds?
**Answer:** Yes, the pod artifacts are entirely consistent with the report.
*   **Evidence:** Inspection of the JSON pod artifacts (`docs/reports/goal2361_rtdl_3d_neighbor_phase/rtdl_grid_phase_raw_repeat_3d_262144_r002_k50.json` and `docs/reports/goal2361_rtdl_3d_neighbor_phase/rtdl_grid_phase_raw_repeat_3d_65536_r002_k50.json`) shows that the `elapsed_sec` (full harness wall time) values are in seconds (e.g., 3.329s for 262,144 points), while the sum of `phase_timings` (native phases) is significantly smaller, in milliseconds (e.g., ~0.112s for 262,144 points). The individual phase timings within the JSON files also confirm values consistent with milliseconds. This matches the report's conclusion that "the measured native count/write phases are not the main 262k wall-time cost" and that "Python-side loading, packing, row view setup, and host exact-normalization dominate the end-to-end harness wall time."

### 4. Are the claim boundaries strict enough around RT-core acceleration, RTNN parity, and v2.2 release readiness?
**Answer:** Yes, the claim boundaries are strict enough.
*   **Evidence:** The "Claim Boundary" section of `docs/reports/goal2361_fixed_radius_3d_phase_telemetry_2026-05-19.md` is explicit and comprehensive in disallowing broad claims. It states: "This goal authorizes a narrow diagnostic claim: RTDL can now explain where time goes inside the current generic 3D bounded-neighbor primitive. It is not a release claim." And "This goal does not authorize: RTNN parity; a broad RT-core speedup claim; a claim that the default path is RT-core accelerated; a v2.2 release claim." The `test_report_keeps_next_step_as_prepared_generic_primitive` in the test file confirms these phrases are present in the report. This level of explicit disclaimers makes the claim boundaries sufficiently strict.

### 5. Is the next-step conclusion reasonable: prioritize explicit prepared bounded-neighbor search and lower-overhead row continuation/normalization before deeper RT-core experiments?
**Answer:** Yes, the next-step conclusion is reasonable and well-supported by the telemetry.
*   **Evidence:** The "Next Step" section of `docs/reports/goal2361_fixed_radius_3d_phase_telemetry_2026-05-19.md` states that "the telemetry says the first prepared-handle work should prioritize reusable host/device grid preparation and lower-overhead row continuation / normalization before deeper RT-core experiments." This directly follows from the observation in the "Pod Evidence" section that Python-side overheads (loading, packing, row view setup, host exact-normalization) dominate the end-to-end wall time, overshadowing the native phase timings. The `docs/reports/goal2357_v2_2_rtnn_uniform_cell_neighbor_step_2026-05-18.md` also explicitly lists "phase telemetry for pack, prepare, launch, copy, and normalization (Goal2361 adds the first fixed-radius 3D timing probe)" as a required addition for the next generic v2.2 primitive (`prepared_bounded_neighbor_search_3d`). This integrated approach makes the prioritization entirely logical and data-driven.

---

**Verdict Justification:**

Based on a thorough review of the provided documentation, source code, and test cases, Goal2361 successfully implements phase telemetry for the `fixed_radius_neighbors_3d` OptiX primitive in an app-agnostic manner. The telemetry fields are generic and useful for diagnostics, and the collected pod artifacts consistently support the report's findings regarding performance distribution. The claim boundaries are appropriately strict, and the proposed next steps are a logical consequence of the telemetry results.
