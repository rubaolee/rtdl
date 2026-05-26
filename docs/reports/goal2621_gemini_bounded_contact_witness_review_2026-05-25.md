Based on the inspection of the provided files and documentation, here is the review for the **Goal2621 bounded contact-witness benchmark candidate**:

### Verdict: Accept
The candidate is technically sound, follows the repository's architectural patterns for "candidate benchmark" promotion, and correctly exercises the `COLLECT_K_BOUNDED` primitive. The implementation provides a clear separation between domain-specific application logic and generic engine primitives.

### Engine App-Agnosticism: Yes
The engine remains strictly app-agnostic. 
- **Generic Primitives:** The app uses `COLLECT_K_BOUNDED`, which is implemented as a generic `int64` row collection operation.
- **Domain Logic Boundary:** All collision-specific vocabulary (contact manifold, witness rows, triangle-intersection) and logic are contained within the Python application (`rtdl_contact_manifold_benchmark_app.py`). 
- **Row Schema:** The engine only sees a generic `int64` row schema `(query_group_id, query_triangle_id, scene_triangle_id)`. 
- **Validation:** The test `test_app_source_does_not_call_collision_specific_native_symbols` confirms that no collision-specific native symbols are invoked by the application.

### `COLLECT_K_BOUNDED` Overflow Semantics: Exact Fail-Closed
The overflow semantics are **exact fail-closed**.
- **Policy:** The application and documentation define the policy as `fail_closed_before_result_materialization`.
- **Implementation:** The `collect_k_reference_payload` uses `validate_collect_k_bounded_result` to ensure that if capacity is exceeded, an error is raised before any partial data is returned.
- **Verification:** Test `test_overflow_fails_closed_without_partial_rows` explicitly asserts that a `RuntimeError` is raised with `partial_result_returned=False` when capacity is exceeded, preventing silent truncation or partial results.

### Missing Gates Before Promoted Benchmark Wording
The following gates must be cleared before the "candidate" status is removed and promoted benchmark wording is authorized:
1.  **Embree Parity:** Verification that the same row schema and fail-closed contract hold when running on the Embree backend.
2.  **OptiX Parity:** Verification on an NVIDIA pod to ensure backend parity for OptiX.
3.  **Baseline Comparison:** More rigorous comparison against a non-RTDL baseline (e.g., a direct CUDA/BVH or specialized physics-library implementation) to justify the "benchmark" claim.
4.  **Claude Review:** As noted in the report's promotion gates.
5.  **3-AI Consensus:** A formal consensus file signed by all three AI agents (Gemini, Claude, and the internal Consensus agent) accepting the promoted wording.

### Required Fixes
No immediate code or documentation fixes are required for this candidate to be accepted into the repository as a **benchmark candidate**. The implementation correctly reflects the current experimental status of `COLLECT_K_BOUNDED` and maintains the necessary boundaries.

---
**Summary of Reviewed Files:**
- `examples/v2_0/.../rtdl_contact_manifold_benchmark_app.py`: Correctly implements the generic collection path.
- `tests/goal2621_..._test.py`: Exhaustively covers the fail-closed and agnosticism requirements.
- `docs/reports/goal2621_...md`: Accurately describes the state and gates.
- `docs/rtdl_primitive_catalog.md` & `docs/application_catalog.md`: Properly categorized under "Experimental" and "Candidate".
- `scripts/goal2617_surface_smoke.py`: Successfully integrated into the surface smoke test suite.
