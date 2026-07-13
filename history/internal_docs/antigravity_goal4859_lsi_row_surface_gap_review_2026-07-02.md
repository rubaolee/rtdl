# Antigravity Review Verdict: Goal4859 LSI Row-Surface Gap and Goal4860 Plan

**Date:** 2026-07-02
**Verdict Label:** `approve_goal4859_pause_section57_and_authorize_goal4860_lsi_row_repair`

---

## 1. Review Questions and Answers

### Question 1: Does the evidence justify classifying the current blocker as an LSI row-surface contract gap rather than a PIP/Section 5.3 bug?
**Answer:** Yes. The evidence clearly demonstrates that the discrepancy lies strictly between the LSI scalar counts and the LSI row materialization. As summarized in [goal4859_minimal_real_witness_probe_summary.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4859_minimal_real_witness_probe_summary.json), a three-segment synthetic case yields a public count of `2` but a hidden-predicate row count of `0`. This mismatch occurs prior to and completely independent of point-in-polygon (PIP) or point-location stages (Section 5.3). Because the counted intersections are not being generated in the row output, this is fundamentally an LSI row-surface contract gap under Section 5.2.

### Question 2: Is it correct that Section 5.2 count-only reproduction remains valid, but Section 5.2 now needs an additional row-materialization gate for Section 5.7?
**Answer:** Yes. While Section 5.2 count-only validation successfully completed its reproduction criteria, Section 5.7 (County x Zipcode correctness-first overlay construction) requires actual intersection coordinate rows (left segment ID, right segment ID, and intersection points) to reconstruct the topological overlay. Since the count path and row materialization path currently disagree, Section 5.2 needs an additional row-contract gate:
```text
planar_map_lsi_count == planar_map_lsi_rows.length
```
Section 5.7 cannot proceed until this contract gate is consistently satisfied.

### Question 3: Does the minimal witness (`count=2`, `rows=0`) provide a sufficiently small, controlled regression case?
**Answer:** Yes. The minimal witness uses two base segments and one query segment extracted from the Australia Lakes x Parks representative case (see [goal4859_minimal_real_witness_probe_summary.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4859_minimal_real_witness_probe_summary.json)). It operates without any CDB file dependency, making it an excellent, lightweight regression test case that can be executed rapidly during debugging.

### Question 4: Is it correct to pause Section 5.7 full overlay and performance work until the LSI row path matches the scalar count path?
**Answer:** Yes. Attempting to build or optimize the point-location (Section 5.3) or overlay (Section 5.7) logic while the input intersection coordinates are missing or incorrect is futile. Core correctness must be established bottom-up. Correcting the row-materialization path first ensures a solid mathematical foundation for subsequent stages.

### Question 5: Is Goal4860 scoped correctly as a generic planar-map LSI row repair rather than a RayJoin-specific application patch?
**Answer:** Yes. The scope must remain strictly generic to preserve RTDL's architectural separation. The bug originates in the interaction between the native LSI scaling predicates and the host-side row refinement routines (such as [finalize_segment_pair_intersection_rows](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/native/optix/rtdl_optix_workloads.cpp#L6113-L6213) and [rayjoin_lsi_intersection_host](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/native/optix/rtdl_optix_workloads.cpp#L5842-L5886)). Fixing this at a generic library level prevents polluting the RTDL runtime with application-specific hacks (e.g. RayJoin-specific kernels) and ensures the repaired contract remains valid for any planar map application.

### Question 6: Are the Goal4860 exit gates sufficient?
**Answer:** Yes, the proposed gates are highly rigorous:
- **Minimal witness:** `count == rows == 2`
- **Australia representative pair:** `count == rows == 13622` (verifying medium-scale behavior, see [goal4859_au_chunk_mismatch_locator_summary.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4859_au_chunk_mismatch_locator_summary.json))
- **Correct County x Zipcode input:** `count == rows == 961165` (verifying large-scale production behavior, see [goal4859_county_zipcode_correct_input_hidden_predicate_lsi_rows_summary.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4859_county_zipcode_correct_input_hidden_predicate_lsi_rows_summary.json))
These gates ensure that both synthetic and real-world datasets align across all scale thresholds.

### Question 7: Should PIP/Section 5.3 remain out of scope until LSI rows are correct?
**Answer:** Yes. Since point-location and PIP classifications depend on the output coordinates and topological faces generated during LSI, debugging PIP while LSI rows are broken would result in chasing false positives. Section 5.3 must remain out of scope until LSI rows are verified correct.

### Question 8: Do you authorize Goal4860 to start, with the understanding that any runtime/native repair must be generic and externally reviewed before closure?
**Answer:** Yes. Starting Goal4860 is fully authorized, subject to the condition that all native C++ or CUDA modifications are generic and undergo external code review before closure.

---

## 2. Reviewer Critical Evaluation

### The Core Architectural Dilemma: Section 5.2 vs PIP/Section 5.3
During the review, we evaluated whether this gap could be classified under PIP/Section 5.3. We confirm that classifying it under Section 5.2 is mathematically and architecturally correct. PIP operates on coordinates produced by LSI; if those coordinates are missing (returning `0` rows instead of `2`), the error lies in the LSI stage. Fixing this in Section 5.3 would require introducing complex coordinate-recovery workarounds, which violates the strict separation of concerns in the RTDL pipeline.

### Genericity: Planar-Map LSI Repair vs. RayJoin Patch
We emphasize that the repair for Goal4860 **must not** special-case RayJoin or rely on its application-layer structures.
- The mismatch happens because the GPU count path and CPU row-filtering path use different scaling / precision rules.
- The host-side refinement in [finalize_segment_pair_intersection_rows](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/native/optix/rtdl_optix_workloads.cpp#L6113-L6213) applies both the `rayjoin_lsi_intersection_host` predicate and the `exact_segment_intersection` check, which can disagree on endpoints or exact overlap cases under float/double conversions.
- The correction must be made generically within the native LSI implementation in [rtdl_optix_workloads.cpp](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/native/optix/rtdl_optix_workloads.cpp) to align the two evaluation paths under a unified planar-map LSI contract.

---

## 3. Non-Authorization Boundaries

This review does **NOT** authorize:
- Treating raw segment-pair rows as planar-map LSI rows.
- Application-layer patches or RayJoin-specific hidden kernel workarounds.
- Claims of Section 5.7 correctness or completion.
- Section 5.7 performance or speedup claims.
- Proceeding to PIP/Section 5.3 debugging before all Goal4860 exit gates are satisfied.
