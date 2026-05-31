# Handoff: Gemini Review For Goal2771

Please perform an independent Gemini review of Goal2771 and write the review to:

`docs/reviews/goal2771_gemini_review_hit_stream_event_ordered_grouped_reduction_2026-05-31.md`

## Files To Inspect

- `src/rtdsl/optix_runtime.py`
- `tests/goal2771_hit_stream_event_ordered_grouped_reduction_consumer_test.py`
- `docs/reports/goal2771_hit_stream_event_ordered_grouped_reduction_consumer_2026-05-31.md`
- Prior context:
  - `tests/goal2770_hit_stream_event_ordered_row_reduction_consumer_test.py`
  - `docs/reports/goal2770_hit_stream_event_ordered_row_reduction_consumer_consensus_2026-05-31.md`

## Review Questions

1. Does Goal2771 preserve the engine/app boundary by grouping on the generic
   hit-stream `ray_id` column rather than introducing app/domain vocabulary?
2. Does the CuPy grouped-reduction helper insert `streamWaitEvent` before the
   grouped kernel launch, and does it avoid host materialization of hit rows or
   grouped output columns before the consumer runs?
3. Does the public method keep the producer event/stream lifetime and async
   launch owner lifetime honest until the consumer completes?
4. Are the metadata/report boundaries honest:
   `cuda_event_cross_stream`, `cuda_event_wait_inserted_before_consumer = True`,
   `grouped_output_columns_written_on_device = True`,
   `bounded_event_ordered_grouped_ray_id_reduction_consumer_only`,
   `query_rays_still_packed_on_host = True`, and no true-zero-copy or public
   speedup claim?
5. Are the tests sufficient for this narrow goal, including the pod smoke
   result with grouped output columns `[2, 0, 2]`, `[1, 0, 1]`, `[1, 0, 1]`?

## Expected Verdict

Use one of the existing verdict labels:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

This goal is a bounded v2.5 primitive/runtime step, not a release gate and not
a public performance claim.
