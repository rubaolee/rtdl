# Gemini Review - Goal3165/3166 RTNN Ranked-Summary Front Door

Date: 2026-06-03

## Review Scope

This review is based on the handoff document `docs/handoff/HANDOFF_EXTERNAL_REVIEW_GOAL3165_3166_RTNN_RANKED_SUMMARY_FRONT_DOOR_2026-06-03.md` and focuses on the work related to Goal3165/3166, specifically the RTNN Ranked-Summary Front Door.

## Files Inspected

- `docs/reports/goal3165_rtnn_ranked_summary_typed_stream_front_door_2026-06-03.md`
- `docs/reports/goal3166_v2_8_runtime_gap_rtnn_ranked_summary_refresh_2026-06-03.md`
- `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`
- `src/rtdsl/v2_8_benchmark_runtime_gap.py`
- `src/rtdsl/__init__.py`
- `examples/v2_0/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py`
- `tests/goal3165_rtnn_ranked_summary_typed_stream_front_door_test.py`
- `tests/goal3166_v2_8_runtime_gap_rtnn_ranked_summary_refresh_test.py`

## Review Questions Addressed

1. Does `execute_ranked_summary_typed_stream_partner_columns(...)` stay generic
   and app-agnostic, with RTNN vocabulary confined to the benchmark wrapper and
   reports?
2. Does the helper correctly publish a `ranked_summary_stream` typed result
   stream and grouped continuation plan over caller-supplied columns without
   hidden host row materialization?
3. Are the partner boundaries precise, especially `torch`/`triton` for top-k,
   `numba` for argmin/argmax, and no automatic partner selection?
4. Does the RTNN app wrapper preserve the existing benchmark front door while
   adding a useful v2.8 descriptor/preview?
5. Does Goal3166 honestly update the v2.8 runtime-gap matrix without claiming
   prepared packed-column residency, native typed producer evidence, RT-core
   speedups, zero-copy, release readiness, or RTNN paper reproduction?
6. Do the tests and pod evidence support only the claimed scope?

## Findings

1.  **Does `execute_ranked_summary_typed_stream_partner_columns(...)` stay generic and app-agnostic, with RTNN vocabulary confined to the benchmark wrapper and reports?**
    *   **Finding:** Yes. The `execute_ranked_summary_typed_stream_partner_columns` function (in `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`) uses generic terms for its inputs (`group_ids`, `item_ids`, `scores`) and operations (`grouped_argmin_f64`, `grouped_argmax_f64`, `grouped_topk_f64`). RTNN-specific vocabulary is indeed confined to the `examples/v2_0/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py` wrapper and the `docs/reports/goal3165_rtnn_ranked_summary_typed_stream_front_door_2026-06-03.md` and `docs/reports/goal3166_v2_8_runtime_gap_rtnn_ranked_summary_refresh_2026-06-03.md` reports. The `Goal3165` report explicitly states: "RTNN vocabulary appears only in the benchmark app wrapper and this report."

2.  **Does the helper correctly publish a `ranked_summary_stream` typed result stream and grouped continuation plan over caller-supplied columns without hidden host row materialization?**
    *   **Finding:** Yes. The `execute_ranked_summary_typed_stream_partner_columns` helper returns a dictionary that includes a `typed_stream` with `stream_kind: "ranked_summary_stream"` and a `continuation_plan`. The `source_materialization` field in the response (and in the code) is set to `caller_supplied_partner_columns_no_hidden_host_rows`, confirming that no hidden host row materialization is performed. This is validated by `test_generic_ranked_summary_front_door_is_exported_and_non_authorizing` in `tests/goal3165_rtnn_ranked_summary_typed_stream_front_door_test.py`.

3.  **Are the partner boundaries precise, especially `torch`/`triton` for top-k, `numba` for argmin/argmax, and no automatic partner selection?**
    *   **Finding:** Yes. The `execute_ranked_summary_typed_stream_partner_columns` function strictly requires an explicit `partner` and raises a `ValueError` if `partner` is `""`, `"auto"`, or `"explicit_user_choice_required"`. The `Goal3165` report and the `describe_rtnn_v2_8_ranked_summary_typed_stream` function in `rtdl_rtnn_benchmark_app.py` clearly define that `torch`/`triton` are supported for `grouped_topk_f64`, while `numba` supports `grouped_argmin_f64`/`grouped_argmax_f64`. Numba's `top-k` support is explicitly noted as "not_promoted_in_current_partner_adapter".

4.  **Does the RTNN app wrapper preserve the existing benchmark front door while adding a useful v2.8 descriptor/preview?**
    *   **Finding:** Yes. The `rtdl_rtnn_benchmark_app.py` includes `describe_rtnn_v2_8_ranked_summary_typed_stream` and `run_rtnn_v2_8_ranked_summary_typed_stream_preview`. These functions successfully integrate the new v2.8 descriptor and preview functionality using the generic front door. The test `test_rtnn_descriptor_uses_generic_ranked_summary_front_door` confirms this integration. The `rtnn_command_plan_payload` in the benchmark app also indicates that existing benchmark functionalities are preserved.

5.  **Does Goal3166 honestly update the v2.8 runtime-gap matrix without claiming prepared packed-column residency, native typed producer evidence, RT-core speedups, zero-copy, release readiness, or RTNN paper reproduction?**
    *   **Finding:** Yes. The `Goal3166` report and the `rtnn` entry within the `V2_8_BENCHMARK_RUNTIME_GAP_ROWS` in `src/rtdsl/v2_8_benchmark_runtime_gap.py` (and its validation in `tests/goal3166_v2_8_runtime_gap_rtnn_ranked_summary_refresh_test.py`) accurately describe the current state. The bottleneck is identified as "prepared packed-column residency, native typed producer evidence, and replay/chunking at serious scale remain unresolved." All authorization flags, such as `release_authorized`, `public_speedup_claim_authorized`, `rt_core_speedup_claim_authorized`, and `true_zero_copy_claim_authorized`, are explicitly set to `False` in both the code and documentation, and the reports clearly state that full RTNN paper reproduction is not claimed.

6.  **Do the tests and pod evidence support only the claimed scope?**
    *   **Finding:** Yes. Both `docs/reports/goal3165_rtnn_ranked_summary_typed_stream_front_door_2026-06-03.md` and `docs/reports/goal3166_v2_8_runtime_gap_rtnn_ranked_summary_refresh_2026-06-03.md` provide detailed local and pod validation steps, including compile checks, focused regression tests, and CLI descriptor checks. The test results confirm that the implemented functionality works as expected within the defined boundaries and that unauthorized claims (e.g., release, speedup, zero-copy) are correctly blocked. The tests in `tests/goal3165_rtnn_ranked_summary_typed_stream_front_door_test.py` and `tests/goal3166_v2_8_runtime_gap_rtnn_ranked_summary_refresh_test.py` specifically assert these boundaries.

## Verdict

`accept-with-boundary`

## Residual Boundaries

*   **Prepared packed-column residency:** The current implementation processes caller-supplied columns. The goal of achieving device-resident, packed-column inputs to remove data transfer overhead is a recognized future development.
*   **Native typed producer evidence:** There is no native producer that directly generates the ranked summary typed stream, implying that explicit data preparation and marshalling are still required by the caller.
*   **Replay/chunking at serious scale:** The current front-door does not yet address the complexities of managing replay or chunking for the ranked summary stream at large scales, which is critical for performance-sensitive applications.
*   **Full RTNN paper reproduction:** This work provides a generic ranked-summary typed-stream front door and does not claim to fully reproduce the entire RTNN paper system, which involves a broader scope of features and optimizations.
*   **Release readiness:** The feature is not yet authorized for release and is considered an internal development lane.
*   **Public speedup claims:** No public speedup claims are authorized, maintaining a cautious approach to performance marketing.
*   **RT-core speedup claims:** No specific RT-core speedup claims are authorized, ensuring that performance benefits are not prematurely attributed solely to RT cores.
*   **True zero-copy:** The implementation does not claim to achieve true zero-copy, indicating that data copying may still occur.
*   **Automatic partner selection:** The design explicitly requires an explicit partner selection, and automatic partner selection is not supported, emphasizing user control.
*   **Numba top-k:** Numba's `top-k` capability is not yet promoted within the current partner adapter and remains a future extension.