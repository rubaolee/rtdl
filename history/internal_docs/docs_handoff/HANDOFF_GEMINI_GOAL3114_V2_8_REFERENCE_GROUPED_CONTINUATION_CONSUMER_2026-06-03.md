# Handoff: Gemini Review For Goal3114 v2.8 Reference Grouped-Continuation Consumer

Please perform an independent static review and write your review to:

`docs/reviews/goal3115_gemini_review_goal3114_reference_grouped_continuation_consumer_2026-06-03.md`

## Scope

Goal3114 extends the Goal3111 segmented typed-stream adapter with:

`execute_segmented_typed_stream_reference_continuation`

This function reconstructs segmented rows, maps the adapter's
`V28GroupedContinuationPlan` to existing v2.5 Python reference continuation
inputs, calls `execute_v2_5_partner_continuation_reference`, and returns
reference outputs with non-authorizing flags preserved.

Codex validation:

```powershell
py -3 -m py_compile src\rtdsl\v2_8_segmented_typed_stream_adapter.py src\rtdsl\v2_8_typed_result_stream.py src\rtdsl\__init__.py
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3111_v2_8_segmented_typed_stream_adapter_test tests.goal3108_v2_8_typed_result_stream_contract_test tests.goal3105_v2_8_benchmark_runtime_gap_map_test
```

Observed result: py_compile passed; 22 focused tests OK.

## Files To Inspect

- `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`
- `src/rtdsl/v2_8_typed_result_stream.py`
- `src/rtdsl/partner_continuation_protocol.py`
- `src/rtdsl/__init__.py`
- `tests/goal3111_v2_8_segmented_typed_stream_adapter_test.py`
- `docs/reports/goal3114_v2_8_reference_grouped_continuation_consumer_2026-06-03.md`

## Questions

1. Does Goal3114 correctly reuse the existing v2.5 Python reference
   continuation executor instead of inventing a second reduction oracle?
2. Does the adapter-to-reference mapping correctly cover grouped argmax,
   segmented sum, top-k `k` handling, and the other listed operations at the
   contract level?
3. Does it preserve all claim boundaries: no native producer promotion, no
   partner consumer promotion, no device-residency proof, no true-zero-copy
   claim, no release/speedup/RT-core claim, no hidden dispatch, no hidden
   partner selection, no app-specific native engine behavior, and no
   user-defined shader injection?
4. What is the next v2.8 engineering step?

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. Include findings by severity, claim boundary, files inspected, and
next step.
