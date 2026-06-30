# Gemini Plan Review: Goal602 (v0.9.3 Full Apple RT Native Coverage)

**Date:** 2026-04-19
**Reviewer:** Gemini CLI
**Recommendation:** **ACCEPT**

## Summary

The proposed plan for `v0.9.3` honestly and feasibly scopes the completion of native Apple RT coverage for the RTDL project. By establishing a strict definition of "hardware-backed" execution and enforcing a `native_only=True` contract, the plan ensures that the Apple RT backend moves beyond a simple CPU-reference compatibility layer.

## Rationale

### 1. Honest Definition of Hardware-Backed
The plan explicitly distinguishes between native Metal/MPS RT candidate discovery and CPU-bound refinement. This clarity prevents "marketing-only" native claims and provides a clear architectural target for developers. The "Definition of Hardware-Backed" section is a strong foundation for this version.

### 2. Feasible Lowering Strategies
The technical strategy for each workload family (Geometry, Nearest-Neighbor, Graph, and DB) builds upon established project patterns (e.g., the v0.6 graph traversal model and v0.7 RT-DB spirit). Encoding non-geometric predicates as 3D triangle/segment slabs for MPS traversal is a proven path in this codebase for leveraging fixed-function RT hardware for general-purpose discovery.

### 3. Clear Honesty Boundaries
The plan includes non-negotiable boundaries that protect project integrity. Specifically, the commitment to keeping workloads unsupported in `native_only=True` if they cannot be honestly lowered to MPS ensures that correctness is never sacrificed for a "full coverage" checkmark.

### 4. Incremental and Measured Ladder
The Goal Ladder (Goal603 through Goal610) provides a logical sequence of dependencies. Starting with the Contract (Goal603) and Geometry (Goal604) before tackling the higher-difficulty Graph and DB workloads (Goal606, Goal607) is a sound engineering approach that maximizes infrastructure reuse.

## Risks and Considerations

- **Performance Overhead:** As noted in the risks, MPS-backed candidate discovery for complex predicates (like Graph/DB) might introduce overhead (encoding/decoding) that could result in lower performance than Embree in some cases. However, the plan correctly prioritizes native-discovery coverage and correctness as the primary goals for v0.9.3.
- **Complexity of Graph/DB Lowering:** These workloads are labeled as "High" difficulty. While the strategy is sound, the implementation effort for deterministic parity with CPU references should not be underestimated.

## Conclusion

The v0.9.3 plan is an honest, well-defined, and technically sound roadmap for maturing the Apple RT backend. I fully support its adoption.
