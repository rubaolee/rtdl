# Review for Goal2081: Streaming Witness Page Adapter

**Date:** 2026-05-15
**Reviewer:** Gemini

**1. Does the new adapter solve the right design problem for the slow `segment_polygon_anyhit_rows` row: avoiding full Python witness-row materialization?**

Yes. The `docs/reports/goal2081_streaming_witness_page_adapter_2026-05-15.md` explicitly states the problem: "v2.0 was slower when it materialized full Python witness-row dictionaries." The new adapter's design aims to avoid this, and this is confirmed by the `tests/goal2081_streaming_witness_page_adapter_test.py` which asserts that `metadata["full_python_row_table_materialization_avoided"]` is `True`.

**2. Does it preserve the app-agnostic native-engine boundary by keeping the native contract as generic ray/primitive candidate witness pairs?**

Yes. The report clearly states, "The native engine still emits generic ray/primitive candidate witness pairs. This does not add app logic to the native engine." The test file also contains assertions to confirm that "generic ray/primitive candidate witness pairs" and "does not add app logic to the native engine" are present in the relevant source code and documentation, upholding the app-agnostic boundary.

**3. Is the app-layer exact filtering and paging contract clear and bounded?**

Yes. The design described in the report indicates that the new adapter "Exact-filters candidate pairs in the partner layer" and "Returns a bounded page of partner-owned columns." The `partner_page_columns` function in `src/rtdsl/partner_adapters.py` demonstrates a clear implementation of paging using `offset` and `limit` parameters. The `segment_polygon_exact_witness_pair_page_optix_prepared_partner_columns` function also supports `page_offset` and `page_limit`, and the test validates `metadata["page_row_count"]`.

**4. Are the claim boundaries honest, especially that pod timing is still required before updating performance tables?**

Yes, the claim boundaries are honest and clearly articulated. The report states, "This is a structural fix for the full-witness output shape, not a release claim. Pod timing is still required before updating the OptiX/RT performance table or making any speedup wording." Furthermore, the `scripts/goal2081_streaming_witness_page_perf.py` output payload includes `v2_0_release_authorized: false`, `whole_app_speedup_claim_authorized: false`, and `requires_pod_review_before_table_update: True`, reinforcing these boundaries.

**5. Flag any API, correctness, or wording risk.**

*   **API Risk:** No significant API risks were identified. The `_partner_module` function correctly checks for CUDA availability before proceeding, preventing issues in unsupported environments.
*   **Correctness Risk:** The `_require_uint32_id` function enforces `uint32` compatibility for IDs, which is crucial for the OptiX contract and helps prevent potential data integrity issues.
*   **Wording Risk:** The documentation, code comments, and test descriptions are consistent and clear in their explanation of the new adapter's purpose, functionality, and limitations. The explicit metadata flags within the adapter outputs further reduce potential misinterpretations of claims.

**Verdict:** `accept-with-boundary`

The new streaming witness page adapter effectively solves the problem of full Python witness-row materialization, adhering to the established native-engine boundary and providing a clear, bounded app-layer contract. The project demonstrates a strong commitment to honest claim boundaries, explicitly deferring performance table updates until further pod timing reviews are complete.
