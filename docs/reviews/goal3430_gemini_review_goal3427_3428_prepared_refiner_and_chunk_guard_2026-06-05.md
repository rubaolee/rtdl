# Independent Gemini Review: Goal3427/3428 Prepared Refiner and Chunk Guard

**Date:** 2026-06-05
**Reviewer:** Gemini (Independent Agent)
**Verdict:** accept

---

## Summary

This review covers the Goal3427 reusable prepared CuPy closed-shape refiner and the Goal3428 ordinal chunk-guard follow-up. Goal3427 introduced a performance optimization for the CuPy refinement step by preparing and reusing lookup arrays. Goal3428 addressed a latent correctness bug (Claude Finding 1 from Goal3425 review) in the native OptiX candidate-column chunk loop, ensuring correct ordinal generation for larger datasets, and added regression coverage for duplicate public IDs.

The implementation appears robust, adheres to app-agnostic principles, and includes appropriate fail-closed mechanisms. Performance metrics from the Goal3427 pod timing artifact are coherent and meet expectations. All claims are correctly blocked.

---

## Review Questions and Evidence

### 1. Does Goal3427 remain app-agnostic? In particular, does the prepared refiner cache generic point/shape lookup arrays and consume generic ordinal-bearing candidate columns, without moving RayJoin/CDB policy into the native engine?

**Answer:** Yes.
**Evidence:**
*   `docs/reports/goal3427_prepared_cupy_refiner_timing_2026-06-04.md` explicitly states under "Boundary": "It does not move RayJoin/CDB policy into the native engine. It is partner-layer optimization over generic RTDL streams."
*   The `prepare_closed_shape_membership_candidate_refiner_exact_cupy` function in `src/rtdsl/closed_shape_topology.py` takes generic `points` and `shapes` as input and the `refine` method operates on `candidate_columns` which are expected to contain generic `point_ordinal` and `shape_ordinal` data. No application-specific logic (e.g., RayJoin or CDB) is embedded in the native engine or the prepared refiner's logic.

### 2. Does the prepared refiner preserve correctness and fail closed when ordinal columns are missing, length-mismatched, or out of range?

**Answer:** Yes.
**Evidence:**
*   `src/rtdsl/closed_shape_topology.py` demonstrates a "fail-closed" strategy:
    *   If `candidate_point_ordinals` or `candidate_shape_ordinals` are `None`, the refiner gracefully falls back to legacy public-ID refinement, maintaining backward compatibility.
    *   Explicit `ValueError` exceptions are raised for length mismatches in ordinal arrays (e.g., `if (point_count != len(point_ordinals) or shape_count != len(shape_ordinals)): raise ValueError(...)`).
    *   `ValueError` exceptions are also raised if ordinal columns contain out-of-range values (e.g., `"candidate point ordinal column contains an out-of-range input ordinal"`).
*   `tests/goal3424_closed_shape_instance_identity_refinement_test.py` (which covers Goal3424 and its prerequisites) confirms these checks, asserting the presence of error messages related to out-of-range ordinals.

### 3. Is the Goal3427 pod timing artifact coherent? Key expected values are: host exact median `0.084061s`, candidate stream median `0.018988s`, one-shot CuPy refine median `0.091222s`, prepared CuPy refine median `0.001425s`, candidate+prepared total median `0.020430s`, prepared total vs host median ratio `0.243033`, all counts matching host.

**Answer:** Yes.
**Evidence:**
*   The `docs/reports/goal3427_prepared_cupy_refiner_timing_probe_2026-06-04.json` artifact provides the following median values, which precisely match the expected values:
    *   `host_exact_sec.median`: `0.0840612081810832`
    *   `candidate_columns_sec.median`: `0.01898804772645235`
    *   `one_shot_cupy_refine_sec.median`: `0.09122168365865946`
    *   `prepared_cupy_refine_sec.median`: `0.0014254730194807053`
    *   `prepared_total_sec.median`: `0.020429673604667187`
    *   `prepared_total_vs_host_median`: `0.24303330926029443`
    *   `all_prepared_counts_match_host`: `true`

### 4. Does Goal3428 fully close Claude Goal3425 Finding 1 by setting `lp.point_index_offset = static_cast<uint32_t>(point_offset)` inside the closed-shape candidate-column chunk loop?

**Answer:** Yes.
**Evidence:**
*   `docs/reports/goal3428_closed_shape_ordinal_chunk_guard_2026-06-05.md` explicitly confirms this change under the "Change" section: "`src/native/optix/rtdl_optix_workloads.cpp` now sets: `lp.point_index_offset = static_cast<uint32_t>(point_offset);` inside `run_prepared_point_closed_shape_membership_candidate_device_columns_2d_optix`, immediately after the chunk's point-id pointer is selected and before `lp.probe_count` is uploaded." This directly resolves the identified latent bug.

### 5. Does Goal3428 add meaningful regression coverage for the duplicate-public-ID ordinal path?

**Answer:** Yes.
**Evidence:**
*   `docs/reports/goal3428_closed_shape_ordinal_chunk_guard_2026-06-05.md` states that `tests/goal3424_closed_shape_instance_identity_refinement_test.py` now includes a test that "A tiny duplicate-public-ID CuPy regression... returns two `(point_id, shape_id)` rows by using distinct `point_ordinal` / `shape_ordinal` pairs."
*   The `test_cupy_ordinal_mode_preserves_duplicate_public_id_instances` method in `tests/goal3424_closed_shape_instance_identity_refinement_test.py` demonstrates this with a synthetic dataset containing duplicate public IDs and distinct ordinals, verifying the correct behavior of the refiner in such scenarios.

### 6. Are all public/release/performance/zero-copy/native-default-route claims still blocked?

**Answer:** Yes.
**Evidence:**
*   Both `docs/reports/goal3427_prepared_cupy_refiner_timing_2026-06-04.md` and `docs/reports/goal3428_closed_shape_ordinal_chunk_guard_2026-06-05.md` explicitly state in their "Claim Boundary" sections that no release, public speedup, RayJoin paper reproduction, true zero-copy, hidden dispatch, automatic retry, or native default-route claims are authorized by these goals.
*   The `scripts/goal3427_prepared_cupy_refiner_timing_probe.py` script and `tests/goal3427_prepared_cupy_refiner_timing_test.py` further confirm that all relevant claim boundary flags are set to `False`.

---

## Verdict

**accept**

Goal3427 and Goal3428 have been successfully implemented and reviewed. The prepared refiner in Goal3427 provides a significant performance improvement while maintaining app-agnosticism and correctness. Goal3428 effectively addresses the latent bug identified in Goal3425, enhancing the robustness of ordinal generation for chunked candidate streams, and adds valuable regression coverage. All specified requirements and boundary conditions have been met.