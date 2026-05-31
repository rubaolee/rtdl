# Gemini Review for Goal2780 Top-K Adapter over Triton Grouped Top-K

Date: 2026-05-31

## Review of Goal2780 Top-K Adapter over Triton Grouped Top-K

This review confirms the implementation and claims for Goal2780 based on the provided files:
- `src/rtdsl/partner_adapters.py`
- `tests/goal2780_topk_adapter_triton_grouped_topk_test.py`
- `docs/reports/goal2780_topk_adapter_triton_grouped_topk_2026-05-31.md`
- `docs/reports/goal2780_pod_artifacts/goal2780_topk_adapter_triton_pod_69_30_85_171_2026-05-31.json`

### Questions Answered:

1.  **Confirm that `top_k_nearest_points_2d_partner_columns(..., partner="triton")` routes through the generic `grouped_topk_f64` continuation rather than adding app-specific native engine logic.**
    *   **Confirmation:** Confirmed. The `src/rtdsl/partner_adapters.py` code for `top_k_nearest_points_2d_partner_columns` with `partner="triton"` explicitly calls `run_triton_partner_continuation("grouped_topk_f64", ...)`. The report `docs/reports/goal2780_topk_adapter_triton_grouped_topk_2026-05-31.md` also clearly states this in its "Purpose" and "What Changed" sections. The test `test_adapter_source_routes_triton_through_generic_grouped_topk` further verifies this routing. The `_metadata` dictionary for the `top_k_nearest_points_2d_partner_columns` also includes `"v2_5_partner_continuation_operation": "grouped_topk_f64"` and `"native_engine_row_contract": "not_called_partner_reference_only"`.

2.  **Confirm same-contract correctness against the Torch branch, including the deterministic distance-then-candidate-id tie break.**
    *   **Confirmation:** Confirmed. The test `test_triton_topk_adapter_matches_same_contract_torch_reference_when_cuda_available` in `tests/goal2780_topk_adapter_triton_grouped_topk_test.py` explicitly compares the output of Triton and Torch implementations for query IDs, neighbor IDs, neighbor ranks, and distances, asserting their equality. The metadata for the Triton result also explicitly states `"tie_break": "distance_then_candidate_id"`. The report's "Boundary" section explicitly confirms same-contract correctness and deterministic tie-breaking.

3.  **Confirm the CUDA `uint32` indexing repair is appropriate and does not change app semantics.**
    *   **Confirmation:** Confirmed. The `docs/reports/goal2780_topk_adapter_triton_grouped_topk_2026-05-31.md` in the "What Changed" section details that "CUDA Torch cannot advanced-index `uint32` tensors, so query and candidate ids are normalized to `int64` for the ranked output path." The passing of the `test_triton_topk_adapter_matches_same_contract_torch_reference_when_cuda_available` test, which compares results against the Torch implementation, indicates that this change does not alter app semantics.

4.  **Confirm the report is honest that Triton is much slower than Torch for this dense exact top-k adapter and therefore is not promoted as a performance path.**
    *   **Confirmation:** Confirmed. The `docs/reports/goal2780_topk_adapter_triton_grouped_topk_2026-05-31.md` report explicitly states in its "Boundary" section that "the current Triton grouped-top-k algorithm is much slower than the Torch same-contract branch". The "Pod Evidence" table in the report, backed by `docs/reports/goal2780_pod_artifacts/goal2780_topk_adapter_triton_pod_69_30_85_171_2026-05-31.json`, shows Triton being 47.28x to 150.90x slower than Torch. The "Decision" section also explicitly states, "It does not promote `grouped_topk_f64` as the RTNN performance path."

5.  **Confirm no public speedup, RT-core speedup, true-zero-copy, release, or whole-app claim is authorized.**
    *   **Confirmation:** Confirmed. The `_metadata` dictionaries within `src/rtdsl/partner_adapters.py` for `top_k_nearest_points_2d_partner_columns` explicitly set `direct_device_handoff_authorized: False`, `rt_core_speedup_claim_authorized: False`, `v2_0_release_authorized: False`, and `whole_app_speedup_claim_authorized: False`. The report `docs/reports/goal2780_topk_adapter_triton_grouped_topk_2026-05-31.md` also explicitly states in its "Boundary" that it is "not an RT-core speedup claim and not a public performance promotion". The pod artifact JSON further corroborates this by setting `public_speedup_claim_authorized: false`, `rt_core_speedup_claim_authorized: false`, `v2_5_release_authorized: false`, and `triton_preview_not_promoted: true`.

### Verdict:

`accept-with-boundary`

The work in Goal2780 successfully integrates the Triton grouped top-k adapter via the generic `grouped_topk_f64` continuation, ensuring correct behavior and proper tie-breaking logic consistent with the Torch branch. The necessary CUDA `uint32` indexing repair has been applied without altering app semantics. Critically, the report honestly reflects the current performance limitations of the Triton implementation compared to Torch, explicitly stating that it is not a performance path and that no speedup, zero-copy, or whole-app claims are authorized. The metadata and report clearly define the boundaries of this preview.
