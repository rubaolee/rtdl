# Critical Review: RTDL Goal2657 v2.4/v2.5 Partner Roadmap

## 1. Verdict
**Accept with Fixes.**

The roadmap is architecturally sound and correctly prioritizes the preservation of the RT-core performance advantage over "ease-of-use" drift. However, specific "blocking" clarifications are required to ensure the v2.4 infrastructure work does not expand into a general-purpose memory manager and that v2.5 performance gates are empirically rigorous.

---

## 2. Blocking Issues
*   **Scope Creep in v2.4 Buffer Stabilization:** Goal 1 ("Stabilize typed host/device buffer descriptors") is currently worded broadly enough to invite a generic GPU memory management layer. This must be restricted to **"RTDL-Specific Handoff Descriptors."** RTDL must not attempt to solve general DLPack/CUDA-array-interface integration beyond what is required to pass columns to and from RTDL primitives.
*   **Verification of Overhead on Low-Margin Benchmarks:** The "10% tolerance" gate (Gate 2) is dangerous for low-margin benchmarks like **Hausdorff (3.29x)** or **Robot Collision (5.29x)**. A 10% loss in the *traversal* phase might be acceptable, but protocol overhead in v2.4 could easily erase the actual advantage.
    *   *Required Fix:* v2.4 deliverables must include a "Protocol Overhead Audit" that specifically measures the latency delta of the new prepared-session/buffer-descriptor path on the three benchmarks with the lowest speedup factors.
*   **Regression CI Mandate:** The v2.4 Exit Gate mentions a "regression runner," but it does not mandate its integration into the CI/CD pipeline.
    *   *Required Fix:* Explicitly state that the v2.4 Exit Gate requires the regression runner to be integrated into the automated test suite, preventing any future partner work from silently regressing the v2.3 performance basis.

---

## 3. Non-Blocking Issues & Wording Improvements
*   **Clarification of "Codex Position":** The roadmap uses the phrase "Codex recommends." Given the 3-AI consensus requirement, this should be strengthened to **"Codex Architecture Mandate"** to ensure it carries appropriate weight during implementation.
*   **Phase Timing Granularity:** Goal 5 ("Make phase timing mandatory") is excellent. Recommendation: Standardize the output format (e.g., JSON) for these timings so that the "regression runner" can automatically generate "Speedup vs. Overhead" charts across releases.

---

## 4. Performance Basis Preservation (10 Benchmark Apps)
**The roadmap correctly preserves the performance basis.**
*   It explicitly names the 10 benchmark apps and their current OptiX-vs-Embree ratios as the "Regression Basis" (Gate 1).
*   The "10-20% Slower = Opt-in Only" and ">20% Slower = Rejected" gates (Gates 3 and 4) provide a clear quantitative barrier against "convenience-driven performance regression."
*   It correctly identifies that RTDL/OptiX must remain responsible for the core `optixTrace` traversal, preventing partners (Triton/Numba) from attempting to reimplement the RT logic in a less-optimized way.

---

## 5. Justification of Triton-First / Numba-Secondary
**The ordering is highly justified.**
*   **Triton First:** Pragmatic and technically aligned. Triton excels at the exact "segmented reduction/compaction" workloads (segmented sums, counts, top-k) that RTDL primitives currently offload to CuPy or custom C++. Its native integration with the PyTorch/DLPack ecosystem matches the user profile for high-performance RT-core Python programming.
*   **Numba Secondary:** Correctly identified as "exploratory." Numba's performance for high-throughput GPU continuation is often less predictable and its interaction with the OptiX/RTDL stream management is more complex than Triton's kernel-centric model.

---

## 6. Risk of App-Specific Semantics in Native Engine
**The risk is well-mitigated but requires vigilant enforcement.**
*   Gate 7 and v2.4 Goal 6 ("Audit native-engine vocabulary") provide a strong defensive posture against app-specific bloat.
*   The roadmap correctly pushes specialization into "generic continuation primitives" (e.g., "segmented count" instead of "DBSCAN core-point count").
*   *Observation:* The v2.5 scope for Triton specifically forbids RayDB or DBSCAN-specific native logic, which is the correct boundary to protect the engine's generality.

---

## 7. Required Changes for 3-AI Consensus-Ready Status
To reach 3-AI consensus-ready status, the following updates must be made to `docs/reports/goal2657_v2_4_v2_5_partner_roadmap_2026-05-27.md`:
1.  **Refine v2.4 Goal 1:** Add: "RTDL will not implement a general-purpose memory manager; descriptors are strictly for RTDL primitive handoff."
2.  **Update v2.4 Exit Gate:** Add: "The regression runner must be integrated into the project's CI/CD pipeline and report 'Protocol Overhead' as a primary metric."
3.  **Strengthen Gate 2:** Add a clause: "For benchmarks with speedups < 5x (Hausdorff, Robot Collision, Barnes-Hut), protocol overhead must be tracked with a zero-tolerance policy for total execution time regression."
4.  **Confirm Phase Splits:** Explicitly state that "Triton-accelerated continuations" must be reported as a separate timing phase from "RTDL Traversal" to ensure we are measuring the correct optimization.
