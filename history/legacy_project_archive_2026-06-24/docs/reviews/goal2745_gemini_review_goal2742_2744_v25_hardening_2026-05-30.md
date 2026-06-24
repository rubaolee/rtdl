# Gemini Independent Review: Goals2742-2744 v2.5 Hardening

Date: 2026-05-30

Verdict: accept-with-boundary

## Review Summary

This review covers the hardening goals 2742, 2743, and 2744, focusing on the preservation of metadata, explicit boundary definitions for Triton group-id validation, and auditing of native hit-stream release mechanisms within RTDL v2.5. The changes appear to correctly address the identified hardening aspects, with particular attention paid to avoiding over-claiming on performance, true zero-copy capabilities, or partner replacement. The associated tests and reports consistently reinforce these conservative claims and boundary definitions.

## Review Questions Addressed

### 1. Does Goal2742 correctly preserve stream-ordering metadata without claiming stream synchronization is proven?

**Yes.** Goal2742 correctly preserves `producer_consumer_stream_ordering` metadata when the OptiX runtime rebuilds a hit-stream handoff. The report `docs/reports/goal2742_optix_hit_stream_metadata_preservation_2026-05-30.md` explicitly states that this change is for "metadata preservation, not a new synchronization proof." The test `tests/goal2738_native_hit_stream_stream_ordering_boundary_test.py` verifies that `producer_consumer_stream_ordering` is indeed preserved and that `true_zero_copy_authorized` remains `False`, confirming that no premature stream synchronization claims are made.

### 2. Does Goal2743 honestly expose Triton's current group-id validation as a host-scalar-sync precheck, not a future device-resident error-flag path?

**Yes.** Goal2743 honestly exposes the current Triton group-id validation. The report `docs/reports/goal2743_triton_group_id_validation_boundary_2026-05-30.md` details that the validation occurs as a "Torch CUDA predicate followed by a host scalar sync" and is not a device-resident error-flag path. The `src/rtdsl/triton_partner_continuation.py` file sets `TRITON_GROUP_ID_BOUNDS_VALIDATION_MODE = "torch_cuda_precheck_host_scalar_sync"` and `TRITON_GROUP_ID_BOUNDS_DEVICE_ERROR_FLAG_AVAILABLE = False`. The test `tests/goal2743_triton_group_id_validation_boundary_test.py` validates these explicit metadata settings, ensuring the boundary is clearly communicated without implying advanced device-resident capabilities or true zero-copy claims.

### 3. Does Goal2744 correctly classify native release-entrypoint status as "present/audited" while keeping broader native lifetime, multi-driver, and true-zero-copy claims blocked?

**Yes.** Goal2744 accurately classifies the native release-entrypoint status. The audit report `docs/reports/goal2744_native_hit_stream_release_enforcement_audit_2026-05-30.md` confirms the presence and correct implementation of the `rtdl_optix_release_ray_triangle_hit_stream_device_columns` symbol across native and Python code. Crucially, the report explicitly states that this audit "does not close all native-lifetime risk" and that "true zero-copy and public speedup claims remain unauthorized." The test `tests/goal2744_native_hit_stream_release_enforcement_audit_test.py` verifies the presence of the release symbol, its invocation, and that `true_zero_copy_authorized` is `False` in handoff metadata, aligning with the conservative claims.

### 4. Do the tests catch the intended regressions without overfitting to stale historical wording?

**Yes.** The tests appear well-scoped to catch regressions related to the specific hardening goals without overfitting. Each test focuses on the explicit metadata and behavior changes defined by its respective goal, such as stream-ordering preservation (`goal2738_..._test.py`), group-id validation modes (`goal2743_..._test.py`), and release symbol enforcement (`goal2744_..._test.py`). They specifically check for `False` values on claims like `true_zero_copy_authorized`, indicating a deliberate effort to prevent misrepresentation of capabilities rather than merely matching historical phrasing.

### 5. Are public speedup, true-zero-copy, and partner-replacement claim boundaries preserved?

**Yes.** All three hardening goals, as documented in their respective reports and implemented in code/tests, diligently preserve public speedup, true-zero-copy, and partner-replacement claim boundaries.
- **Goal2742:** The report states, "No true-zero-copy claim is authorized." and "No stream synchronization claim is authorized."
- **Goal2743:** The report explicitly says, "No performance claim is authorized." and "No true-zero-copy claim is authorized." `src/rtdsl/triton_partner_continuation.py` consistently sets `promoted_performance_path=False` and `rt_core_speedup_claim_authorized=False` in its run results and descriptors.
- **Goal2744:** The report reiterates, "true zero-copy and public speedup claims remain unauthorized."
The `src/rtdsl/triton_partner_continuation.py` file also defines `claim_boundary` for Triton operations, indicating that Triton is a "continuation partner" but that "RTDL/OptiX traversal remains separate," thus preserving partner-replacement claim boundaries. The tests confirm these limitations by asserting appropriate flags are set to `False`.
