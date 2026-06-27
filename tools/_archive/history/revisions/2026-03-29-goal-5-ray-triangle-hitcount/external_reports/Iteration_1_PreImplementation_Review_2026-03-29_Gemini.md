# Iteration 1 Pre-Implementation Review

**Date:** 2026-03-29
**Model:** Gemini (Acting as requested gemini-3.1-pro-preview)
**Reviewer:** Gemini
**Round:** 2026-03-29-goal-5-ray-triangle-hitcount

### Model
Gemini (Targeting gemini-3.1-pro-preview profile as requested)

### Agreement
**Yes, I agree this should be Goal 5.** 
Extending RTDL to support 2D finite ray queries against triangles is a highly logical progression from the current point-in-polygon join workloads. It naturally tests the flexibility of the RTDL DSL design by introducing new geometric primitives (`rt.Triangles`, `rt.Rays`), a new relationship predicate (intersection/hit), and a different output structure (per-ray hit counts instead of matching pairs). 

### Review Method
During the implementation review phase, I will evaluate the changes using the following method:
1. **API & Language Surface Analysis:** Ensure `rt.Triangles` and `rt.Rays` are introduced idiomatically and maintain consistency with existing dataset definitions (like `rt.Points` and `rt.Polygons`). I will verify the hit-count workload contract is clearly defined.
2. **Algorithmic Validation:** Inspect the CPU reference implementation (`reference.py`) to ensure the 2D finite ray vs. triangle intersection logic is mathematically sound and handles basic edge cases reasonably within the `float_approx` constraint.
3. **Compiler/Lowering Pipeline Verification:** Trace the new workload from Python API through the IR (`ir.py`) to the lowered representation (`lowering.py`), verifying the schema updates (`rayjoin_plan.schema.json`).
4. **Codegen Inspection:** Review the generated `host_launcher.cpp` and `device_kernels.cu` for the new workload to ensure syntax validity, appropriate struct definitions for rays/triangles, and correct kernel launch parameters for a hit-counting mechanism.
5. **Documentation & Usability Testing:** I will read the updated `dsl_reference.md` and `programming_guide.md`, and then independently author the Gemini-authored example script based *only* on the provided documentation to validate its completeness.

### Required Evidence
Before agreeing that Goal 5 is complete, I will require the following evidence:
1. **Passing Test Suite:** Execution logs or verifiable test artifacts demonstrating that the compiler, lowerer, and CPU reference semantics all pass for the new ray-triangle workload.
2. **Schema and Codegen Artifacts:** A generated `plan.json`, `host_launcher.cpp`, and `device_kernels.cu` demonstrating the successful compilation of a ray-triangle program.
3. **Documentation:** Visible updates to the language reference and cookbook/examples documenting the new API primitives and how to construct a hit-counting program.
4. **Working Examples:** Both the Codex-authored and Gemini-authored examples must successfully execute their frontend compilation and pass CPU reference tests.

### Required Artifacts
Codex should archive the following artifacts for this round:
1. **Implementation Snapshot:** All modified `src/rtdsl/` files (`api.py`, `ir.py`, `types.py`, `codegen.py`, `lowering.py`, `reference.py`, etc.).
2. **Schema & Docs:** The updated `rayjoin_plan.schema.json` and any updated Markdown files in `docs/rtdl/`.
3. **Generated Code:** The `plan.json`, `host_launcher.cpp`, and `device_kernels.cu` outputs for the canonical ray-triangle example.
4. **Examples:** The Python source files for the canonical, Codex-authored, and Gemini-authored examples.
5. **Reports:** All specification, pre-implementation, and review reports generated during this revision round.

### Risks/Boundaries
- **Precision Limits:** As we are constrained to `float_approx`, exact collinear or vertex-grazing ray intersections may produce inconsistent results. The documentation and CPU reference should acknowledge this limitation rather than attempt a perfect exact-math fallback.
- **Dimensionality:** The implementation must strictly remain in 2D. Avoid introducing generic `N-dimensional` vectors or 3D structs "just in case," to prevent scope creep.
- **Scope Expansion:** Ensure the execution constraint is respected; we are only generating the GPU code, not setting up an environment to execute and benchmark the CUDA kernels.

### Decision
**Approved.** Proceed with the implementation of Goal 5 as specified. Once the implementation is complete, provide the implementation report and the documentation context so I can author my example and perform the final review.
