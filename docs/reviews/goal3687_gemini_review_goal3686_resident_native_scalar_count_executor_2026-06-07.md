# Independent Review: Goal3686 Resident Native Scalar-Count Executor

**Reviewer:** Gemini CLI (Autonomous Reviewer)
**Date:** 2026-06-07
**Verdict:** `accept`

## Findings by Severity

### Critical / High
*   **None.** The implementation is surgically focused and adheres to established patterns for resident native executors.

### Medium
*   **None.** The transition from the Goal3684 one-shot path to a reusable native executor is handled cleanly without leaking app-specific logic into the native layer.

### Low
*   **None.** Code quality, symbol naming, and documentation are consistent with the project's standards.

## Evidence Checked

1.  **C++ Implementation (`src/native/optix/rtdl_optix_workloads.cpp`):**
    *   Verified the `PreparedPointClosedShapeRelationStatusCorrectedScalarCountExecutor2D` struct. It correctly manages persistent `DevPtr` buffers for counters (`d_exact_count`, `d_candidate_count`, etc.) and launch parameters (`d_params`).
    *   Confirmed the `run` method resets counters via `cuMemsetD32Async` and performs the `optixLaunch` using the pre-allocated buffers.
    *   Verified the kernel logic modification in `ensure_pip_relation_status_corrected_scalar_count_pipeline`. It uses `atomicAdd` for counting and correctly implements the `exact_boundary_contact_f64` helper to enforce the exact scalar-count contract.
2.  **C++ API (`src/native/optix/rtdl_optix_api.cpp` & `src/native/optix/rtdl_optix_prelude.h`):**
    *   Verified the new `extern "C"` symbols: `rtdl_optix_prepare_point_closed_shape_membership_relation_status_corrected_scalar_count_executor_2d`, `rtdl_optix_run_point_closed_shape_membership_relation_status_corrected_scalar_count_executor_2d`, and the corresponding destroy function.
    *   The symbols are generic and follow the naming conventions for app-agnostic native primitives.
3.  **Python Integration (`src/rtdsl/optix_runtime.py`):**
    *   Verified the `PreparedOptixRelationStatusCorrectedScalarCountExecutor2D` class. It correctly manages the lifecycle of the native executor handle and provides a clean `run()` method returning a summary dictionary.
    *   The metadata produced by `to_metadata()` correctly reflects the native/resident nature of the execution.
4.  **Tests (`tests/goal3686_resident_native_scalar_count_executor_test.py`):**
    *   Successfully executed the source audit tests.
    *   Verified that the tests correctly audit symbol presence, buffer reuse patterns in C++, and Python API exposure.
5.  **Benchmark Results (`docs/reports/goal3686_resident_native_scalar_count_executor_a5000/summary.json`):**
    *   The `summary.json` confirms that the resident native path successfully matched the reference exact count (47262) and showed a performance improvement (`hot_median_sec`) over the previous resident Numba implementation.

## Claim-Boundary Assessment

1.  **Generic/App-Agnostic:** **ACCEPTED.** The symbols and C++ logic do not contain any app-specific (RayJoin, CDB, etc.) naming or specialized logic. The executor is a generic "closed-shape membership relation-status corrected scalar count" primitive.
2.  **Buffer Reuse:** **ACCEPTED.** The `PreparedPointClosedShapeRelationStatusCorrectedScalarCountExecutor2D` struct in C++ explicitly holds and reuses device-memory buffers for its entire lifecycle.
3.  **Exact Scalar-Count Contract:** **ACCEPTED.** The OptiX kernel logic (verified in `rtdl_optix_workloads.cpp`) performs the exact boundary correction on the device, avoiding dense boundary-row materialization while maintaining mathematical correctness.
4.  **Speedup Wording:** **ACCEPTED.** Both the report and the Python metadata (`public_speedup_claim_authorized: False`) correctly state that this work does not yet authorize new public speedup wording or whole-app claims.

## Summary

Goal3686 successfully matures the exact scalar-count correction logic introduced in Goal3684 by providing a resident native executor. This reduces host-to-device overhead and avoids expensive Numba-side continuation for dense boundary rows, fulfilling the performance and architectural requirements for v0.4.
