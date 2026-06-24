# Goal2834 Gemini Review: Goal2833 Primitive Payload Partner Planner

Date: 2026-05-31

## Review Summary

This review assessed Goal2833, the Primitive Payload Partner Planner, focusing on its integration with Goal2831 descriptors and the existing v2.5 partner support matrix. The primary objective was to verify that the planner operates as a neutral, explainable contract for determining partner eligibility without introducing new execution logic or making unauthorized claims.

The review confirmed that Goal2833 successfully builds upon prior work, rigorously enforces fail-closed mechanisms with explicit fallback reasons, and maintains strict claim boundaries regarding performance, zero-copy, and arbitrary execution. The Python reference path is preserved without overstating capabilities, and the CuPy preview remains narrow and matrix-approved. The proposed next step of integrating planner decisions into continuation entrypoint metadata is a logical and reasonable progression.

## Files Inspected

-   `docs/reports/goal2833_primitive_payload_partner_planner_2026-05-31.md`
-   `tests/goal2833_primitive_payload_partner_planner_test.py`
-   `src/rtdsl/hit_stream_handoff.py`
-   `src/rtdsl/__init__.py`
-   `src/rtdsl/v2_5_partner_support_matrix.py`
-   `docs/reports/goal2831_primitive_payload_column_descriptors_2026-05-31.md`
-   `docs/reports/goal2832_goal2831_primitive_payload_column_descriptors_consensus_2026-05-31.md`

## Review Questions & Answers

### 1. Does Goal2833 build on the Goal2831 descriptors and existing support matrix instead of adding app-shaped routing?

**Answer:** Yes, Goal2833 explicitly builds on Goal2831 descriptors and the existing `v2.5_partner_support_matrix` by consuming them as inputs for its planning logic. This design avoids app-shaped routing, ensuring the planner remains partner-neutral and leverages established contracts.

### 2. Does the planner fail closed with explicit reasons for descriptor-only partners, host descriptors when CUDA is required, missing/invalid descriptor metadata, and unproven stream ordering?

**Answer:** Yes, the planner explicitly fails closed with specific fallback reasons for these scenarios. This is evident in the implementation of `plan_primitive_payload_partner_continuation` in `src/rtdsl/hit_stream_handoff.py`, where various conditions trigger the appending of descriptive fallback reasons such as "partner_unavailable", "host_reference", "lifetime_unproven", and "stream_ordering_unproven". Dedicated unit tests (`tests/goal2833_primitive_payload_partner_planner_test.py`) further confirm this fail-closed behavior for invalid inputs and unsupported configurations.

### 3. Does the accepted CuPy preview case remain narrow to the support-matrix-approved hit-stream grouped reduction path?

**Answer:** Yes, the CuPy preview case is intentionally narrow, restricted to the `hit_stream_grouped_ray_id_primitive_i64` operation and requiring CUDA with same-stream ordering. The `v2_5_partner_support_matrix` explicitly notes this narrow scope, and the corresponding test case (`test_cupy_preview_accepts_cuda_same_stream_descriptor_for_hit_stream_operation`) confirms that only this specific path is authorized as a preview.

### 4. Does the Python reference path remain available without pretending zero-copy or performance promotion?

**Answer:** Yes, the Python reference path remains available, accepting host descriptors as a `reference_contract` without authorizing any zero-copy or performance claims. The `plan_primitive_payload_partner_continuation` function consistently sets `true_zero_copy_authorized` and `public_speedup_claim_authorized` to `False` in its output, and the test suite verifies this behavior for Python reference plans.

### 5. Are claim boundaries strict: no arbitrary partner execution, RT traversal replacement, public speedup, broad true-zero-copy, paper reproduction, whole-app speedup, or v2.5 release claim?

**Answer:** Yes, the claim boundaries are rigorously strict. The `docs/reports/goal2833_primitive_payload_partner_planner_2026-05-31.md` and `src/rtdsl/hit_stream_handoff.py` explicitly list all these items as *not authorized*. The code enforces this by setting relevant flags (e.g., `rt_traversal_replacement_allowed`, `true_zero_copy_authorized`, `public_speedup_claim_authorized`) to `False` and including detailed `claim_boundary` strings in the planner's output.

### 6. Is the next step reasonable: attach planner decisions to real continuation entrypoint metadata?

**Answer:** Yes, the proposed next step is reasonable and aligns perfectly with the planner's design as an explainable contract. Attaching planner decisions, including explicit fallback reasons, to real continuation entrypoint metadata will enhance transparency, debuggability, and allow downstream systems to accurately report on why certain execution paths were chosen or why operations were deferred to a reference.

## Verdict

`accept-with-boundary`
