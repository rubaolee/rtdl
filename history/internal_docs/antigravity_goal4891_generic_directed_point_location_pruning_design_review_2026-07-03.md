# RTDL Goal4891 Generic Directed Point-Location Pruning Design Review

**Date:** 2026-07-03
**Reviewer:** Antigravity AI
**Verdict:** `approve_with_amendments`

---

## 1. Executive Summary

This review evaluates the design proposal for **Goal4891 (Generic Directed Point-Location Candidate-Pruning Design)** within the RTDL codebase located at [rtdl_v0_4_release_prep_review](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review).

Goal4891 was initiated in response to the decisive findings of [goal4890_traversal_work_count_probe_result_2026-07-03.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4890_traversal_work_count_probe_result_2026-07-03.md), which confirmed a massive candidate segment-test explosion (up to **6,069.9x** on vertex PIP map0 in map1) in RTDL's public directed point-location/PIP primitives compared to the AuthorPatch reference implementation.

The proposed design targets this candidate explosion at the algorithm/traversal level rather than resorting to low-level hardware optimizations or RayJoin-specific shortcuts.

### Final Verdict Summary
We approve the design direction for Goal4891 with the verdict **`approve_with_amendments`**. The implementation proof is authorized to proceed once the specific amendments detailed in Section 5 are incorporated.

---

## 2. Review of Design Routes

The design file [goal4891_generic_directed_point_location_pruning_design_2026-07-03.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4891_generic_directed_point_location_pruning_design_2026-07-03.md) outlines three routes:

*   **Route A (Generic Candidate-Range Tightening):** Focuses on BVH spatial partitioning / grouping structure.
    *   *Evaluation:* While mathematically clean, it carries a high risk of failing to bridge the performance gap if the bottleneck stems from shader-level candidate processing rather than group hierarchy overlap.
*   **Route B (Generic In-Traversal Pruning Predicate):** Discards candidate segments within the intersection/traversal shader before executing full geometric segment tests.
    *   *Evaluation:* **Recommended.** This directly targets the measured work-count inflation (the segment-loop iterations) at the leaf shader level. It is localized, maintains a generic contract, and does not require complex compiler modifications.
*   **Route C (Data-Flow Pushdown):** Exposes a declarative compilation and optimization layer.
    *   *Evaluation:* Over-engineered for a first proof. Treating this as a full compiler project would introduce excessive scope creep.

---

## 3. Responses to Key Review Questions

### 1. Does the design correctly respond to Goal4890's candidate-explosion evidence?
Yes. The design addresses the root cause of the performance bottleneck (work volume) by targeting the reduction of candidate segment-loop iterations inside [__intersection__rayjoin_cdb_point_location](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/native/optix/rtdl_optix_core.cpp#L1584-L1676) rather than pre-emptively micro-tuning execution speed.

### 2. Is Route B the right first proof?
Yes. Moving pruning predicates into the traversal loop represents the most direct, localized path to achieving a 10x-100x reduction in segment tests without changing the public API surface.

### 3. Are Route A/B/C distinctions clear enough to prevent scope creep?
Yes. The distinctions isolate compilation/data-flow features (Route C) and broad-phase construction overhauls (Route A) from traversal-level optimization (Route B), preventing unnecessary infrastructure tasks.

### 4. Are the 10x hard gate / 100x strong gate reasonable?
Yes. Because the measured inflation is 915x-6,069x, a 10x hard gate is a conservative minimum baseline to verify that the pruning mechanism is active and correct. The 100x strong gate is a realistic milestone before continuing deeper optimizations.

### 5. Does the design prevent RayJoin-specific shortcuts?
Yes. The design explicitly forbids introducing `rayjoin_overlay` specific symbols or hidden kernels. The locator contract remains generic directed point-location, and it requires validation on a second non-RayJoin synthetic workload.

### 6. Is "no raw public callback API" the right boundary?
Yes. Exposing OptiX any-hit or closest-hit shaders directly to users would break encapsulation, create security risks, and leak internal GPU architecture details, compromising the RTDL API.

### 7. Are verification gates sufficient?
Yes. Requiring byte-equality on the Australia representative workload, passing synthetic correctness tests, and enforcing the absence of RayJoin-specific API symbols are robust controls.

---

## 4. Reiteration of Non-Authorization Boundary

The approval of this design **does not authorize** the following:
*   Any public performance claims or release documentation modifications.
*   RayJoin-specific shortcuts or hidden bypasses in public wrappers.
*   Raw OptiX callback APIs exposed to Python.
*   Prepared-session / row-buffer / Numba API modifications (which remain deferred).
*   Low-level native micro-tuning (register allocation, instruction selection) before the algorithmic candidate count is reduced.

---

## 5. Required Amendments Before Implementation

To ensure that the implementation proof remains correct, generic, and strictly scoped, the following amendments must be applied:

### Amendment 1: Define the Non-RayJoin Synthetic Workload
The validation suite must include a synthetic directed point-location test consisting of complex, non-grid-aligned planar-map topologies (e.g., a randomized Delaunay triangulation or concentric nested ring shapes). This ensures that the traversal-level pruning logic remains robust and correct under arbitrary geometric layouts.

### Amendment 2: Document Simulation-of-Simplicity (SoS) Correctness
The pruning predicate must not alter the exact Simulation-of-Simplicity (SoS) tie-breaking behavior for vertical rays. The implementation team must document how the pruning rules maintain exact logical equivalence to the unpruned code (e.g., in [vertical_ray_segment_t](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/native/optix/rtdl_optix_core.cpp#L1471-L1505)), ensuring bit-for-bit output match.

### Amendment 3: Code Surface Constraints
To prevent scope creep, the code changes for the first proof must be strictly limited to:
*   [rtdl_optix_core.cpp](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/native/optix/rtdl_optix_core.cpp) (primarily the intersection shaders and geometric helper methods).
*   [rtdl_optix_workloads.cpp](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/native/optix/rtdl_optix_workloads.cpp) (wiring counters and setting up launch parameters).
No modifications to python-level data structures or compiler representations in `src/rtdsl` are allowed.

### Amendment 4: Freeze Work-Count Instrumentation Interfaces
The work counters introduced in the temporary Goal4890 probe must be formally integrated into the internal/diagnostic outputs of the locator objects. This ensures that work counts (candidate loops and queries) can be monitored directly in diagnostic runs without adding custom public-facing API clutter.

---

## 6. Implementation Failure Labels

The implementation proof will terminate with one of the following labels:
*   `candidate_pruning_proof_passed_continue_engine_work`
*   `candidate_pruning_correct_but_not_enough_reassess_route_a_or_c`
*   `candidate_pruning_breaks_correctness_stop`
*   `candidate_pruning_is_rayjoin_specific_reject`
*   `measurement_not_reproducible_redo_goal4890`
