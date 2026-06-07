# Review: Goal3684 Native Relation-Status Corrected Scalar Count

**Reviewer:** Gemini CLI (Independent External Review)  
**Date:** 2026-06-07  
**Verdict:** `accept`

## Findings by Severity

### Critical
*None.*

### Major
*None.*

### Minor
*None.*

### Informational / Suggestions
*   **ABI Genericity:** The new native symbol `rtdl_optix_count_prepared_point_closed_shape_membership_relation_status_corrected_prepared_points_2d` and the associated summary structure `RtdlNativeClosedShapeScalarCountSummary` successfully avoid any application-specific vocabulary (e.g., "RayJoin", "county", "cdb"). This maintains a clean architectural boundary between the generic RTDL engine and the benchmarking applications.
*   **Performance:** The 3.53x speedup over the resident Numba path is a significant optimization for dense-boundary datasets. The avoidance of materializing 47k+ boundary rows is the primary driver of this improvement.

## Evidence Checked

1.  **Native API & Prelude:** Verified `src/native/optix/rtdl_optix_api.cpp` and `src/native/optix/rtdl_optix_prelude.h` for app-agnostic signatures and generic summary structures.
2.  **Workload Implementation:** Verified `src/native/optix/rtdl_optix_workloads.cpp` (lines 8439-8600 and 6155-6350) for:
    *   Avoidance of dense `PipRecord` materialization (`lp.output = nullptr`).
    *   Use of double-precision pointers for both points and vertices.
    *   Implementation of `exact_boundary_contact_f64` helper using double-precision math.
    *   Correct use of `relation_status` (Interior vs. Boundary) to drive scalar counters.
3.  **A5000 Artifact:** Verified `docs/reports/goal3684_native_relation_status_corrected_scalar_count_a5000/summary.json`:
    *   Exact count: `47262` (matches oracle).
    *   Native timing: `0.0005168` s median.
    *   Resident Numba timing: `0.0018245` s median.
    *   Verified speedup: `3.53x` (v. Resident Numba) and `6.21x` (v. One-shot Numba).
4.  **Python Test Suite:** Executed `tests/goal3684_native_relation_status_corrected_scalar_count_test.py`. All 5 tests passed, confirming ABI genericity, lack of row materialization, and claim-boundary integrity.

## Claim-Boundary Assessment

The review confirms that the claim boundaries are strictly maintained:
*   **Release:** Not authorized.
*   **Public Speedup:** Not authorized.
*   **RayJoin Reproduction:** Not authorized.
*   **Default Route Promotion:** Not authorized.

The implementation is correctly guarded by explicit Python front doors and does not modify the default behavior of the `optix_runtime.py` outside of the new opt-in route.

## Conclusion

Goal3684 successfully addresses the performance bottleneck identified in Goal3677 (dense boundary materialization) by moving the exact boundary correction into the native OptiX traversal path while maintaining an app-agnostic contract. The implementation is technically sound, the performance claims are empirically verified, and the architectural boundaries are preserved.
