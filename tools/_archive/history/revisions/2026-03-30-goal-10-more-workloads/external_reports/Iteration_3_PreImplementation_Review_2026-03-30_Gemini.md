I will now read the requested files to summarize the "Goal 10: More Workloads" planning and review state.

Based on the reviewed documentation for Goal 10 (More Workloads), here is the summary of the current planning and review state:

### Candidate Selection
The primary candidates for expansion beyond the existing `lsi`, `pip`, `overlay`, and `ray_tri_hitcount` workloads are:
*   **`segment_polygon_hitcount`**: Inputs segments and polygons to produce a hit count per segment; reuses existing geometry representations.
*   **`polygon_polygon_overlap`**: Identifies overlap pairs or boolean overlap seeds between two sets of polygons; deepens the existing overlay path.
*   **`point_nearest_segment`**: Finds the nearest segment ID and distance for each input point; provides a general spatial query workload.
*   **Selection Goal**: At least two of these families must be implemented to satisfy the Goal 10 requirement.

### Review Criteria
Acceptance of Goal 10 requires:
*   **Execution Parity**: At least two new workload families must run successfully on both the CPU reference and Embree runtimes with passing parity tests.
*   **Full Pipeline Support**: Implementation must include Python DSL support, IR/lowering, and dataset loaders (or deterministic derived datasets).
*   **Documentation & Examples**: New workloads must be supported by example programs, updated language documentation, and LLM authoring guides.
*   **Evaluation Integration**: Updated support in the evaluation matrix or a documented rationale for any deferred integration.

### Risks / Gaps
*   **Backend Limitation**: The expansion is strictly limited to the CPU/Embree path; NVIDIA/OptiX integration and RT-core benchmarking are explicit non-goals.
*   **Arithmetic Precision**: The plan avoids requirements for exact or robust arithmetic, which may limit the complexity of polygon-based workloads.
*   **Dependency**: Goal 10 assumes Goal 9 (Embree evaluation baseline) is frozen; any regressions in the existing baseline could stall new workload integration.

### Final Decision
The scope is technically sound for the current Embree-only phase, focusing on additive expansions that reuse existing geometry contracts while broadening the RTDL workload surface.

consensus to begin execution
