# Handoff: Gemini Review For Goal2819 Batched Prepared Aggregate

Please perform a read-only independent review of Goal2819.

## Files To Inspect

- `docs/reports/goal2819_rtnn_batched_prepared_aggregate_contract_2026-05-31.md`
- `tests/goal2819_rtnn_batched_prepared_aggregate_contract_test.py`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `scripts/goal2348_rtnn_v2_2_external_runner.py`
- `docs/reports/goal2819_rtnn_batched_prepared_aggregate_contract_pod/goal2819_summary.json`
- `docs/reports/goal2819_rtnn_batched_prepared_aggregate_contract_pod/rtnn_batched_prepared_aggregate_uniform_32768_req4.json`
- `docs/reports/goal2819_rtnn_batched_prepared_aggregate_contract_pod/rtnn_batched_prepared_aggregate_uniform_65536_req4.json`

## Review Questions

1. Confirm whether the native/API/runtime changes are generic and app-agnostic: fixed-radius prepared-query ranked-summary aggregate batching, not an RTNN-native ABI or benchmark-specific engine branch.
2. Confirm whether the implementation uses the current block-partial path for small rows and records the correct phase label `prepared_query_uniform_cell_ranked_summary_aggregate_f32_batch_block_partials`.
3. Confirm whether the pod artifacts are clean and valid: source commit `0cb57ed07e396dff487acb9c5aefe346af36fc35`, empty `source_dirty`, RTX A5000, status pass, first batch result equals the single prepared-query result, and 4 aggregate requests are recorded.
4. Confirm whether the timing interpretation is accurate and bounded: 32K uniform improves from `0.000070732` single to `0.000047873` amortized per request (1.477x), and 65K uniform improves from `0.000127490` to `0.000094803` amortized per request (1.345x).
5. Confirm whether the report correctly says this is amortized batch evidence, not a single-request speedup claim, not a public RTDL-beats-CuPy claim, not an RTDL-beats-RTNN-paper claim, and not a v2.5 release claim.
6. Call out any stale wording, overclaim, test/artifact mismatch, correctness risk, determinism/concurrency risk, or app-agnosticity risk.

## Output

Write the review to:

`docs/reviews/goal2819_gemini_review_rtnn_batched_prepared_aggregate_2026-05-31.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`, `reject`, or `needs-more-evidence`.
