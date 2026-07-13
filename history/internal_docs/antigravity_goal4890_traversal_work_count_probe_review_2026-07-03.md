# RTDL Goal4890 Traversal Work-Count Probe Review

**Date:** 2026-07-03
**Reviewer:** Antigravity AI
**Verdict:** `approve_goal4890_candidate_explosion_result_authorize_generic_pruning_design_goal`

---

## 1. Executive Summary

This review evaluates the deliverables and findings of **Goal4890 (Temporary Traversal Work Instrumentation Probe)** in the RTDL worktree ([rtdl_v0_4_release_prep_review](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review)).

The primary objective of Goal4890 was to implement temporary, non-production counters in both RTDL and the AuthorPatch reference code to measure the number of candidate segment/intersection tests (the traversal work-count denominator). These metrics are critical to diagnosing the massive performance gap on the Australia representative Section 5.7 workload.

### Key Findings
1. **Goal4890 remained strictly measurement-only.** The main product code remains clean of temporary instrumentation. Counters were only applied inside temporary POD scratch directories (`/workspace/goal4890_rtdl_instr` and `/workspace/goal4890_author_instr`).
2. **RTDL byte-equality is preserved.** The RTDL run output remains bit-for-bit identical to the AuthorPatch reference output (`byte_equal_to_author: true`).
3. **Severe Candidate Explosion in PIP is confirmed.** RTDL executes **915x to 6,069x** more segment tests than AuthorPatch for directed point-location/PIP. This proves that the performance bottleneck is a work-inflation issue rather than execution speed per test, justifying prioritizing work-reduction over kernel micro-tuning.
4. **The LSI caveat is correct.** LSI counters measure grouped-range candidate events in RTDL vs. individual segment tests in AuthorPatch, meaning they are not apples-to-apples units.
5. **No forbidden features were authorized or implemented.** There is no trace of RayJoin-specific shortcuts, raw callback APIs, prepared sessions, row-buffer ABIs, or Numba integration in the main line.

Based on these findings, we authorize transition to the next design goal: generic in-traversal pruning and data-flow pushdown for directed point-location.

---

## 2. Detailed Verification

### 2.1 Measurement-Only Constraint & Patch Scoping
* **Verdict:** **Verified (Pass)**
* **Analysis:** Git status and diffs confirm that the main product repository at [rtdl_v0_4_release_prep_review](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review) contains no instrumentation changes in `src/native/optix/rtdl_optix_core.cpp` or `src/native/optix/rtdl_optix_workloads.cpp`. The code changes were successfully restricted to scratch copies (`/workspace/goal4890_rtdl_instr` and `/workspace/goal4890_author_instr`) and are preserved in local patches:
  * [goal4890_rtdl_measurement_instrumentation.patch](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4890_rtdl_measurement_instrumentation.patch)
  * [goal4890_authorpatch_measurement_instrumentation.patch](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4890_authorpatch_measurement_instrumentation.patch)

### 2.2 Correctness & Byte-Equality
* **Verdict:** **Verified (Pass)**
* **Analysis:** The output comparison log [goal4890_rtdl_work_count_summary_2026-07-03.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4890_rtdl_work_count_summary_2026-07-03.json) confirms:
  ```json
  "byte_equal_to_author": true
  ```
  The generated output [rtdl_goal4890_output.txt](file:///workspace/goal4890_rtdl_instr/rtdl_goal4890_output.txt) matched the SHA-256 hash of the reference `author_contract_au_overlay.txt` (`a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e`).

### 2.3 PIP Counter Parity & Candidate Explosion
* **Verdict:** **Verified (Pass)**
* **Analysis:** The counters implemented on both sides measure the identical logical operation (the number of segment-loop iterations executed in leaf intersection shaders):
  * **RTDL:** `atomicAdd` inside `__intersection__rayjoin_cdb_point_location` counting `range.end - range.begin`.
  * **AuthorPatch:** `atomicAdd` inside custom intersection shaders counting `end_eid - begin_eid`.

  The measured work counts reveal extreme traversal work discrepancy:

  | Stage | RTDL segment-loop iterations | AuthorPatch segment tests | RTDL / AuthorPatch Ratio |
  | --- | ---: | ---: | ---: |
  | Vertex PIP map0 in map1 | 511,943,147,571 | 84,341,083 | **6,069.9x** |
  | Vertex PIP map1 in map0 | 36,359,368,176 | 18,561,490 | **1,958.9x** |
  | Midpoint PIP map0 | 68,493,462 | 74,815 | **915.5x** |
  | Midpoint PIP map1 | 105,145,275 | 108,540 | **968.7x** |

  This enormous discrepancy indicates that RTDL's public point-location primitive is traversing massive candidate segment ranges per query ray compared to the reference implementation. The performance gap is fundamentally a work-volume issue.

### 2.4 LSI Caveat Verification
* **Verdict:** **Verified (Pass)**
* **Analysis:** The LSI caveat is correct.
  * RTDL LSI measures **grouped-range candidate events** (returned by `PreparedOptixPlanarMapLsi2D.run_raw` via the timing library).
  * AuthorPatch LSI measures **individual segment tests** (`end_eid - begin_eid` in `rt_lsi_custom.cu`).
  * Because these represent candidate work at different hierarchies, they are not direct apples-to-apples semantic units and must not be used as a simple candidate ratio.

### 2.5 Next Architectural Branch Selection
* **Verdict:** **Verified (Pass)**
* **Analysis:** The evidence heavily supports prioritizing work reduction over micro-optimization.
  * Micro-tuning of the GPU kernels cannot bridge a 1,000x-6,000x execution work gap.
  * First-order priority must be reducing the volume of segment tests.
  * Therefore, authorizing a design goal for **generic in-traversal pruning and data-flow pushdown** for directed point-location is correct. Micro-tuning of kernels should be postponed until work counts are comparable.

### 2.6 Boundary Audit (Non-Authorization)
* **Verdict:** **Verified (Pass)**
* **Analysis:** No forbidden elements were introduced to the codebase:
  * No RayJoin-specific shortcuts or hidden bypasses.
  * No prepared-session modifications.
  * No row-buffer ABI changes.
  * No Numba-partner API integrations or continuation modifications.
  * No raw OptiX callback APIs exposed to the public surface.

---

## 3. Review Verdict & Recommendations

### Final Verdict Label
`approve_goal4890_candidate_explosion_result_authorize_generic_pruning_design_goal`

### Next Steps & Amendments
1. **Authorize Next Design Goal:** The team is authorized to initiate `candidate_explosion__dataflow_pushdown_or_in_traversal_pruning_next`.
2. **Generic Core Pruning:** The design must address the candidate explosion in a *generic* way in the public RTDL directed point-location primitive rather than through RayJoin-specific code paths.
3. **No Public Claims:** No public performance claims or benchmarks may be published until a clean, pruning-enabled product version is built and verified.
