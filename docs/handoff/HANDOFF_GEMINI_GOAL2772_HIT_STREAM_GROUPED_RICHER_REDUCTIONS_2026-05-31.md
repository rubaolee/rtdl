# Handoff: Gemini Review For Goal2772

Please perform an independent Gemini review of Goal2772 and write the review to:

`docs/reviews/goal2772_gemini_review_hit_stream_event_ordered_grouped_richer_reductions_2026-05-31.md`

## Files To Inspect

- `src/rtdsl/optix_runtime.py`
- `tests/goal2772_hit_stream_event_ordered_grouped_richer_reductions_test.py`
- `docs/reports/goal2772_hit_stream_event_ordered_grouped_richer_reductions_2026-05-31.md`
- Prior context:
  - `tests/goal2771_hit_stream_event_ordered_grouped_reduction_consumer_test.py`
  - `docs/reports/goal2771_hit_stream_event_ordered_grouped_reduction_consumer_consensus_2026-05-31.md`

## Review Questions

1. Does Goal2772 keep the generic engine/app boundary intact by reducing only
   generic hit-stream columns grouped by `ray_id`?
2. Does the richer grouped kernel correctly add min/max and first/last
   row-order outputs without introducing app-specific semantics?
3. Does the helper still wait on the producer CUDA event before the CuPy kernel
   launch, and does it avoid host materialization of hit rows or grouped output
   columns before the consumer completes?
4. Does the first/last row-order contract honestly reflect the observed hit
   stream order rather than implying sorted-by-ray ordering?
5. Are the metadata/report boundaries honest: no true-zero-copy, no public
   speedup, no arbitrary continuation, no unbounded stream, and query rays still
   packed on host?
6. Are the tests and pod evidence sufficient for this narrow runtime primitive,
   including the fixed `group_last_hit_row_index` initializer bug?

## Expected Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

This is a bounded v2.5 primitive/runtime step, not a release gate and not a
public performance claim.
