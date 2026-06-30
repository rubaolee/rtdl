# Goal3124: Gemini Review For Goal3123 v2.8 Partner-Consumer Named Output Hardening

## Verdict
accept

## Findings By Severity

### High
None.

### Medium
None.

### Low
None.

## Claim Boundary
This review is based on local functional smoke tests and unit tests. No release, public speedup, broad RT-core, true-zero-copy, hidden dispatch, automatic partner selection, app-specific native-engine behavior, user-defined shader injection, or benchmark-app performance claims are made. The scope is limited to hardening the output schema for specific partner-consumer front door operations.

## Files/Evidence Considered
- Goal3123 hardening description
- Code change descriptions for `segmented_count_i64`, `segmented_sum_f64`, and `grouped_vector_sum_f64x2`
- Windows unit test details for `partner_group_count_by_key` and `partner_group_sum_by_key`
- Windows validation results (py_compile, focused tests)
- Local Linux smoke test results (GTX 1070, CuPy 14.0.1)
- Local Linux actual vs reference outputs
- Claim flags status
- Explicitly stated boundaries
- Next-step boundary for remaining partner-front-door operations

## Review Question Answers

1.  **Is the output-schema hardening correct and narrowly scoped?**
    Yes, the output-schema hardening is correct and narrowly scoped. The changes specifically address `segmented_count_i64` and `segmented_sum_f64` to return named outputs (`{"counts": ...}` and `{"sums": ...}` respectively), aligning with the existing `grouped_vector_sum_f64x2` which already uses named outputs and remains unchanged. This directly fulfills the goal of hardening the v2.8 explicit partner-consumer front door.

2.  **Do actual partner outputs and reference outputs now use the same named column shape for segmented_count_i64, segmented_sum_f64, and grouped_vector_sum_f64x2?**
    Yes. The evidence states that `segmented_count_i64` and `segmented_sum_f64` now return their results wrapped in named dictionaries (`{"counts": <partner array>}` and `{"sums": <partner array>}`), and `grouped_vector_sum_f64x2` already conformed. The Windows unit tests explicitly mock relevant functions to "enforce named outputs," confirming the consistent structure.

3.  **Are local Linux CuPy smoke results honestly bounded as functional smoke, not performance/release evidence?**
    Yes, the local Linux CuPy smoke results are honestly bounded. The "Boundaries" section explicitly states that the validation is "local functional smoke only" and negates any claims related to release, public speedup, or specific hardware/performance metrics.

4.  **Is the next-step boundary correct for grouped argmin/argmax/top-k and bounded collect?**
    Yes, the next-step boundary is correctly identified. The review explicitly notes that `grouped_argmin_f64`, `grouped_argmax_f64`, `grouped_topk_f64`, and `bounded_collect_finalize_i64` "still require a suitable host or pod with the selected partner stack installed," clearly defining the work remaining for these operations.

## Next Step
None explicitly required by this review. The identified next-step boundary for other operations implies future work, but this Goal3123 itself is complete and accepted.
