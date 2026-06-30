# Gemini Review: Goal3325 RayJoin Boundary and Candidate Primitive

**Date:** 2026-06-04
**Reviewer:** Gemini CLI
**Verdict:** accept-with-boundary

## Executive Summary

This review assesses the RayJoin PIP boundary chain and the proposed `candidate.closed_shape_topology_membership_count_2d` primitive. The current fast scalar count route for point-in-polygon (PIP) demonstrates a correctness boundary with complex `br_county` datasets, exhibiting overcounting due to topology/degeneracy issues, while remaining accurate for simpler `br_soil` datasets (Goal3320). To mitigate this, an app-level preflight API (`preflight_rayjoin_pip_fast_count_domain`) has been successfully implemented and validated, ensuring the fast path fails closed on unsuitable domains, preventing "hidden dispatcher magic" (Goal3321). Per-point mismatch diagnosis confirms a structured overcounting pattern, strongly supporting the hypothesis that a richer, topology-aware, boundary-owning, and duplicate-gated primitive is necessary (Goal3322). The new candidate primitive `candidate.closed_shape_topology_membership_count_2d` is well-defined, app-agnostic, and correctly integrated into the primitive hierarchy and catalog, passing duplicate-gating checks (Goal3324). All specified release, public speedup, RTDL-beats-RayJoin, RayJoin reproduction, broad RT-core, and true-zero-copy claims are consistently and explicitly blocked across all reports and code. The work clearly identifies and manages the existing boundary, and the proposed candidate addresses the identified gaps without violating RTDL's app-agnostic principles.

## Review Questions & Answers

### 1. Are the validation artifacts internally consistent and correctly interpreted?

Yes, the validation artifacts (reports and JSON files for Goal3320, Goal3321, Goal3322) are internally consistent and correctly interpreted.

*   **Goal3320:** The `goal3320_rayjoin_pip_full_dataset_validation_boundary_2026-06-04.md` report accurately summarizes the data from `goal3320_rayjoin_pip_device_count_validation_matrix_2026-06-04.json`. It correctly identifies that the fast route works for `br_soil_start256_count512.cdb` but overcounts for `br_county.cdb` and `br_county_start256_count512.cdb`. The interpretation correctly points to a "correctness boundary, not a timing failure" and suggests a need for a richer generic closed-shape topology contract.
*   **Goal3321:** The `goal3321_rayjoin_pip_validated_domain_preflight_2026-06-04.md` report correctly describes the preflight API and its behavior, matching the data in `goal3321_rayjoin_pip_preflight_pod_smoke_2026-06-04.json`. It confirms that the preflight correctly identifies valid domains and rejects mismatched ones, requiring fallback.
*   **Goal3322:** The `goal3322_rayjoin_pip_per_point_mismatch_diagnosis_2026-06-04.md` report provides a detailed interpretation of the per-point mismatch data in `goal3322_rayjoin_pip_per_point_mismatch_diagnosis_2026-06-04.json`. The analysis clearly shows a structured overcount, pointing to topology/boundary issues rather than random errors.

All reports consistently block claims regarding release, public speedup, RT-core speedup, true zero-copy, RTDL-beats-RayJoin, and RayJoin paper reproduction.

### 2. Does the preflight API make the fast path fail closed without becoming hidden dispatcher magic?

Yes, the preflight API (`preflight_rayjoin_pip_fast_count_domain`) makes the fast path fail closed without becoming hidden dispatcher magic.

*   The `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py` code shows `preflight_rayjoin_pip_fast_count_domain` explicitly compares `fast_count` with `exact_count` and sets `matches_exact` and `fallback_required` flags. If `require_match=True`, it raises a `RuntimeError` on mismatch, explicitly failing closed.
*   The `native_engine_boundary` metadata in the preflight results states: "The engine sees generic point/closed-shape count primitives. RayJoin CDB topology policy remains in Python preflight/fallback logic." This confirms that the policy and decision-making for the fast path remain at the app level in Python, not hidden within the native engine.
*   The `goal3321_rayjoin_pip_validated_domain_preflight_2026-06-04.md` report explicitly calls this out, stating "This is app-level benchmark policy over generic RTDL primitives. It does not authorize the native engine to infer RayJoin semantics."

### 3. Does the mismatch diagnosis support a topology/boundary/duplicate-policy design hypothesis?

Yes, the mismatch diagnosis strongly supports a topology/boundary/duplicate-policy design hypothesis for future primitives.

*   The `goal3322_rayjoin_pip_per_point_mismatch_diagnosis_2026-06-04.md` report details that all mismatches are overcounts, with no undercounts, and several involve points with duplicate coordinates. This pattern is not random but suggests a systematic issue related to how complex geometries (like those in `br_county.cdb`) are interpreted, especially regarding boundaries and potential duplicate assignments.
*   The report explicitly concludes: "This points away from random launch instability and toward a semantic contract gap around CDB topology, boundary degeneracy, duplicate ownership, ring/chain identity, or face assignment policy." It further states that the next major primitive should be a "generic face/topology-aware closed-shape membership/count contract with explicit deterministic boundary ownership and duplicate policy." This directly aligns with the proposed design hypothesis.

### 4. Does the candidate primitive remain app-agnostic and duplicate-gated?

Yes, the candidate primitive `candidate.closed_shape_topology_membership_count_2d` remains app-agnostic and is duplicate-gated.

*   **App-agnostic:** The `src/rtdsl/primitive_hierarchy.py` and `docs/rtdl_primitive_catalog.md` both define a clear `boundary` for this candidate: "The primitive must expose generic topology and boundary-ownership policy only. CDB source naming, RayJoin assignment interpretation, map/entity lookup, and paper-system semantics remain app code." The `goal3324_closed_shape_topology_membership_candidate_2026-06-04.md` report reiterates this, explicitly excluding "RayJoin-specific map/entity semantics" and "paper-system reproduction policy" from the native engine's purview.
*   **Duplicate-gated:** The `tests/goal3324_closed_shape_topology_membership_candidate_test.py` test explicitly verifies that the candidate passes `rt.validate_primitive_hierarchy` with `enforce_promotion_metadata=True` and `promotion_candidate_ids=(NODE_ID,)`. This means it satisfies the requirements for `considered_alternatives` and `distinct_from`, which are in place to prevent the promotion of redundant primitives and maintain a clean hierarchy. The report itself lists several alternatives (`traversal.count_hits`, `rows.point_closed_shape_boundary_event_columns`, `reduction.grouped`, `candidate.device_grouped_candidate_merge`) and explains why this candidate is distinct.

### 5. Are the generated catalog and tests aligned with the hierarchy source of truth?

Yes, the generated catalog and tests are aligned with the hierarchy source of truth.

*   **Generated Catalog:** The `docs/rtdl_primitive_catalog.md` explicitly states it is "Generated from `src/rtdsl/primitive_hierarchy.py`" and should not be hand-edited. Its structure and content directly reflect the `PRIMITIVE_HIERARCHY` defined in `primitive_hierarchy.py`, including the presence and details of `candidate.closed_shape_topology_membership_count_2d`. The validation snapshot within the catalog shows `Hierarchy validation valid: True` and `Strict discovery metadata validation valid: True`.
*   **Tests:** The tests (`tests/goal3324_closed_shape_topology_membership_candidate_test.py`) specifically import `rtdsl` and use `rt.describe_primitive(NODE_ID)` and `rt.validate_primitive_hierarchy(...)` to programmatically verify the node's properties, status, layer, capabilities, dependencies, and boundary against the `primitive_hierarchy.py` source of truth. This direct testing against the Python source confirms alignment.

### 6. Are all release, public speedup, RTDL-beats-RayJoin, RayJoin reproduction, broad RT-core, and true-zero-copy claims still blocked?

Yes, all specified claims remain explicitly blocked across all relevant reports and code.

*   Each of the reports (`goal3320_rayjoin_pip_full_dataset_validation_boundary_2026-06-04.md`, `goal3321_rayjoin_pip_validated_domain_preflight_2026-06-04.md`, `goal3322_rayjoin_pip_per_point_mismatch_diagnosis_2026-06-04.md`, `goal3324_closed_shape_topology_membership_candidate_2026-06-04.md`) contains a "Claim Boundary" section with all these claims explicitly set to `false`.
*   The code in `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py` consistently includes `claim_boundary` dictionaries where these flags are set to `False` in functions like `preflight_rayjoin_pip_fast_count_domain` and `run_rayjoin_prepared_optix_workload`.
*   The `docs/rtdl_primitive_catalog.md` (generated from `primitive_hierarchy.py`) also includes a "Claim Boundary" section that blocks these claims broadly.
*   The tests for each goal specifically assert that these `claim_boundary` flags are `False`, ensuring that any changes would break the tests.


## Claims Status

All release, public speedup claims, RayJoin paper reproduction claims, RTDL-beats-RayJoin claims, broad RT-core speedup claims, and true-zero-copy claims are still blocked. App-specific native-engine direction is also blocked.
