# Critical Review: Goal 4806 V4 + Numba RayJoin Section 5.7 Auto-Primitive Planner

This document provides the external critical review for the RTDL V4 execution proposal:
[goal4806_v4_numba_rayjoin_section57_auto_primitive_planner_2026-06-28.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tools/_archive/future/v4/goals/goal4806_v4_numba_rayjoin_section57_auto_primitive_planner_2026-06-28.md), in response to [call_for_review_goal4806_v4_numba_rayjoin_auto_primitive_planner_2026-06-28.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tools/_archive/future/v4/reviews/call_for_review_goal4806_v4_numba_rayjoin_auto_primitive_planner_2026-06-28.md).

---

## 1. Verdict Label

`approve_with_required_amendments`

---

## 2. Short Rationale

The proposed goal establishes a sound plan to automate primitive selection for Section 5.7 Polygon Overlay using a V4 automatic primitive planner. It successfully eliminates primitive-name theater from the user interface. However, to guarantee that the Numba partner integration remains a meaningful compiler-backed stage (rather than wrapper theater), to prevent correctness verification gaps in polygon reconstruction, and to explicitly block V4.1 arbitrary ray-tracing callback creep, implementation must proceed only after incorporating the required amendments specified below.

---

## 3. Answers to Required Review Questions

### 1. Is the goal clear and executable?
Yes. The goal is conceptually clear and divides the implementation tasks logically. To be fully executable, the search space of candidate plans and the specific verification API contracts must be explicitly mapped in the planner logic.

### 2. Does it correctly require user-level semantics instead of primitive-name hand selection?
Yes. The proposal correctly mandates that the user-level API exposes only high-level parameters (`select="fastest_valid"` and `partner="numba"`) while automatically enumerating and evaluating primitives internally.

### 3. Is the automatic primitive-plan selection requirement strong enough?
Yes, but with reservations. The selection must not degrade into a static lookup heuristic. The runtime must dynamically evaluate candidates on the target GPU and make selection decisions based on measured timing statistics.

### 4. Is Numba partner work defined in a way that is meaningful and not just wrapper theater?
Mostly, but it needs to be made stricter. To ensure it is not wrapper theater, Numba must compile Python user-defined logic (like predicates and aggregations) down to custom GPU kernels via `numba.cuda.jit` and execute zero-copy on device arrays, rather than calling pre-compiled backend routines.

### 5. Are the correctness and performance bars fair and not toy-level?
Yes. Gating the performance bar on the full Section 5.7 real inputs and requiring a geomean improvement of `1.20x` over the V2.14 baseline ensures a rigorous test. However, correctness checks must validate the structural geometry coordinates and topologies of output chains, not just match row counts.

### 6. Are the no-go and bounded-claim outcomes explicit enough?
Yes. The proposal clearly defines outcomes for timing regressions, correctness failures (`no_go_correctness_failed`), and missing datasets (`blocked_missing_inputs`).

### 7. Does anything in this plan accidentally pull V4.1 arbitrary callback work into V4.0?
There is a potential risk if Numba is called from within the OptiX ray-intersection loop. This must be strictly prohibited by enforcing a post-traversal execution boundary for Numba kernels.

### 8. What amendments are required before implementation?
The plan requires four specific amendments, detailed in the section below.

---

## 4. Required Amendments

To address potential gaps, the following amendments are required:

1. **Numba JIT Compilation & Zero-Copy Execution**:
   - The Numba partner stage must use `numba.cuda.jit` to compile Python code representing workload-specific logic (e.g., predicates, filters, or aggregators) directly into GPU kernels.
   - It must execute directly on GPU device-resident arrays (e.g., PyTorch/CuPy device pointers) produced by RTDL's ray-tracing stages. Wrapping pre-compiled C++/CUDA libraries is prohibited.

2. **Strict Post-Traversal Execution Boundary**:
   - All Numba-compiled kernels must execute strictly outside of the native OptiX ray traversal execution loop (i.e., only as pre-traversal or post-traversal/refinement stages).
   - Dynamic user callback code injection into OptiX shader execution is strictly out of scope for V4.0 and reserved for V4.1.

3. **Topology-Aware Correctness Verification**:
   - Correctness checks against the V2.14 exact-suite baseline must validate output chain geometries (e.g., matching coordinates or structural hashes) to verify polygon reconstruction correctness, rather than relying solely on row count comparisons.

4. **Planner Scoreboard Logging**:
   - The final evidence packet must log a complete candidate-plan scoreboard displaying all considered, evaluated, or skipped plans (with detailed skip reasons), alongside their compile/jit overheads and execution times.

---

## 5. Explicit Non-Authorization

This review is limited to checking the validity of the goal for execution. It **does NOT authorize** a public high-performance claim, a new public release tag, or a full Section 5.7 paper-reproduction claim based on this plan alone.
