# Handoff: Gemini Review For Goal2770 Event-Ordered Hit-Stream Row Reduction

Please perform an independent review of Goal2770 and write the review to:

`docs/reviews/goal2770_gemini_review_hit_stream_event_ordered_row_reduction_2026-05-31.md`

## Context

Goal2769 added a same-stream CuPy row-reduction consumer over all stored generic
hit rows. Goal2770 proves the next ordering model: an OptiX producer runs on a
Torch CUDA producer stream, records a CUDA event, and a separate CuPy consumer
stream waits on that event before running the row-reduction kernel.

This goal does not claim true zero-copy, public speedup, arbitrary partner
continuation, or release readiness.

## Files To Inspect

- `src/rtdsl/optix_runtime.py`
- `tests/goal2770_hit_stream_event_ordered_row_reduction_consumer_test.py`
- `docs/reports/goal2770_hit_stream_event_ordered_row_reduction_consumer_2026-05-31.md`
- Context:
  - `tests/goal2769_hit_stream_same_stream_row_reduction_consumer_test.py`
  - `docs/reports/goal2769_hit_stream_same_stream_row_reduction_consumer_consensus_2026-05-31.md`

## Required Review Questions

1. Does Goal2770 actually record a Torch CUDA event after producer enqueue and
   make a separate CuPy stream wait on that event before launching the
   row-reduction kernel?
2. Does the Python method preserve the async native owner, producer stream,
   and producer event lifetimes until after the consumer finishes?
3. Are metadata/report boundaries honest:
   `producer_consumer_stream_ordering = cuda_event_cross_stream`,
   `cuda_event_cross_stream_ordering_proven = True`,
   `cuda_event_wait_inserted_before_consumer = True`,
   `bounded_event_ordered_row_reduction_consumer_only`,
   `query_rays_still_packed_on_host = True`, and no true-zero-copy or public
   speedup claim?
4. Do the tests cover the exact contract without turning this into a broad
   partner-continuation or release claim?
5. Is there any hidden host sync or app-specific engine logic introduced by
   this patch?

## Validation Evidence To Check

Local Windows:

- `tests.goal2770_hit_stream_event_ordered_row_reduction_consumer_test`
  `tests.goal2769_hit_stream_same_stream_row_reduction_consumer_test`
  `tests.goal2768_hit_stream_same_stream_row_window_consumer_test`
  `tests.goal2767_hit_stream_async_input_upload_test`
  `tests.goal2764_hit_stream_same_stream_status_consumer_test`: 29 tests OK,
  6 live CUDA tests skipped.
- Python compile check for `src/rtdsl/optix_runtime.py` and
  `tests/goal2770_hit_stream_event_ordered_row_reduction_consumer_test.py`: OK.

Pod:

- SSH target used: `root@69.30.85.171 -p 22167`.
- Pod base commit: `9f7611d85f4b65385c13b626d7191c5a23d7c8fd`.
- Method: reset to latest `origin/main`, apply Goal2770 patch only, rebuild
  OptiX with `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`, run with
  `PYTHONPATH=src:.` and
  `RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so`.
- Focused live tests: 29 OK.
- Hit-stream regression slice: 46 OK.

## Expected Output Format

Use one of these verdicts exactly: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

Please include:

- verdict;
- short technical reasoning;
- answers to the required review questions;
- blocking issues, if any;
- non-blocking follow-up debt;
- explicit statement that this is independent Gemini review and not Codex
  self-review.
