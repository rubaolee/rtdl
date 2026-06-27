I will read the three specified files to assess the scope, candidate selection, and risks for the "Goal 10: More Workloads" plan.
Based on the provided documentation and pre-implementation reports, here is the assessment for **Goal 10: More Workloads**.

### Scope Assessment
The scope is well-defined as a purely additive expansion of the **Embree baseline** (CPU-only). It targets the addition of at least **two new workload families** to the existing four (`lsi`, `pip`, `overlay`, `ray_tri_hitcount`). The boundary is strictly maintained: no NVIDIA/OptiX integration and no major redesign of the current Embree architecture. This is a technically sound progression that leverages the stable Goal 9 evaluation framework to deepen the DSL's capability before moving to GPU backends.

### Candidate Selection
Three candidates are proposed, with a requirement to implement at least two:
1.  **`segment_polygon_hitcount`**: Strongest candidate for mixed-geometry validation. It reuses existing representations while testing the DSL's ability to handle disparate primitive types in a single query.
2.  **`polygon_polygon_overlap`**: Highly recommended as it deepens the "spatial join" identity of the project, moving from point-in-polygon to more complex polygon-to-polygon relationships.
3.  **`point_nearest_segment`**: A useful fallback or third addition that introduces distance-based logic (nearest-neighbor) which is distinct from the current intersection-heavy workloads.

**Recommendation**: Prioritize **`segment_polygon_hitcount`** and **`polygon_polygon_overlap`** to maximize alignment with the "RayJoin" spatial-query mission.

### Review Criteria
To judge Goal 10 complete, the following must be evidenced:
- **Functional Parity**: 100% pass rate on tests comparing CPU reference results against Embree runtime results for the new workloads.
- **Lowering Integrity**: Evidence of successful IR lowering and Embree kernel generation for the new geometry combinations.
- **Documentation**: Updated `dsl_reference.md` and new example programs in `examples/` for each added workload.
- **Dataset Integration**: Extension of `datasets.py` or existing fixtures to provide deterministic, non-trivial inputs for the new queries.

### Risks / Gaps
- **Dataset Derivation**: The plan assumes "shared dataset derivation from existing fixtures." There is a risk that existing datasets (e.g., `county_soil_overlay`) may not provide interesting or valid edge cases for `segment_polygon_hitcount` without manual curation.
- **Complexity of Polygon-Polygon**: `polygon_polygon_overlap` can become computationally expensive or require more sophisticated BVH setups in Embree than the current `pip` implementation; performance overhead should be monitored.
- **Evaluation Matrix**: While integration is requested, the plan allows for "documented rationale if deferred." This could lead to a gap in performance visibility for the new workloads.

### Final Decision
The plan is cohesive, conservative in its technical risk, and strategically aligned with the project's roadmap. The deliverables are clear and the success criteria are measurable.

**consensus to begin execution**
