RTDL Embree Baseline Plan Review Report

1. Is the scope well-defined enough to start implementation?
Yes. The plan identifies four specific workloads (lsi, pip, overlay, ray_tri_hitcount) and two backends (CPU and Embree) as the core targets. The 10-step process provides a clear path from contract definition to final archival. Success conditions for each step are explicit, and the relationship between this baseline and the future OptiX implementation is clearly articulated. The scope is bounded and actionable.

2. What specific criteria should be used later to review implementation work for this baseline?
- Numerical Parity: The rt.run_embree() results must match rt.run_cpu() within defined precision limits for all four baseline workloads using identical inputs.
- ABI Consistency: A single, unified runtime ABI must be used by both backends, ensuring that dataset loading and record emitting logic are not backend-specific.
- Test Coverage: Automated comparison tests must exist for every workload in the baseline set.
- Tooling Maturity: A benchmark harness must be able to generate timing data and save raw results for both backends across multiple datasets.
- Documentation Completeness: The "how to" for kernel authoring and runtime execution must be verified as usable by both human and AI agents (Codex/Gemini).
- Performance Baseline: Execution times for the Embree backend must be recorded as the pre-GPU performance standard.

3. What gaps, ambiguities, or ordering problems remain?
- Data Schemas: While Step 2 mandates freezing geometry types and record fields, the plan does not yet contain the actual schema definitions. These must be the first technical artifacts produced.
- Precision Definitions: The "allowed precision mode" is mentioned but not specified (e.g., handling of float32 vs float64 for spatial intersections).
- Dataset Specification: The "representative RayJoin-aligned datasets" mentioned in Step 5 lack specific scale or source identifiers (e.g., row counts or specific file references).
- Approximation Limits: Step 8 mentions documenting "what is still approximate," which implies known limitations in the Embree or CPU implementations that aren't yet categorized.

4. If acceptable, what conditions would constitute consensus to begin execution?
- Formal adoption of the four workloads (lsi, pip, overlay, ray_tri_hitcount) as the exhaustive baseline set.
- Agreement that rt.run_cpu() serves as the ground-truth semantic reference.
- Commitment to producing the ABI and Schema definitions (Step 2 and 3) before expanding the test or benchmark code.
- Validation that the proposed Embree backend (native C++/Embree) is currently buildable and linkable within the existing development environment.

The plan is acceptable for immediate execution of Step 1 and Step 2.
