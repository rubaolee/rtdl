# Gemini Review - Goal2774 v2.5 Grouped Hit-Stream Support Matrix

**Date:** 2026-05-31

**Verdict:** accept

## Findings

### 1. Confirm the new operation name and field names are generic/app-agnostic.

The new operation `hit_stream_grouped_ray_id_primitive_i64` defined in `src/rtdsl/partner_continuation_protocol.py` is indeed generic and app-agnostic.

*   **Operation Name:** `hit_stream_grouped_ray_id_primitive_i64` is descriptive of its function (grouping hit streams by ray ID and reducing primitive IDs) without implying any specific application.
*   **Input Names:** (`ray_ids`, `primitive_ids`, `row_count`, `hit_event_count`, `overflow`, `group_count`) are all generic terms.
*   **Output Names:** (`group_hit_counts`, `group_primitive_id_sum`, `group_primitive_id_xor`, `group_primitive_id_min`, `group_primitive_id_max`, `group_first_hit_row_index`, `group_last_hit_row_index`, `group_first_primitive_id`, `group_last_primitive_id`) are also generic aggregate statistics.
*   **Behavior Description:** The `behavior` string explicitly states "group event-ordered RT hit-stream rows by generic ray_id; reduce nonnegative primitive_id rows with count, sum, xor, min, max, and first/last row-order primitive ids; ray ids must be in [0, group_count); empty groups use signed -1 sentinels; overflow fails closed without returning partial reductions". This description is purely functional and avoids application-specific terminology.
*   **`app_specific_semantics_allowed`:** The `RtdlPartnerContinuationOperation` for this operation is correctly set with `app_specific_semantics_allowed=False`.

### 2. Confirm the support matrix is honest:

The support matrix, as defined in `src/rtdsl/v2_5_partner_support_matrix.py` and validated by `tests/goal2774_v2_5_grouped_hit_stream_support_matrix_test.py`, accurately reflects the stated support levels:

*   **`python_reference`**: `reference_contract`. This is confirmed in `src/rtdsl/v2_5_partner_support_matrix.py` where `V25PartnerSupportCell` for `python_reference` and any operation explicitly sets `status=V2_5_SUPPORT_STATUS_REFERENCE`.
*   **`cupy_conformance`**: `preview_not_promoted`. For the `hit_stream_grouped_ray_id_primitive_i64` operation, the `V25PartnerSupportCell` for `cupy_conformance` correctly sets `status=V2_5_SUPPORT_STATUS_PREVIEW` and notes that it's a preview from Goals2771-2772 and remains unpromoted.
*   **`triton`**: `unsupported_fail_closed`. For the `hit_stream_grouped_ray_id_primitive_i64` operation, the `V25PartnerSupportCell` for `triton` correctly sets `status=V2_5_SUPPORT_STATUS_UNSUPPORTED` with the note "Triton preview kernel is not implemented for this operation."
*   **`numba`**: `unsupported_fail_closed`. Similarly, for `numba`, the status is `V2_5_SUPPORT_STATUS_UNSUPPORTED` with the note "Numba fallback kernel is not implemented for this operation."

### 3. Confirm Goal2774 does not authorize public speedup, release, true zero-copy, or RT traversal replacement claims.

The code and documentation consistently confirm that Goal2774 explicitly does not authorize these claims:

*   **`src/rtdsl/v2_5_partner_support_matrix.py`**:
    *   `V2_5_RT_TRAVERSAL_REPLACEMENT_ALLOWED` is `False`.
    *   `public_speedup_claim_authorized` is `False`.
    *   `true_zero_copy_claim_authorized` is `False`.
    *   The `V25PartnerSupportCell` class has assertions preventing `promoted_performance_path`, `rt_traversal_replacement_allowed`, `public_speedup_claim_authorized`, and `true_zero_copy_claim_authorized` from being set to `True`.
*   **`src/rtdsl/partner_continuation_protocol.py`**:
    *   `V2_5_PERFORMANCE_PATH_AUTHORIZED` is `False`.
    *   `V2_5_RT_TRAVERSAL_REPLACEMENT_ALLOWED` is `False`.
    *   `V2_5_RAWKERNEL_REQUIRED_ALLOWED` is `False`.
    *   The `RtdlPartnerContinuationSpec` class also has checks preventing `replaces_rt_traversal`, `raw_kernel_required`, and `promoted_performance_path` from being `True`.
*   **`docs/reports/goal2774_v2_5_grouped_hit_stream_support_matrix_2026-05-31.md`**: The "Boundary" section explicitly states "Goal2774 does not authorize: no public speedup claims, true zero-copy claims, release readiness, partner replacement of RTDL/OptiX traversal, app-specific primitive semantics inside the engine or generic partner contract."

### 4. Confirm the reference semantics match Goal2772: row-order first/last and `-1` empty-group sentinels.

The reference implementation in `src/rtdsl/partner_continuation_protocol.py` (function `_hit_stream_grouped_ray_id_primitive_i64`) and its tests in `tests/goal2662_v2_5_partner_continuation_contract_test.py` and `tests/goal2774_v2_5_grouped_hit_stream_support_matrix_test.py` (which includes the test from `tests/goal2772_hit_stream_event_ordered_grouped_richer_reductions_test.py`) confirm these semantics:

*   **Row-order first/last:** The implementation correctly captures `first_row[group] = row_index` and `last_row[group] = row_index` based on the iteration order (`for row_index in range(row_count)`). The corresponding `first_primitive[group] = primitive` and `last_primitive[group] = primitive` also reflect the first and last primitives encountered in row order.
*   **`-1` empty-group sentinels:** The initialization of `primitive_min`, `primitive_max`, `first_row`, `last_row`, `first_primitive`, and `last_primitive` with `-1` (represented by the `missing` variable) correctly handles empty groups, as demonstrated in the tests (e.g., `group 1` in `test_reference_hit_stream_grouped_ray_id_primitive_reduction` test in `goal2662`).

### 5. Confirm the changed older tests still preserve the v2.5 Triton-first/Numba fallback policy without pretending this new CuPy preview is a Triton kernel.

The tests (`tests/goal2662_v2_5_partner_continuation_contract_test.py` and `tests/goal2696_v2_5_partner_support_matrix_test.py`) demonstrate that the existing Triton-first/Numba fallback policy is preserved, and the new CuPy preview is not mistakenly treated as a Triton kernel.

*   **Planner Logic:** The `test_planner_prefers_triton_then_numba_then_reference` in `goal2662_v2_5_partner_continuation_contract_test.py` explicitly shows that for operations where Triton or Numba have previews (e.g., `segmented_sum_f64`), those partners are preferred. However, for `hit_stream_grouped_ray_id_primitive_i64`, if only `triton` is available, it correctly falls back to `python_reference` because Triton explicitly `unsupported_fail_closed` for this operation. When `cupy` is available, it correctly selects `cupy_conformance` for the new operation.
*   **Support Matrix Honesty:** The `goal2696_v2_5_partner_support_matrix_test.py` confirms that for the `hit_stream_grouped_ray_id_primitive_i64` operation, Triton and Numba cells are `unsupported_fail_closed`, while CuPy is `preview_not_promoted`. This means the system correctly identifies that Triton and Numba do not have an implementation for this specific operation.

### 6. List any blockers or required follow-up before Goal2775.

Based on the handoff document and code inspection, the following are either explicit blockers or implied follow-ups:

*   **Benchmark Integration and Performance Promotion:** The `V2_5_PREVIEW_GATE_STATUS` (`internal_v2_5_preview_pod_validation_required`) and the `remaining_validation_scope` in `v2_5_partner_preview_gate()` (from `src/rtdsl/partner_continuation_protocol.py`) clearly state that "full RT hit-stream handoff, benchmark integration, optimized performance path, and external 3-AI consensus" are remaining validation steps. The current CuPy preview for `hit_stream_grouped_ray_id_primitive_i64` is "unpromoted" and does not authorize public speedup claims. Full benchmark integration and performance promotion for this operation would be a significant follow-up.
*   **Triton/Numba Implementation:** The current status for Triton and Numba for the `hit_stream_grouped_ray_id_primitive_i64` operation is `unsupported_fail_closed`. Implementing Triton and/or Numba kernels for this operation would be a required follow-up to provide broader support and potentially better performance within the primary partner ecosystem.
*   **External 3-AI Consensus:** `V2_5_PREVIEW_GATE_STATUS` also mentions that "external 3-AI consensus" is required. This implies a need for further review and agreement from external stakeholders before broader adoption or promotion.

No immediate blockers for Goal2775 are identified within the scope of this review, assuming Goal2775 builds upon the current "preview" status and does not require full promotion or Triton/Numba implementation yet. However, the listed follow-ups are crucial for the eventual maturity and broader adoption of this operation.