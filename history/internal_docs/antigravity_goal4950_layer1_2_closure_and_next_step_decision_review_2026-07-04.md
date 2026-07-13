# Goal4950 Review: Layer 1/2 Closure And Next-Step Decision

**Review Date:** 2026-07-04
**Assigned Reviewer:** Antigravity
**Verdict:** `approve_goal4950_close_layer1_2_move_to_layer3`

---

## Executive Summary

We have conducted a strict review of the closure and next-step decision for Goal4950, supported by measurements from Goal4949 and Goal4924.

The report in [goal4950_layer1_2_closure_and_next_step_decision_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4950_layer1_2_closure_and_next_step_decision_2026-07-04.md) presents an honest, evidence-based assessment of the Layer 1/2 engineering path. It correctly distinguishes between the success of the generic interface capabilities (generic row-buffer and Numba continuation handoff) and the performance reality of the RayJoin application workload, where the current Numba-based helpers yield regressions.

Closing the current Layer 1/2 line as a **capability success but RayJoin performance no-go** is the correct, rigorous engineering decision. Repeating micro-optimization of Python/Numba on reprojection and sorting without a new algorithmic idea is a looks-busy trap. Moving to Layer 3 writer and output assembly is fully justified because serialization and structural formatting constitute the single largest remaining bottleneck (~2.1–2.6 seconds of a 6.3-second hot rerun).

We issue a verdict of **`approve_goal4950_close_layer1_2_move_to_layer3`** under a strict non-authorization mandate: **no app-specific RayJoin output formatting, code, or serialization logic may enter the RTDL core.**

---

## Detailed Answers to Review Questions

### 1. Does the report correctly distinguish Layer 1/2 capability success from RayJoin performance success?

**Yes.**
* **Capability Success:** The integration framework was successfully built and tested. Layer 1 (device-column row-buffer) handles generic device-resident columns without host-side row materialization. Layer 2 (Numba continuation handoff) successfully bridged those native columns to compiled code, passing a non-RayJoin genericity gate (a 3D ray/triangle hit-stream workload).
* **RayJoin Performance No-Go:** The report honestly states that this connector did not translate to RayJoin speedups. Timings show the current Numba overlay helper is slower than the baseline, meaning the framework is structurally proven but the specific RayJoin application helper is rejected for production.

### 2. Does Goal4949 justify rejecting the current Numba overlay helper as a performance path?

**Yes.**
As measured in [goal4949_rayjoin_hot_path_remeasure_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4949_rayjoin_hot_path_remeasure_2026-07-04.md), the Numba variant introduces a significant performance regression compared to the baseline:
* **Baseline Hot Rerun:** `6.305s` total elapsed (writer took `2.615s`).
* **Numba Variant Hot Rerun:** `8.034s` total elapsed (writer took `4.237s`).
The Numba writer is over 60% slower than the baseline writer due to Python-side materialization, formatting, and buffer overhead (e.g., `bulk_writelines_sec` took `4.163s`). The current Numba overlay helper must not be promoted.

### 3. Does Goal4924 justify not repeating another reprojection/sort micro-optimization goal without a new algorithmic idea?

**Yes.**
As detailed in [goal4924_columnar_reprojection_sort_probe_result_2026-07-03.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4924_columnar_reprojection_sort_probe_result_2026-07-03.md), the reprojection phase cannot be simplified into cheap numeric vector loops because exact coordinate match requires arbitrary-precision rational coordinates and `math.gcd` reductions.
* Numba cannot compile Python's arbitrary-precision integer semantics efficiently.
* While sorting was optimized, reprojection remained expensive (~0.43s), causing the overall hot-body run to miss its target performance bar (observed `3.79s` vs. target `<= 3.45s`).
* Thus, micro-optimizing the current code structure is mathematically bounded; further work requires a fundamentally new algorithmic design for coordinate calculation, not more Numba tuning.

### 4. Is the recommendation to move to Layer 3 writer/output assembly the correct next step?

**Yes.**
* With prepared-hot point-in-polygon (PIP) traversal consuming less than 0.33% of the execution time (`0.020s`), and reprojection/sort blocked by rational arithmetic constraints, the writer / output-chain serialization is the primary remaining bottleneck, consuming between 33% and 40% of the entire hot path (`2.1s - 2.6s` out of `6.3s`).
* Redesigning output assembly to move structural grouping and index manipulation to generic compiled infrastructure is the only viable path to achieve major performance improvements.

### 5. Does the report preserve the genericity boundary: compiled generic output assembly may be RTDL infrastructure, but RayJoin text output format must remain app-owned?

**Yes.**
The report preserves this boundary under the instructions for Goal4951:
* The expensive structural part (grouping, indexing, and output-chain assembly) can become generic compiled infrastructure inside RTDL.
* The final point formatting, line/string construction, and application-specific text output formatting must remain in the application layer (RayJoin).
* The RTDL core must not know about RayJoin's text schema or custom output formats.

### 6. Does the report avoid broad RTDL / RayJoin speedup claims?

**Yes.**
Under **"Authorized Claim"** and **"Not authorized"**, the report explicitly forbids any claims that:
* Layer 1/2 has materially moved RayJoin whole-app performance.
* Numba closes the RayJoin performance gap.
* RTDL itself has achieved a broad speedup.

### 7. Should Goal4950 close with label `completed_layer1_2_capability_success__rayjoin_perf_no_go__move_to_layer3_writer_design`?

**Yes.**
This label is completely accurate and reflects the dual outcome: the row-buffer and Numba continuity interface work generically as a capability (success), but they did not resolve RayJoin's performance constraints (no-go), leading to the redirection of optimization efforts to the Layer 3 writer design.

---

## Strict Non-Authorization & Enforcement Mandate

We explicitly enforce the following restrictions:
1. **No App-Specific Code in RTDL Core:** Under no circumstances shall RayJoin-specific text output formatting, coordinate representation, or schema parsing be written into the `src/rtdsl` or `src/native` folders. RTDL core must remain entirely agnostic of RayJoin's specific file schemas.
2. **Reject Current Numba Helpers:** The current Numba writer wrapper is confirmed to be a performance regression and is rejected from promotion.
3. **No Broad Speedup Claims:** The RTDL project must not publish or claim any general RayJoin or whole-app speedup from the Layer 1/2 connector.

---

## Reviewed Files Reference List

* [call_for_review_goal4950_layer1_2_closure_and_next_step_decision_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/call_for_review_goal4950_layer1_2_closure_and_next_step_decision_2026-07-04.md)
* [goal4950_layer1_2_closure_and_next_step_decision_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4950_layer1_2_closure_and_next_step_decision_2026-07-04.md)
* [goal4949_rayjoin_hot_path_remeasure_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4949_rayjoin_hot_path_remeasure_2026-07-04.md)
* [goal4924_columnar_reprojection_sort_probe_result_2026-07-03.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4924_columnar_reprojection_sort_probe_result_2026-07-03.md)
