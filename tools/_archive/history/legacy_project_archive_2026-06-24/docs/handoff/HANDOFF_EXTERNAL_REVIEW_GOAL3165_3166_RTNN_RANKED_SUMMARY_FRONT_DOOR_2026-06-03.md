# Handoff - External Review of Goal3165/3166 RTNN Ranked-Summary Front Door

Date: 2026-06-03

Please perform an independent review of the Goal3165/3166 work.

## Files To Read

- `docs/reports/goal3165_rtnn_ranked_summary_typed_stream_front_door_2026-06-03.md`
- `docs/reports/goal3166_v2_8_runtime_gap_rtnn_ranked_summary_refresh_2026-06-03.md`
- `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`
- `src/rtdsl/v2_8_benchmark_runtime_gap.py`
- `src/rtdsl/__init__.py`
- `examples/v2_0/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py`
- `tests/goal3165_rtnn_ranked_summary_typed_stream_front_door_test.py`
- `tests/goal3166_v2_8_runtime_gap_rtnn_ranked_summary_refresh_test.py`

## Review Questions

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

## Expected Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Lead with findings by severity. If accepted, state the residual boundaries
clearly.

## Output Paths

Claude should write:

`docs/reviews/goal3167_claude_review_goal3165_3166_rtnn_ranked_summary_front_door_2026-06-03.md`

Gemini should write:

`docs/reviews/goal3168_gemini_review_goal3165_3166_rtnn_ranked_summary_front_door_2026-06-03.md`
