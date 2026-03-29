# RTDL Verification Report: v0.1-alpha (Internal)

**Date:** Sunday, March 29, 2026  
**Status:** **FUNCTIONAL PROTOTYPE** (Narrow Path Verified)  
**Baseline:** `make test` (4/4 PASS), `make run-rtdsl-py` (SUCCESS)

---

### 1. Executive Summary
The current version of RTDL successfully implements a "narrow path" compiler from a Python DSL to OptiX/CUDA skeleton code for segment-vs-segment spatial joins. The architecture (DSL → IR → Lowering → Codegen) is sound and follows the vision described in the documentation. However, there is a **critical semantic mismatch** between the DSL's "exact" precision claim and the floating-point implementation in the generated kernels.

---

### 2. Technical Findings Matrix

| ID | Component | Severity | Category | Finding |
| :--- | :--- | :--- | :--- | :--- |
| **RTDL-01** | **Codegen** | **HIGH** | **Over-claim** | DSL surface accepts `precision="exact"`, but generated CUDA uses `float` math with a hardcoded epsilon (`1.0e-7f`). This does not provide the robustness guaranteed by "exact" spatial joins. |
| **RTDL-02** | **Lowering** | **MEDIUM** | **Rigidity** | `lowering.py` is effectively a template for one workload. It throws `ValueError` for any geometry other than `segments`, even though `Points` and `Polygons` are defined in the types system. |
| **RTDL-03** | **DSL/IR** | **MEDIUM** | **Validation** | Layout field validation happens late in the lowering phase. Providing a `Segment2D` layout with non-standard field names (e.g., `x_start` instead of `x0`) causes an error only after compilation has "succeeded." |
| **RTDL-04** | **Artifacts** | **LOW** | **Stale/Empty** | `host_launcher.cpp` contains only print statements. It does not implement any of the `host_steps` (OptiX module creation, SBT assembly) described in the IR and README. |
| **RTDL-05** | **Makefile** | **LOW** | **Redundancy** | `make build` creates an empty `build/` directory that is never utilized by the Python toolchain or the code generator. |

---

### 3. Subsystem Review

#### Python DSL & IR (`src/rtdsl/api.py`, `ir.py`)
*   **Status:** **STABLE**.
*   **Verification:** Successfully captures user intent and transforms it into a structured `CompiledKernel`.
*   **Assumption Check:** The `_context_stack` correctly prevents DSL operations from running outside of a `@rt.kernel` decorated function.

#### RayJoin Lowering (`src/rtdsl/lowering.py`)
*   **Status:** **FRAGILE**.
*   **Verification:** Correctly assigns "probe" and "build" roles based on user hints or default heuristics.
*   **Invalid Assumption:** Assumes all segment-join workloads use the same 4-register payload contract (`probe_index`, `build_primitive_index`, `hit_t_bits`, `hit_kind`).

#### OptiX/CUDA Codegen (`src/rtdsl/codegen.py`)
*   **Status:** **FUNCTIONAL SKELETON**.
*   **Verification:** Produces syntactically correct CUDA C++ that mirrors the IR’s layout and output schema.
*   **Correctness Bug:** `rtdl_intersect_segments` uses `fabsf(denom) < 1.0e-7f`, which is a graphics-style heuristic, not a spatial-data-layer "exact" primitive.

---

### 4. Roadmap & Milestone Alignment
The current implementation aligns with **Milestone B (Frontend and IR Coverage)** and **Milestone C (Lowering and Codegen Coverage)** for the *segment-join workload only*. 

*   **Roadmap Gap:** The system claims to cover "RayJoin workloads," but currently only supports 1 of the ~5 workloads implied by the vision document.
*   **Precision Policy Gap:** The "exactness" policy mentioned in the roadmap (Milestone E) is currently violated by the implementation.

---

### 5. Residual Risks & Testing Gaps
1.  **No Integration Test:** There is no automated check that the generated `.cu` code actually compiles with `nvcc`.
2.  **Numerical Stability:** No unit tests exist for degenerate geometries (parallel segments, zero-length segments, or T-junctions).
3.  **Buffer Safety:** The generated `rtdl_store_record` does not check for `output_records` buffer overflow during high-cardinality joins.

---

### 6. Recommendations
1.  **Immediate:** Rename `precision="exact"` to `precision="float_approx"` or add a warning until true exactness (e.g., via integer coordinates or predicates) is implemented.
2.  **Next:** Generalize `lowering.py` to support `Point-in-Polygon` (PiP) to prove the IR is truly extensible.
3.  **Short-term:** Add an integration test that runs `nvcc --preprocess` on the generated artifacts to verify syntax correctness.
