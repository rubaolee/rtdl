# Handoff: Goal2821 RTNN Heterogeneous Batched Aggregate Review

Please independently review Goal2821 as a distinct external AI reviewer.

## Context

Goal2821 extends the RTNN v2.5 prepared-query aggregate batch path so the
benchmark runner can send heterogeneous aggregate requests over the same
resident prepared search/query handles. Goal2819 had already added the native
batch ABI, but only measured repeated identical requests. Goal2821 adds runner
support for explicit per-request radius multipliers and `k_max` values, then
records pod evidence for a four-request radius/K sweep.

## Files To Inspect

- `scripts/goal2348_rtnn_v2_2_external_runner.py`
- `tests/goal2821_rtnn_heterogeneous_batched_aggregate_requests_test.py`
- `docs/reports/goal2821_rtnn_heterogeneous_batched_aggregate_requests_2026-05-31.md`
- `docs/reports/goal2821_rtnn_heterogeneous_batched_aggregate_requests_pod/goal2821_summary.json`
- `docs/reports/goal2821_rtnn_heterogeneous_batched_aggregate_requests_pod/rtnn_heterogeneous_batch_uniform_32768.json`
- `docs/reports/goal2821_rtnn_heterogeneous_batched_aggregate_requests_pod/rtnn_heterogeneous_batch_uniform_65536.json`

## Facts To Verify

- The added CLI options are generic and app-agnostic:
  `--aggregate-radius-multipliers` and `--aggregate-k-values`.
- The runner rejects malformed/mismatched request lists.
- The prepared OptiX handle uses the maximum requested radius for a sweep.
- The batch request list is passed to
  `aggregate_ranked_summary_prepared_queries_batch(...)` rather than silently
  repeating one request.
- Pod evidence is from commit
  `17302d0f02bc0630cd7f4993309727d1bd47ebb7` with `source_dirty: []`.
- Batch results exactly match the equivalent four sequential single aggregate
  calls for both 32K and 65K rows.
- The measured internal amortization improvements are about 1.16x at 32K and
  2.50x at 65K versus four sequential single aggregate calls over the same
  prepared handles.
- All public/release/paper/single-request speedup claim flags remain closed.

## Review Questions

1. Is Goal2821 a valid generic v2.5 runtime hardening step rather than an
   RTNN-specific shortcut?
2. Is the pod comparison fair for the narrow claim it makes: one heterogeneous
   four-request batch versus four sequential single aggregate calls over the
   same prepared data?
3. Are the correctness checks and artifact metadata sufficient for
   `accept-with-boundary`?
4. Are there any overclaims in the report wording?
5. What should the next v2.5 optimization target be after this result?

## Required Output

Write the review to:

`docs/reviews/goal2821_gemini_review_rtnn_heterogeneous_batched_aggregate_2026-05-31.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.
