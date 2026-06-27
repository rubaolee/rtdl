# Independent Gemini Review: Goal4169 RT-DBSCAN Road3D 2M Scale Probe

Review Date: Tuesday, June 09, 2026
Reviewer: Gemini CLI
Verdict: `accept`

## Overview

Goal4169 provides scale evidence for the RT-DBSCAN all-predicate fast path at 2,097,152 points using the `road3d` dataset. This review evaluates the report, the pod artifact, the associated test, and the registry update against the project's strict claim-boundary and advisory-only requirements.

## Question Responses

### 1. Does the report correctly distinguish the generic component-size schema from the RT-DBSCAN app/reference signature shape?

**Yes.** The report (`goal4169...md`) and artifact (`goal4169...pod.json`) explicitly separate the "generic component schema" from the "RT-DBSCAN app signature shape."
- The `prepared_direct_status_until_stable` row is correctly identified as returning a generic component list (`{"component_count": 1, "component_sizes": [2097152], ...}`).
- The `predicate_all_true_until_stable` row is correctly identified as matching the RT-DBSCAN app signature (`{"cluster_sizes": {"1": 2097152}, "core_count": 2097152, "noise_count": 0}`).
- The test `test_plain_component_signature_is_fast_but_not_the_app_signature_shape` confirms this distinction is enforced during validation.

### 2. Does the artifact support the bounded claim that the all-predicate wrapper matches the current RT-DBSCAN signature and remains above parity at road3d 2M?

**Yes.** The pod artifact records a measured speedup of **1.411x** (`predicate_all_true_until_stable` vs `current_grouped_stream_numba`) at the 2,097,152 point scale. The metadata confirms `all_predicate_fast_path: true` and `border_candidate_updates: 0`, supporting the claim that the fast path remains effective and correct at this scale for road-like profiles.

### 3. Does the registry update remain advisory and avoid hidden route, partner, factor, or border-policy selection?

**Yes.** The update to `src/rtdsl/current_benchmark_route_decisions.py` (version `rtdl.v2_10.current_benchmark_route_decisions.goal4169.v1`) maintains all safety guards:
- `user_explicit_choice_required` remains `True`.
- `automatic_partner_selection_authorized` and other authorization flags remain `False`.
- The `user_choice_guidance` for `rt_dbscan` explicitly warns: "Do not auto-select the partner, route, factor, or border policy."
- The registry notes that Goal4169 is "advisory guidance only."

### 4. Does the report avoid release, public speedup, whole-app, broad RT-core, and route-promotion overclaims?

**Yes.** Both the MD report and the JSON artifact contain explicit boundary sections that deny authorization for:
- Release and public speedup wording.
- Whole-app benchmark claims.
- Broad RT-core acceleration wording.
- Automatic route/partner/factor/policy selection.
- AMD performance or true-zero-copy claims.

### 5. Does this evidence change the next engineering priority, or should mixed-predicate border policy and/or one-shot prepare cost remain the next targets?

**The priority remains unchanged.** The report acknowledges that Goal4169 "does not solve mixed-predicate rows" and that Goals4165-4168 (focusing on mixed-predicate border policies) still stand. The registry's `next_runtime_action` correctly identifies one-shot prepare-cost reduction and generic border-assignment policies as the next serious targets. This scale probe successfully validates the upper bound for all-predicate road-like profiles without diverting resources from the primary mixed-predicate blockers.

## Conclusion

Goal4169 is a high-quality scale probe that provides necessary evidence for the v0.4 release prep without overstepping its research boundaries. The implementation of the all-predicate wrapper is correctly validated as signature-compatible with the legacy reference.

**Verdict: `accept`**
