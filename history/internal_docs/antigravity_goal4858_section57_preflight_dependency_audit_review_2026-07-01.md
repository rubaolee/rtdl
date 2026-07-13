# Antigravity Goal4858 RayJoin Section 5.7 Preflight Dependency Audit Review

**Date:** 2026-07-01
**Verdict:** `approve_goal4858_go_directly_to_section57`

---

## Executive Summary

As an external reviewer, I have inspected the preflight dependency audit in [goal4858_rayjoin_section57_preflight_dependency_audit_2026-07-01.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4858_rayjoin_section57_preflight_dependency_audit_2026-07-01.md) and the proposed correctness execution plan in [goal4859_rayjoin_section57_overlay_correctness_execution_plan_2026-07-01.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4859_rayjoin_section57_overlay_correctness_execution_plan_2026-07-01.md).

This audit is verified against:
- [goal4816_A_rayjoin_section57_paper_source_contract_extraction_2026-06-30.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4816_A_rayjoin_section57_paper_source_contract_extraction_2026-06-30.md)
- [goal4853_section52_lsi_final_reproduction_closure_2026-07-01.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4853_section52_lsi_final_reproduction_closure_2026-07-01.md)
- [goal4856_section53_pip_result_consistency_2026-07-01.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4856_section53_pip_result_consistency_2026-07-01.md)
- [goal4857_planar_map_point_location_public_front_door_cleanup_2026-07-01.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4857_planar_map_point_location_public_front_door_cleanup_2026-07-01.md)
- Product source files: [optix_runtime.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/optix_runtime.py), [datasets.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/datasets.py), [rayjoin_overlay.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/rayjoin_overlay.py), and [rayjoin_paper_suite.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/rayjoin_paper_suite.py).
- Script suites: [rayjoin_section57_overlay_matrix.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/scripts/rayjoin_section57_overlay_matrix.py) and [rayjoin_paper_reproduction_suite.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/scripts/rayjoin_paper_reproduction_suite.py).

The audit is exceptionally thorough, technically precise, and maps existing RTDL primitives directly to Section 5.7's logic. It correctly avoids runtime/native edits, prevents premature performance claims, and establishes clear correctness boundaries.

---

## Detailed Review Answers

Below are the detailed answers to the 10 review questions outlined in [call_for_review_goal4858_section57_preflight_dependency_audit_2026-07-01.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/call_for_review_goal4858_section57_preflight_dependency_audit_2026-07-01.md):

### 1. Does Goal4858 correctly identify Sections 5.4 and 5.5 as dependencies for Section 5.7, not full prerequisite reproduction projects?
**Yes.**
- **Section 5.4 (Precision Evaluation):** This section validates the correctness necessity of conservative AABBs and rational representations under FP32 RT cores. Rather than being a standalone benchmark workload, it constitutes a correctness gate for Section 5.7 polygon overlay. Verifying it as a dependency-only contract (rather than a full standalone reproduction project) is correct because if Section 5.7 does not preserve this precision contract, the overlay will fail.
- **Section 5.5 (Parameter Tuning):** This section maps adaptive grouping thresholds and optimal paper parameters (e.g. `s=3.5` / `enlarge=3.5`, `grid_size=15000`). This is a static parameter selection dependency, not an independent workload. Deferring a full parameter sweep and instead locking the paper parameters into the Section 5.7 runner is appropriate.

### 2. Does Goal4858 correctly defer Section 5.6 scalability until after Section 5.7 correctness?
**Yes.**
Section 5.6 focuses on primitive LSI/PIP query scalability under massive synthetic uniform and Gaussian datasets (up to 5M polygons) with adaptive grouping disabled. This is a performance/scalability study of primitive algorithms, not a correctness integration test for the full polygon overlay. Deferring this performance evaluation until after Section 5.7 correctness is byte-equal or topology-diagnosed is the correct engineering sequence.

### 3. Does the report carry forward the Section 3.2 / 5.4 conservative representation, precision, and SoS requirements into 5.7?
**Yes.**
The audit carries forward these requirements in the "Locked Section 5.7 Parameters And Contracts" section of [goal4858_rayjoin_section57_preflight_dependency_audit_2026-07-01.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4858_rayjoin_section57_preflight_dependency_audit_2026-07-01.md). Specifically, it preserves:
- Conservative AABBs for FP32 RT traversal.
- Exact LSI predicates after RT candidate generation.
- Integer-scaled coordinates and rational intersection/midpoint handling in the overlay chain.
- The Simulation of Simplicity (SoS) tie-breaker rule for equal-height vertical ray boundary crossings using the perturbed `t_reported` distance contract detailed in [rayjoin_pip_determinism_summary.md](file:///C:/Users/Lestat/Downloads/rayjoin_pip_determinism_summary.md).

### 4. Does it lock the author Section 5.7 parameters (`grid_size=15000`, `-fau`, `xsect_factor=0.1`, `enlarge=3.5`, `mode=rt`) sufficiently for the next run?
**Yes.**
These parameters are explicitly locked in both [goal4858_rayjoin_section57_preflight_dependency_audit_2026-07-01.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4858_rayjoin_section57_preflight_dependency_audit_2026-07-01.md) and the executable template inside [goal4859_rayjoin_section57_overlay_correctness_execution_plan_2026-07-01.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4859_rayjoin_section57_overlay_correctness_execution_plan_2026-07-01.md).

### 5. Does the author-source dependency map name the correct source areas for LSI, PIP, midpoint classification, and output-chain construction?
**Yes.**
The "Author-Source Dependency Map" section matches the code boundaries extracted during [goal4816_A_rayjoin_section57_paper_source_contract_extraction_2026-06-30.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4816_A_rayjoin_section57_paper_source_contract_extraction_2026-06-30.md):
- **Top-level driver:** `src/run_overlay.cu` and `expr/run_overlay.sh`.
- **LSI:** `src/algo/rt_lsi_custom.cu` (casts query segment rays with range `[0,1]`).
- **Vertex PIP / point-location:** `src/algo/rt_pip_custom.cu` and `src/app/map_overlay_rt.h` (casts vertical rays, resolves face ids).
- **Midpoint point-location:** `src/app/map_overlay_rt.h` (projects midpoints between adjacent intersections).
- **Output-chain construction:** `src/app/output_chain.h` and `src/app/map_overlay_rt.h` (groups intersections, splits chains, deduplicates points, writes format).
- **Precision/SoS:** `src/config.h` (coordinate types), `src/rt/primitive.h` (expanded AABBs), and `src/algo/rt_pip_custom.cu`.

### 6. Does the RTDL capability map correctly update older Goal4816 conclusions with the later public front doors from Goal4851 and Goal4857?
**Yes.**
The capability map is fully updated to reflect the public, application-neutral interface surface:
- **CDB Loading:** Migrated to [chains_to_planar_map_segments](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/datasets.py#L817-L831) and [chains_to_planar_map_points](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/datasets.py#L944-L950) from Goal4857.
- **LSI Count:** Mapped to the public primitive [prepare_planar_map_lsi_2d_optix](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/optix_runtime.py#L3966) from Goal4851.
- **Vertex PIP / point-location:** Mapped to the public primitive [prepare_planar_map_point_location_2d_optix](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/optix_runtime.py#L4140-L4161) from Goal4857.

### 7. Does the Goal4859 plan correctly distinguish the generic-public route from the bounded bundled-helper route?
**Yes.**
[goal4859_rayjoin_section57_overlay_correctness_execution_plan_2026-07-01.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4859_rayjoin_section57_overlay_correctness_execution_plan_2026-07-01.md) enforces a strict boundary:
- **Preferred route (`generic_public_primitives_plus_app_layer`):** Allowed to call public APIs such as [load_cdb](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/datasets.py#L350), [chains_to_planar_map_segments](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/datasets.py#L817-L831), [chains_to_planar_map_points](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/datasets.py#L944-L950), [prepare_planar_map_lsi_2d_optix](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/optix_runtime.py#L3966), and [prepare_planar_map_point_location_2d_optix](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/optix_runtime.py#L4140-L4161). It explicitly forbids importing or calling private helpers in [rayjoin_overlay.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/rayjoin_overlay.py):
  - [_run_lsi_rows](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/rayjoin_overlay.py#L1097-L1106)
  - [_run_point_location_faces](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/rayjoin_overlay.py#L1191)
  - [_assemble_output_chains](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/rayjoin_overlay.py#L1555)
  - [run_rayjoin_overlay_rtdl_from_cdb_paths](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/rayjoin_overlay.py#L1930) (unless fallback route is used)
  If this route is blocked by surface gaps (like retrieving LSI row intersection IDs and coordinates via public API), it must close with `blocked_by_public_lsi_row_coordinate_surface_gap` and must not silently switch routes.
- **Fallback route (`bounded_bundled_helper_reproduction`):** Allowed only under an explicit label using [run_rayjoin_overlay_rtdl_from_cdb_paths](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/rayjoin_overlay.py#L1930), representing a packaged application helper rather than a user constructing the workflow from scratch.

### 8. Does it correctly block performance timing until output correctness is byte-equal or explicitly diagnosed?
**Yes.**
The "Correctness Gate" in the plan blocks performance timing. It demands that:
1. Both AuthorPatch and RTDL outputs exist.
2. Byte equality is checked.
3. If byte equality fails, a detailed topology/chain mismatch diagnostic is computed (chain count, multiset coordinates hash, etc.).
4. No performance timing comparisons are allowed unless correctness matches or is explicitly diagnosed as topology-equivalent.

### 9. Did Goal4858 avoid runtime/native edits, POD spend, and Section 5.7 overclaims?
**Yes.**
The preflight audit was purely an internal planning and analysis task. It did not touch `src/rtdsl/**` or `src/native/**`, did not issue POD command runs, and did not make premature overlay or reproduction claims.

### 10. Should Goal4858 close with `completed_section57_preflight__go_directly_to_57` and authorize Goal4859?
**Yes.**
The dependency analysis is complete and accurate. Authorizing [goal4859_rayjoin_section57_overlay_correctness_execution_plan_2026-07-01.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4859_rayjoin_section57_overlay_correctness_execution_plan_2026-07-01.md) to proceed with County x Zipcode overlay correctness testing is the optimal next step.

---

## Verdict Summary

> [!NOTE]
> **Verdict Label:** `approve_goal4858_go_directly_to_section57`
>
> The dependency audit meets all rigorous correctness and API boundary requirements. Proceed directly to Section 5.7 execution under the [Goal4859 Plan](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4859_rayjoin_section57_overlay_correctness_execution_plan_2026-07-01.md).
