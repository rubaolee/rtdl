# Gemini Review: Goal2947 Payload-Mapped Hit-Stream Continuation

Date: 2026-06-01
Verdict: accept-with-boundary

## Review Summary

Goal2947 successfully introduces a generic v2.5 event-ordered RT hit-stream continuation: `hit_stream_primitive_payload_grouped_sum_f64`. This operation allows users to map event-ordered RT hit-stream primitive IDs through generic primitive payload columns and compute grouped sums. The implementation adheres strictly to app-agnostic boundaries and transparently manages partner support, with CuPy identified as the executable preview partner while Triton and Numba correctly fail closed. The pod smoke test validates the intended device-resident, event-ordered producer-consumer path without host scalar or row materialization before the consumer. Claim boundaries are meticulously maintained, preventing overstatements regarding release, public speedup, or true zero-copy. The primary area for future work lies in optimizing the CuPy consumer for larger scale.

## Review Questions and Findings

1.  **Does Goal2947 preserve the app-agnostic engine boundary?**
    *   **Finding:** Yes.
    *   **Evidence:**
        *   `src/rtdsl/partner_continuation_protocol.py`: The `RtdlPartnerContinuationOperation` for `hit_stream_primitive_payload_grouped_sum_f64` explicitly sets `app_specific_semantics_allowed=False`. Its behavior description uses generic terms like `primitive_id`, `primitive_group_ids`, and `primitive_values`.
        *   `src/rtdsl/generic_primitives.py`: The `GenericPreparedRayTriangleEventOrderedPayloadGroupedSum3D` metadata includes `"native_engine_app_specific_vocab_allowed": False` and `"generic_user_facing_primitive": True`.
        *   `docs/reports/goal2947_generic_event_ordered_payload_grouped_sum_front_door_2026-06-01.md`: The "Purpose" section explicitly states, "No app terms are added to the native engine."
        *   `docs/reports/goal2947_generic_event_ordered_payload_grouped_sum_front_door_pod/goal2947_payload_grouped_sum_smoke.json`: The `metadata.native_engine_app_specific_vocab_allowed` field is `false`.

2.  **Is `hit_stream_primitive_payload_grouped_sum_f64` a generic primitive rather than hidden app logic?**
    *   **Finding:** Yes.
    *   **Evidence:**
        *   `src/rtdsl/partner_continuation_protocol.py`: The `behavior` for the operation describes a generic data transformation and reduction: "map event-ordered RT hit-stream primitive_id rows through generic primitive payload columns, then sum float64 primitive_values per primitive_group_id...". This clearly defines a mathematical operation without app-specific context.
        *   The operation's inputs (`ray_ids`, `primitive_ids`, `primitive_group_ids`, `primitive_values`) are abstract and do not embed domain-specific semantics.

3.  **Are partner boundaries honest: explicit CuPy preview, Triton/Numba fail closed, no hidden forced partner path?**
    *   **Finding:** Yes.
    *   **Evidence:**
        *   `src/rtdsl/partner_continuation_protocol.py`: `V2_5_CUPY_PREVIEW_OPERATIONS` includes `hit_stream_primitive_payload_grouped_sum_f64`, while `V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS` (Triton) and `V2_5_NUMBA_PREVIEW_OPERATIONS` do not.
        *   `src/rtdsl/v2_5_partner_support_matrix.py`: For `hit_stream_primitive_payload_grouped_sum_f64`, CuPy's status is `V2_5_SUPPORT_STATUS_PREVIEW`, while Triton and Numba are explicitly marked `V2_5_SUPPORT_STATUS_UNSUPPORTED` with corresponding notes.
        *   `tests/goal2947_generic_event_ordered_payload_grouped_sum_front_door_test.py`: The test `test_operation_is_declared_and_supported_only_by_cupy_preview` and `test_unsupported_partner_fails_closed_before_optix_runtime` confirm this behavior, verifying that Triton fails closed.
        *   `docs/reports/goal2947_generic_event_ordered_payload_grouped_sum_front_door_2026-06-01.md`: States "Current executable partner: `cupy` / `cupy_conformance`" and "Triton and Numba fail closed for this operation".

4.  **Does the pod smoke prove the intended event-ordered RT producer plus CuPy consumer path without host scalar/row materialization before the consumer?**
    *   **Finding:** Yes.
    *   **Evidence:**
        *   `docs/reports/goal2947_generic_event_ordered_payload_grouped_sum_front_door_pod/goal2947_payload_grouped_sum_smoke.json`:
            *   `metadata.producer_consumer_stream_ordering`: `"cuda_event_cross_stream"`
            *   `metadata.cuda_event_wait_inserted_before_consumer`: `true`
            *   `metadata.host_scalar_read_before_consumer`: `false`
            *   `metadata.host_row_materialization_before_consumer`: `false`
            *   `metadata.device_resident_payload_columns_for_partner`: `true`
            *   `metadata.grouped_output_columns_written_on_device`: `true`
            *   `summary.consumer_read_rows_on_device`: `true`
            *   `summary.consumer_read_status_on_device`: `true`
        *   `docs/reports/goal2947_generic_event_ordered_payload_grouped_sum_front_door_2026-06-01.md`: The "Observed pod result" confirms these facts, explicitly stating "host row materialization before consumer: `false`" and "device status read before host scalar: `true`".

5.  **Are claim boundaries intact: no release, public speedup, broad RT-core, whole-app speedup, true-zero-copy, package-install, paper reproduction, or app-specific native engine logic?**
    *   **Finding:** Yes.
    *   **Evidence:**
        *   Across `src/rtdsl/partner_continuation_protocol.py`, `src/rtdsl/v2_5_partner_support_matrix.py`, `src/rtdsl/v2_5_partner_conformance_matrix.py`, and `src/rtdsl/v2_5_determinism_policy.py`, various flags such as `_RELEASE_TAG_AUTHORIZED`, `_PUBLIC_SPEEDUP_CLAIM_AUTHORIZED`, `_RT_TRAVERSAL_REPLACEMENT_ALLOWED`, `promoted_performance_path`, `true_zero_copy_claim_authorized`, `broad_rt_core_claim_authorized`, and `whole_app_speedup_claim_authorized` are consistently set to `False` and enforced in constructors/validation functions.
        *   `src/rtdsl/generic_primitives.py`: The `GenericPreparedRayTriangleEventOrderedPayloadGroupedSum3D` metadata explicitly sets these authorization flags to `False`.
        *   `scripts/goal2947_generic_event_ordered_payload_grouped_sum_front_door_smoke.py`: The `claim_boundary` in the generated JSON sets all relevant authorization flags to `False`.
        *   `docs/reports/goal2947_generic_event_ordered_payload_grouped_sum_front_door_2026-06-01.md`: The "Boundary" section explicitly disclaims all these authorizations.
        *   `docs/reports/goal2947_generic_event_ordered_payload_grouped_sum_front_door_pod/goal2947_payload_grouped_sum_smoke.json`: All relevant "authorized" flags in the `metadata` are `false`.

6.  **What performance risk should Codex attack next? In particular, comment on whether the current single-kernel CuPy consumer should be scale-probed and potentially optimized with multi-block partial reductions.**
    *   **Finding:** The current single-kernel CuPy consumer for `hit_stream_primitive_payload_grouped_sum_f64` poses a performance risk, particularly as the number of hits and groups increases. For grouped reduction operations on GPUs, a single global reduction kernel can become inefficient due to contention in global memory access patterns and suboptimal utilization of the GPU's memory hierarchy.
    *   **Recommendation:** Codex should prioritize **scale-probing** the performance of this CuPy consumer. If the scale probes identify bottlenecks, the next optimization step should involve implementing a **multi-block partial reduction strategy**. This would improve performance by:
        1.  **Leveraging shared memory:** Each GPU thread block would compute partial sums for a subset of groups, storing these intermediate results in fast shared memory.
        2.  **Reducing global memory traffic:** Once block-local reductions are complete, a subsequent kernel (or a coordinated multi-pass approach within a persistent kernel) would combine these partial sums from global memory, significantly reducing contention and improving overall efficiency for large datasets. This approach is standard for optimizing grouped reductions on GPUs.

## Conclusion

Goal2947 is well-designed and implemented, meeting its stated objectives and adhering to all critical boundaries. The new primitive is generic, partner interactions are explicit, and the technical claims are supported by evidence. The identified performance risk with the CuPy consumer is a natural next step for optimization, rather than a flaw in the current deliverable.
