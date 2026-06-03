# Handoff: Gemini Review For Goal3123 v2.8 Partner-Consumer Named Output Hardening

Please review Goal3123 and write the review to:

`docs/reviews/goal3124_gemini_review_goal3123_partner_consumer_named_output_hardening_2026-06-03.md`

## Scope

Goal3123 hardens the explicit v2.8 partner-consumer front door so actual
partner execution returns named output columns matching the Goal3114 Python
reference consumer for scalar reductions:

- `segmented_count_i64` -> `{"counts": ...}`
- `segmented_sum_f64` -> `{"sums": ...}`
- `grouped_vector_sum_f64x2` was already named as `{"sum_x": ..., "sum_y": ...}`

It also records a local Linux CuPy sweep for the three CuPy-supported operations
above.

## Files To Inspect

- `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`
- `tests/goal3111_v2_8_segmented_typed_stream_adapter_test.py`
- `docs/reports/goal3123_v2_8_partner_consumer_named_output_hardening_2026-06-03.md`
- `docs/reports/goal3122_v2_8_cupy_partner_consumer_local_linux_smoke_2ai_consensus_2026-06-03.md`

## Review Questions

1. Is the output-schema hardening correct and narrowly scoped?
2. Do actual partner outputs and reference outputs now use the same named column
   shape for `segmented_count_i64`, `segmented_sum_f64`, and
   `grouped_vector_sum_f64x2`?
3. Are the local Linux CuPy smoke results honestly bounded as functional smoke,
   not performance/release evidence?
4. Is the next-step boundary correct for grouped argmin/argmax/top-k and
   bounded collect?

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. Include findings by severity, claim boundary, files inspected, and
next step.
