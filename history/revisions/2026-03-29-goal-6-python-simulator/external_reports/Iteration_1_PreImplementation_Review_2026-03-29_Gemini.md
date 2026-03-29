I will begin by reading the Goal 6 specification and the Codex pre-implementation report to understand the proposed Python simulator and its intended scope.
I'll now examine `src/rtdsl/reference.py` and `src/rtdsl/api.py`, along with an example kernel, to understand the current implementation and determine how the proposed `run_cpu` API should be integrated.
I've analyzed the current system and have a clear understanding of how `rt.run_cpu(kernel_fn, **inputs)` would function. To further refine this, I'll examine `src/rtdsl/ir.py` and `src/rtdsl/types.py` to understand the definitions of `CompiledKernel` and `GeometryType`, which are essential for the simulator's implementation.
I have completed the review of the Goal 6 proposal for the Python RT simulator. Based on the project's current state and the provided specifications, here is the consensus report.

### 1. Model
**Reviewer:** Gemini CLI (Autonomous Agent)

### 2. Scope Assessment
The scope is **well-defined and appropriate**. Focusing on the four established workloads (`lsi`, `pip`, `overlay`, `ray_tri_hitcount`) ensures the simulator provides immediate value without expanding into unverified features. Leveraging the existing `src/rtdsl/reference.py` as the "ground truth" for CPU semantics is a sound architectural decision that avoids duplicating logic.

### 3. API Assessment
The proposed `rt.run_cpu(kernel_fn, **inputs)` is a **highly idiomatic and intuitive** interface for a Python-based DSL.
*   **Input Flexibility:** I recommend that `inputs` support both lists of dictionaries (matching `Layout` field names) and the reference dataclasses defined in `reference.py`.
*   **Validation:** The API must perform strict validation. It should verify that:
    1.  All required inputs defined in the kernel are present in `**inputs`.
    2.  The keys in dictionary inputs match the `Layout` fields for the corresponding `GeometryType`.
    3.  Data types are compatible (e.g., numeric values for `f32` fields).
*   **Result Format:** The returned results should be consistent with the `EmitOp` fields and the output format of the reference functions (tuples of dictionaries).

### 4. Recommended Review Method
I recommend a three-tiered review approach:
1.  **Contract Verification:** Automated tests to ensure `run_cpu` correctly extracts the kernel's intent (inputs, predicate, fields) and maps it to the appropriate reference function.
2.  **Cross-Validation:** Comparative tests where `run_cpu` results are checked against hard-coded geometric "golden" results for small, edge-case datasets (e.g., parallel lines, points on polygon boundaries).
3.  **Negative Testing:** Robust verification of error paths. Ensure that passing a `Segment` to a `Point` input or omitting a required field results in a descriptive `ValueError`.

### 5. Required Completion Evidence
To accept Goal 6 as complete, the following should be provided:
*   **New Test Suite:** `tests/rtdsl_simulator_test.py` covering happy paths for all 4 workloads and various validation failure scenarios.
*   **Interactive Demo:** `examples/rtdl_simulator_demo.py` demonstrating a user-friendly end-to-end execution of an RTDL kernel.
*   **Documentation:** An update to `docs/rtdl/programming_guide.md` detailing the `run_cpu` API and providing a "Quick Start" for local execution.
*   **Integration:** Successful execution of the simulator within the existing test environment on a non-GPU (Mac) host.

### 6. Risks / Corrections
*   **Polygon Representation Mismatch:** There is a discrepancy between `src/rtdsl/reference.py` (where `Polygon` contains inline vertices) and `src/rtdsl/types.py` (where `Polygon2DLayout` uses `vertex_offset` and `vertex_count`). The simulator implementation must bridge this: it should likely accept a `vertices` buffer as an auxiliary input or allow passing a `Polygon` dataclass that it then deconstructs to match the lowered plan logic.
*   **Precision Semantic Gap:** While standard Python `float` is sufficient for a simulator, the simulator should warn or log if a kernel requests a precision level (e.g., `exact`) that the current CPU reference does not yet support beyond `float_approx`.
*   **State Management:** Ensure that `run_cpu` does not leave the `_context_stack` in a corrupted state if the `kernel_fn` or the simulation fails.

### 7. Decision
**Approved with corrections.** The implementation should proceed, specifically addressing the Polygon representation discrepancy noted above before finalizing the API.
