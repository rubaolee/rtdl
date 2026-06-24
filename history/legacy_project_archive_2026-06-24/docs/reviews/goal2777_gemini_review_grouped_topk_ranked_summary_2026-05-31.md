# Goal2777 Grouped Top-K Ranked Summary Gemini Review - 2026-05-31

## Review Questions and Answers:

1.  **Confirm `grouped_topk_f64` is generic and not RTNN/app-specific.**
    *   **Evidence:**
        *   `src/rtdsl/partner_continuation_protocol.py`: The `RtdlPartnerContinuationOperation` for `grouped_topk_f64` has `app_specific_semantics_allowed=False`. The `behavior` description ("select up to k lowest-score distinct items per group with deterministic score-then-item-id order") is generic. The `V2_4_FORBIDDEN_NATIVE_APP_TOKENS` are checked against operation names.
        *   `tests/goal2662_v2_5_partner_continuation_contract_test.py`: Asserts that `operation` must reject app-specific semantics and that `V2_4_FORBIDDEN_NATIVE_APP_TOKENS` are not in serialized contract.
        *   `docs/reports/goal2777_v2_5_grouped_topk_ranked_summary_2026-05-31.md`: States "This is not an RTNN-specific primitive." and describes its use for "any other caller-owned metric."
    *   **Verdict:** accept - The `grouped_topk_f64` operation is designed to be generic and explicitly prevents app-specific semantics.

2.  **Confirm reference semantics are deterministic: lowest score, lowest item id, duplicate item rows use the lowest score, explicit row offsets and missing groups.**
    *   **Evidence:**
        *   `src/rtdsl/partner_continuation_protocol.py` (`_grouped_topk` function):
            *   `per_group[item] = score` ensures duplicate `(group_id, item_id)` pairs keep the lowest score.
            *   `sorted(item_scores.items(), key=lambda item_score: (item_score[1], item_score[0]))` explicitly sorts by score (item_score[1]) then item_id (item_score[0]), guaranteeing determinism.
            *   `row_offsets` are explicitly calculated and `missing` group IDs are collected.
        *   `tests/goal2777_v2_5_triton_grouped_topk_preview_test.py`: `test_reference_grouped_topk_is_deterministic_and_distinct_by_item` explicitly validates the output for group IDs, item IDs, scores, ranks, row offsets, and missing group IDs, matching the expected deterministic behavior.
        *   `docs/reports/goal2777_v2_5_grouped_topk_ranked_summary_2026-05-31.md`: The "Semantics" section explicitly lists these rules: "rows are ordered by lowest score, then lowest item id", "duplicate item rows use the lowest score", "empty groups are reported explicitly".
    *   **Verdict:** accept - The reference implementation explicitly defines and tests these deterministic semantics.

3.  **Confirm the Triton preview mirrors the reference shape with score/item selection kernels and no RawKernel.**
    *   **Evidence:**
        *   `src/rtdsl/triton_partner_continuation.py`:
            *   The `run_triton_grouped_topk_f64` function calls `_triton_grouped_topk_score_f64_kernel`, `_triton_grouped_topk_item_i64_kernel`, and `_triton_grouped_topk_store_rank_kernel`. These are Triton JIT kernels that perform the score and item selection logic.
            *   The kernels use `tl.atomic_min` for selection, consistent with lowest score/item ID logic.
            *   The `_base_triton_descriptor` and `run_triton_grouped_topk_f64` explicitly set `raw_kernel_required=False`.
        *   `tests/goal2777_v2_5_triton_grouped_topk_preview_test.py`:
            *   `test_source_uses_triton_topk_kernels_and_no_rawkernel` asserts the presence of the Triton kernels and `tl.atomic_min`, and the absence of "RawKernel" in the source.
            *   `test_grouped_topk_matches_reference_when_cuda_available` validates that the Triton implementation's outputs for `group_ids`, `item_ids`, `scores`, `ranks`, `row_offsets`, and `missing_group_ids` match the reference, indicating it mirrors the reference shape.
    *   **Verdict:** accept - The Triton implementation uses dedicated JIT kernels for score and item selection, matches the reference output shape, and explicitly avoids RawKernel usage.

4.  **Confirm the support matrix is honest: reference contract exists, Triton is preview-not-promoted, Numba fails closed, CuPy is descriptor-only.**
    *   **Evidence:**
        *   `src/rtdsl/v2_5_partner_support_matrix.py` (`v2_5_partner_support_cells` function):
            *   `python_reference`: Always set to `V2_5_SUPPORT_STATUS_REFERENCE` with `notes="universal correctness reference"`.
            *   `triton`: For `grouped_topk_f64`, it falls into `V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS`, so its status is `V2_5_SUPPORT_STATUS_PREVIEW` (`preview_not_promoted`) with notes "preview kernel exists; benchmark promotion still requires pod evidence".
            *   `numba`: `grouped_topk_f64` is not in `V2_5_NUMBA_PREVIEW_OPERATIONS`, so its status is `V2_5_SUPPORT_STATUS_UNSUPPORTED` (`unsupported_fail_closed`) with notes "Numba fallback kernel is not implemented for this operation".
            *   `cupy_conformance`: `grouped_topk_f64` is not in `V2_5_CUPY_PREVIEW_OPERATIONS`, so its status is `V2_5_SUPPORT_STATUS_DESCRIPTOR` (`descriptor_only`) with notes "CuPy remains an app-chosen conformance/interoperability partner; generic v2.5 kernels are not promoted here".
        *   `docs/reports/goal2777_v2_5_grouped_topk_ranked_summary_2026-05-31.md`: The "Partner status" table directly reflects these statuses.
        *   `tests/goal2777_v2_5_triton_grouped_topk_preview_test.py`: `test_preview_kernel_set_and_support_matrix_include_grouped_topk` explicitly asserts these statuses for Triton, Numba, and CuPy.
    *   **Verdict:** accept - The support matrix accurately reflects the implementation status for each partner.

5.  **Confirm no public speedup, release, true-zero-copy, RT traversal replacement, or RTNN paper reproduction claim is introduced.**
    *   **Evidence:**
        *   `src/rtdsl/partner_continuation_protocol.py`:
            *   `V2_5_PERFORMANCE_PATH_AUTHORIZED = False`
            *   `V2_5_RT_TRAVERSAL_REPLACEMENT_ALLOWED = False`
            *   `V2_5_PREVIEW_RELEASE_TAG_AUTHORIZED = False`
            *   `V2_5_PREVIEW_PUBLIC_SPEEDUP_CLAIM_AUTHORIZED = False`
            *   `RtdlPartnerContinuationSpec` constructor raises `ValueError` if `replaces_rt_traversal`, `promoted_performance_path`, or `app_specific_semantics_allowed` are True.
        *   `src/rtdsl/triton_partner_continuation.py`:
            *   `_base_triton_descriptor` sets `raw_kernel_required=False`, `replaces_rt_traversal=False`, `promoted_performance_path=False`, and `rt_core_speedup_claim_authorized=False`.
            *   `_triton_run_result` also consistently sets these flags to `False`.
            *   `_triton_group_id_bounds_validation_metadata` sets `true_zero_copy_claim_authorized=False`.
        *   `src/rtdsl/v2_5_partner_support_matrix.py`: `V25PartnerSupportCell` constructor raises `ValueError` if `promoted_performance_path`, `rt_traversal_replacement_allowed`, `public_speedup_claim_authorized`, or `true_zero_copy_claim_authorized` are True. `V2_5_PARTNER_SUPPORT_CLAIM_BOUNDARY` explicitly states "They do not authorize RT traversal replacement, public speedup claims, release claims, or true zero-copy claims."
        *   `docs/reports/goal2777_v2_5_grouped_topk_ranked_summary_2026-05-31.md`: The "Boundary" section explicitly states: "This is not a public speedup claim, release claim, true-zero-copy claim, RTNN paper reproduction claim, or whole-app benchmark result."
        *   `tests/goal2662_v2_5_partner_continuation_contract_test.py`, `tests/goal2671_v2_5_preview_gate_test.py`, `tests/goal2676_v2_5_triton_partner_pivot_test.py`, and `tests/goal2777_v2_5_triton_grouped_topk_preview_test.py` all contain assertions validating these flags are `False`.
    *   **Verdict:** accept - The code, tests, and documentation consistently and explicitly state that no such claims are introduced.

6.  **List blockers or follow-ups before RTNN-style app adapters consume this operation.**
    *   **Blockers/Follow-ups:**
        *   **RTNN-style App Adapters:** The primary follow-up is the development and integration of RTNN-style app adapters to consume this generic operation. The `docs/reports/goal2777_v2_5_grouped_topk_ranked_summary_2026-05-31.md` states: "It is a generic v2.5 continuation primitive that closes the ranked/top-k operation-shape gap for future RTNN-style app adapters."
        *   **Triton Performance Validation/Promotion:** Before Triton kernels can be "promoted" for performance claims, further validation is required. `src/rtdsl/v2_5_partner_support_matrix.py` notes for Triton's `preview_not_promoted` status: "benchmark promotion still requires pod evidence". The `docs/reports/goal2777_v2_5_grouped_topk_ranked_summary_2026-05-31.md` mentions "Pod validation is required before any performance wording."
        *   **Benchmark Integration:** `tests/goal2671_v2_5_preview_gate_test.py` indicates `benchmark_integration_validated` is `False` and lists "benchmark integration" as part of `remaining_validation_scope`.
        *   **Full RT Hit-Stream Handoff & External 3-AI Consensus:** `tests/goal2671_v2_5_preview_gate_test.py` also lists "full RT hit-stream handoff" and "external 3-AI consensus" as part of `remaining_validation_scope`.
        *   **Optimized Performance Path:** `tests/goal2671_v2_5_preview_gate_test.py` lists "optimized performance path" as part of `remaining_validation_scope`.

## Overall Verdict: accept-with-boundary

The `grouped_topk_f64` operation has been robustly implemented and reviewed. It adheres to the established v2.5 partner continuation contract, maintains genericity, and explicitly avoids making any unauthorized claims (speedup, release, zero-copy, RT traversal replacement). The reference semantics are deterministic, and the Triton preview accurately mirrors these semantics without using RawKernel. The support matrix honestly reflects the status of the operation across different partners.

The identified blockers/follow-ups are primarily external to the core `grouped_topk_f64` operation itself, focusing on future integration (RTNN-style app adapters), performance validation (pod evidence, benchmark integration), and broader consensus. These are clearly documented and aligned with the preview status of the Triton implementation. No immediate issues were found that would prevent its integration for current purposes.
