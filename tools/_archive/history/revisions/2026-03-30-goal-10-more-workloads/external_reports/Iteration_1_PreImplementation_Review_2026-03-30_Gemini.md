I will read the three specified files to understand the proposed Goal 10 plan and its technical context.
### Goal 10 More Workloads: Pre-Implementation Review

I have reviewed the Goal 10 More-Workloads Plan and the associated Codex reports. The transition from the Goal 9 "Baseline Freeze" to broadening the workload surface is the correct strategic move before introducing the complexity of the NVIDIA/OptiX backend.

#### Scope Assessment
The scope is **technically sound** for the current Embree-only phase. 
*   **Architectural Fit:** By restricting the backend to CPU/Embree, the project avoids the "cross-talk" of GPU-specific bugs while validating the DSL's ability to express more complex spatial joins.
*   **Incremental Complexity:** Adding support for mixed-geometry (`segment_polygon`) and distance queries (`point_nearest_segment`) is a natural extension of the existing BVH-based infrastructure.
*   **Completeness:** The requirement for DSL support, IR/lowering, CPU/Embree parity, and documentation ensures that these are not just "kernels" but fully integrated