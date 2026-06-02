# Gemini Review: Goal3025-3028 Hausdorff Tuning

Verdict: accept

### Findings

- **Goal 3025 (Negative Design Result)**: The report correctly records that the `rtdl_rt_grouped_adaptive_reduced_nearest_witness` method is correct but slower than the existing adaptive row path (1.29s vs 0.77s at 4096 points). The decision to reject this path for promotion is well-supported by the pod evidence and correctly identifies the cost of host-orchestrated flag copies.
  - Ref: `docs/reports/goal3025_hausdorff_adaptive_reduced_pod_probe_2026-06-02.md`
- **Goal 3026 (Generic Implementation)**: The "raw row-view" surface is correctly implemented as a generic optimization. `PreparedOptixPointGroupNearestWitness2D.nearest_witness_raw` utilizes the existing point-group nearest-witness ABI without adding any Hausdorff-specific logic to the native engine.
  - Ref: `src/rtdsl/optix_runtime.py`
- **Goal 3026 (Performance Interpretation)**: The interpretation of the performance gap is fair and honest. The report acknowledges a 15-30% improvement over the old adaptive RT path while clearly stating that the method remains 9-14x slower than the dense CuPy grouped-grid reference.
  - Ref: `docs/reports/goal3026_hausdorff_raw_row_view_probe_2026-06-02.md`
- **Goal 3028 (Scale Stability)**: The extended probe across 8192, 16384, 32768, and 65536 points successfully demonstrates that the raw row-view improvement is stable (maintaining an ~18-22% gain over the old RT path). It correctly identifies that while the gap with CuPy narrows as scale increases, no crossover occurs.
  - Ref: `docs/reports/goal3028_hausdorff_raw_row_view_larger_scale_probe_2026-06-02.md`
- **Claim Boundary Consistency**: All updated documentation, including the roadmap and future to-do list, respects the established boundaries. No public speedup, v2.6 release, or broad RT-core claims are made. The "raw row-view" path is accurately labeled as the "preferred current RT path" while maintaining the CuPy reference as the fast baseline for dense exact Hausdorff.
  - Ref: `src/rtdsl/v2_6_roadmap.py`, `docs/research/future_version_to_do_list.md`, `examples/v2_0/research_benchmarks/hausdorff_xhd/README.md`

### Summary

This review accepts the evidence provided for Goals 3025 through 3028. The work successfully identifies a sub-optimal tuning path (adaptive-reduced) and a valid generic runtime optimization (raw row-view). The performance findings are reported with high integrity, distinguishing between internal RTDL improvements and the remaining performance gap relative to optimized dense CUDA-core partner code. The implementation remains strictly app-agnostic, preserving the core RTDL architecture while providing a more efficient path for applications that can consume raw row views.

### Required Fixes

- None. The artifacts and documentation are consistent and ready for use in internal v2.6 planning.

### Statement

This is an independent Gemini review distinct from Codex authoring.

---
**Recap:**
I have completed the review of Goals 3025-3028.
- Verified Goal 3025's negative result and non-promotion decision.
- Verified Goal 3026's generic implementation of raw row-view in `optix_runtime.py`.
- Verified Goal 3026's interpretation of performance gains vs. remaining CuPy gap.
- Verified Goal 3028's scale stability evidence up to 65,536 points.
- Confirmed that all roadmap, README, and to-do list updates maintain strict claim boundaries.
- No over-authorized claims or release authorizations were identified.
