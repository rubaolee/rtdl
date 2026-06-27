# Gemini Review: Goals4197-4198 Two-Pass Boundary Policy

Date: 2026-06-09
Reviewer: Gemini CLI
Verdict: `accept`

## Summary

This review covers the implementation and evidence for the `lowest_component_root_two_pass` boundary assignment policy in RTDL's fixed-radius grouped-stream front door. Goal4197 introduced the policy orchestration in the Python partner adapters, while Goal4198 provided pod evidence of its execution on RTX 4000 Ada hardware.

## Review Questions

### 1. Does Goal4197 keep the native engine app-agnostic, with no DBSCAN/clustering policy embedded in native ABI or native semantic names?

**Answer:** Yes. The native OptiX engine (`src/native/optix/rtdl_optix_core.cpp`) remains agnostic of the two-pass policy. It provides generic primitives like `apply_device_grouped_union_self` which perform predicated union operations and record the lowest root seen in a fallback candidate workspace. The "two-pass" logic is entirely orchestrated in the Python `PartnerAdapter` (`src/rtdsl/partner_adapters.py`), which calls the native primitive twice and resets the intermediate workspace between passes.

### 2. Is the `lowest_component_root_two_pass` policy explicit and user-selected, not hidden dispatch or auto-partner selection?

**Answer:** Yes. The policy is exposed as an explicit choice in `rt.plan_v2_8_fixed_radius_graph_component_continuation` and related front-door functions. It is not the default policy (which remains `lowest_candidate_then_root`), and it currently requires an explicit `partner="numba"` selection, failing with a `ValueError` if used with other partners like CuPy.

### 3. Does Goal4198 prove only RTX execution and metadata integrity, not speedup, release readiness, true zero-copy, or broad RT-core claims?

**Answer:** Yes. The Goal4198 report and its associated pod artifacts (`two_pass_clustered_smoke.stdout.json`) explicitly disclaim performance, release, and zero-copy claims. All relevant metadata flags (`public_speedup_claim_authorized`, `true_zero_copy_claim_authorized`, etc.) are set to `false`. The evidence focus is strictly on the integrity of the pass count and policy naming in the recorded metadata.

### 4. Is the clustered pod artifact credible evidence that the native route reports pass count `1` for the default policy and `2` for the two-pass policy while preserving the counts-only signature?

**Answer:** Yes. The pod artifact clearly distinguishes between the two policies. It records `native_boundary_assignment_pass_count: 1` for the default policy and `native_boundary_assignment_pass_count: 2` for the new two-pass policy. The artifact also confirms `same_counts_only_signature: true`, verifying that the underlying signature format remains consistent regardless of the pass count.

### 5. What should be required before this policy can become a promoted default or release-facing RT-DBSCAN route?

**Answer:**
- **Expanded Correctness Parity:** Exhaustive validation against the Goal4194 reference contract across diverse datasets (e.g., highly fragmented clusters, overlapping spheres, and noise-heavy distributions).
- **Convergence Justification:** Empirical evidence that the two-pass policy provides a convergence or accuracy benefit that justifies the 2x overhead of native traversal.
- **Partner Parity:** Implementation of the two-pass orchestration for other partners (CuPy, Torch, Triton) to ensure backend neutrality.
- **Formal Release Gate:** Completion of a formal v2.8 release audit and removal of the "preview" status in the front-door plan.

## Conclusion

The Goal4197/4198 chain successfully introduces a more robust boundary assignment policy without polluting the native engine with application-specific semantics. The orchestration is clean, the policy is explicit, and the evidence for metadata integrity is solid.
