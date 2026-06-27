I will begin by locating and reading the Goal 5 specification and pre-implementation report to understand the planned Ray-Triangle Hitcount implementation.
I'll read the Goal 5 specification and the pre-implementation report to understand the planned Ray-Triangle Hitcount implementation and its alignment with the existing 2D and float-approx backend.
I have reviewed the Goal 5 specification and pre-implementation report. This goal correctly identifies the next logical expansion for RTDL: moving from spatial joins to general ray-query patterns while respecting the 2D and `float_approx` constraints.

### Model
The "Ray-Triangle Hitcount" model introduces `rt.Triangles` and `rt.Rays` as first-class geometry types in RTDL. It defines a ray-triangle intersection predicate and a specialized workload contract to aggregate hit counts per ray. This extension operates within the existing 2D coordinate space and utilizes the `float_approx` precision model, maintaining compatibility with the current `rayjoin` backend family.

### Agreement
I agree that this is the correct scope for Goal 5. It builds upon the established IR and lowering infrastructure while introducing the first non-join workload pattern (per-ray aggregation), which is a significant milestone for the RTDL language's expressiveness.

### Review Method
1.  **Structural Audit:** Verify the integration of `Triangles` and `Rays` into `rtdsl/types.py`, `rtdsl/ir.py`, and `rtdsl/api.py`.
2.  **Logic Verification:** Surgically review the ray-triangle intersection math in `rtdsl/reference.py` for correctness under 2D floating-point approximations.
3.  **Lowering Path Trace:** Confirm that the `lowering.py` logic correctly maps the hit-count contract to the underlying execution plan.
4.  **Authoring Evaluation:** Peer-review both the Codex and Gemini-authored examples for idiomatic usage of the new API and successful compilation.
5.  **Documentation Audit:** Ensure the `dsl_reference.md` and `workload_cookbook.md` are updated with clear instructions for both humans and LLMs.

### Required Evidence
1.  **Execution Logs:** Successful `pytest` output for new unit tests covering geometry layouts and intersection predicates.
2.  **Compilation Artifacts:** Valid `plan.json` or lowered IR output from the canonical ray-triangle examples.
3.  **Reference Match:** Comparison of the CPU reference hit counts against a set of hand-verified ray-triangle test cases.
4.  **Doc Diffs:** Verified updates to the RTDL documentation suite.

### Required Artifacts
1.  **Authored Examples:** `examples/rtdl_ray_tri_hitcount.py` (and variants).
2.  **Test Suite:** New test files in `tests/` specifically targeting Goal 5 features.
3.  **Design Snapshots:** Lowered plans and IR representations of the new workload.
4.  **Updated Guides:** Revised `docs/rtdl/` content.

### Risks/Boundaries
*   **Boundary:** Restricted to 2D; 3D extensions are explicitly out of scope for this goal.
*   **Boundary:** `float_approx` is the only supported precision; exact geometric predicates are not required.
*   **Risk (Numerical):** Potential for inconsistent hit counts at triangle edges/vertices due to floating-point jitter; this is acceptable within the `float_approx` model but must be documented.
*   **Risk (Backend):** The `rayjoin` backend may require adjustments to handle the 1:N (ray to many triangles) aggregation efficiently compared to standard spatial joins.

### Decision
**Consensus Reached.** Proceed with the implementation of Goal 5 as specified.
