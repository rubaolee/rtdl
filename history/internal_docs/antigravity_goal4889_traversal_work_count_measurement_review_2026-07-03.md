# RTDL Goal4889 Traversal Work-Count Measurement Gate Review

**Date:** 2026-07-03
**Reviewer:** Antigravity AI
**Verdict:** `approve_goal4889_close_with_instrumentation_required_authorize_goal4890_probe`

---

## 1. Executive Summary

This review evaluates the deliverables of **Goal4889 (Traversal Work-Count Measurement Gate)** in the RTDL worktree (`C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review`).

The primary objective of Goal4889 was to obtain or derive traversal work counts (candidate/test denominators) to determine whether the performance gap between RTDL and AuthorPatch on the Australia representative Section 5.7 dataset is caused by **candidate/test count inflation** or **per-test native kernel path inefficiency**.

### Verdict and Recommendation
* **Verdict:** Approved with the verdict label `approve_goal4889_close_with_instrumentation_required_authorize_goal4890_probe`.
* **Key Findings:**
  1. Goal4889 successfully adhered to its measurement-only scope boundary. No product source files (`src/`) or test suites (`tests/`) were modified during the goal's duration.
  2. Launch and query counts match exactly between RTDL and AuthorPatch, eliminating the possibility of a simple ray-launch mismatch.
  3. The critical candidate/test work-count denominators are missing from current timing systems. In RTDL, LSI reports zero candidate events because the row-producing workload API disables instrumentation (`record_group_candidate_events=false`), and PIP lacks iteration counters altogether. AuthorPatch logs do not record actual intersection tests.
  4. Authorizing a temporary, measurement-only instrumented build (**Goal4890 Probe**) is necessary and sufficient to gather these numbers before any compiler, fusion, or native kernel optimization begins.
* **Non-Authorization:** Consistent with the project guidelines, this review does **not** authorize prepared sessions, row-buffer ABI, Numba partner API implementation, native kernel tuning, callback APIs, RayJoin-specific shortcuts, or public performance claims.

---

## 2. Critical Claim Verification

### Claim 1: Goal4889 stayed measurement-only and did not modify the engine code
* **Status:** **Verified (True)**.
* **Evidence:** A recursive check of the modification timestamps of all files under `src/` and `tests/` shows that **no product files or tests were modified on or after July 3, 2026**. All source modifications in the repository are from July 2, 2026 or earlier (corresponding to previous iterations of development). Only files starting with `goal4889_*` under `history/internal_docs/` were created/modified on July 3, 2026.
* **Conclusion:** The goal stayed strictly measurement-only and did not violate the engine code boundary.

### Claim 2: Query/launch counts match exactly across RTDL and AuthorPatch
* **Status:** **Verified (True)**.
* **Evidence:** Review of RTDL summary (`goal4886_pod_numba_au_skip_v2_summary.json`), RTDL LSI probe (`goal4889_lsi_probe_summary_2026-07-03.json`), and AuthorPatch CUDA logs (`goal4886_authorofficial_wall_attempt_freshser_cwd_invalid_summary.json`) confirms matching launch counts:
  * **LSI Queries / Launch size:** Both launch exactly **14,430,155** query segments (from Map0).
  * **Vertex PIP Map0 Queries / Launch size:** Both launch exactly **14,788,065** query points.
  * **Vertex PIP Map1 Queries / Launch size:** Both launch exactly **992,505** query points.
  * **Midpoint PIP Map0 Queries / Launch size:** Both launch exactly **1,707** query points.
  * **Midpoint PIP Map1 Queries / Launch size:** Both launch exactly **2,752** query points.
  * **LSI Output Row Count:** Both produce exactly **13,452** intersection rows.
* **Conclusion:** The launch inputs are identical. The performance gap is not caused by RTDL launching more rays or processing different query coordinates.

### Claim 3: Candidate/test denominators are truly missing
* **Status:** **Verified (True)**.
* **Evidence:**
  * **RTDL LSI:** Native timing returns `raw_candidate_count: 0`. Code inspection of `src/native/optix/rtdl_optix_workloads.cpp` (lines 7749 and 8418) reveals that both calls to `count_segment_pair_intersection_grouped_range_direct_is_exact_one_pass_optix` pass `record_group_candidate_events = false`. Thus, candidate reporting is hardcoded off in the row-producing workloads, making the zero value an instrumentation artifact rather than a true count.
  * **RTDL PIP:** In `src/native/optix/rtdl_optix_core.cpp`, `__intersection__rayjoin_cdb_point_location` executes a segment loop:
    ```cpp
    for (unsigned int segment_index = range.begin; segment_index < range.end; ++segment_index) { ... }
    ```
    This loop is the central execution bottleneck of PIP, but no counter accumulates or reports the total iteration count (`range.end - range.begin`) back to the Python caller.
  * **AuthorPatch:** The execution logs report input dimensions (AABB counts, map shapes, launch dimensions) and phase timings but omit candidate/test totals entirely.
* **Conclusion:** The decisive work counts (how many segments are actually tested per query) are currently unmeasured on both sides.

### Claim 4: The proposed Goal4890 temporary instrumentation counters are sufficient
* **Status:** **Verified (True)**.
* **Reasoning:** To diagnose the performance discrepancy without making premature modifications, we must isolate the count of candidate tests from the time taken per test.
  * **RTDL LSI:** Setting `record_group_candidate_events = true` is trivial, safe, and utilizes existing library paths to get the group-candidate event count.
  * **RTDL PIP:** Adding a simple atomic counter for segment-loop iterations (`range.end - range.begin`) inside `__intersection__rayjoin_cdb_point_location` will measure PIP candidates.
  * **AuthorPatch LSI & PIP:** Counting candidate/intersection tests inside the respective CUDA shaders allows direct parity check.

  These four counters will immediately isolate whether the bottleneck is candidate explosion (pointing toward BVH/fusion issues) or execution latency per test (pointing toward native kernel compile/optimization issues).
* **Conclusion:** The proposed instrumentation plan is correct, minimal, and sufficient.

---

## 3. Scope Boundaries & Non-Authorizations

To maintain the architectural integrity of the upcoming release, the following work is **explicitly unauthorized** under this gate:
* **No prepared sessions** or lifecycle API modifications.
* **No row-buffer ABI** or custom host-materialization layouts.
* **No Numba partner API implementation** or application-layer compiler integration.
* **No native kernel tuning** or custom thread-block scheduling optimizations.
* **No callbacks** or runtime hook configurations.
* **No RayJoin-specific engine shortcuts** (e.g., custom fast-paths bypassing the general planar map interface).
* **No public performance claims** or external benchmarking comparisons.

All activities must remain confined to a **temporary, measurement-only instrumented build** using the exact same Australia dataset.

---

## 4. Next Steps: Goal4890 Probe Authorization

The verdict authorizes the creation of **Goal4890: Traversal Work-Count Temporary Probe**.

The scope of Goal4890 is strictly limited to:
1. Creating a temporary, non-production build to record the proposed counters.
2. Generating a comparison ledger of candidates tested.
3. Deciding the engineering path on the basis of candidate count parity:
   * **If RTDL Candidate Count >> AuthorPatch:** Proceed to data-flow fusion / in-traversal pruning research.
   * **If RTDL Candidate Count == AuthorPatch:** Proceed to native kernel path tuning.
