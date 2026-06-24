# Handoff: Gemini Review For Goal2769 Hit-Stream Row-Reduction Consumer

Please perform an independent review of Goal2769 and write the review to:

`docs/reviews/goal2769_gemini_review_hit_stream_row_reduction_consumer_2026-05-31.md`

## Context

Goal2764 proved same-stream OptiX hit-stream status consumption. Goal2767 moved
the same-stream producer's input upload to stream-ordered pinned-host async
copies. Goal2768 added a bounded same-stream row-window consumer.

Goal2769 is the next larger device-resident operation: a CuPy same-stream
consumer reduces all stored hit rows in the caller-owned device output buffers
before host scalar or row materialization.

This goal does not claim true zero-copy, public speedup, arbitrary partner
continuation, or release readiness.

## Files To Inspect

- `src/rtdsl/optix_runtime.py`
- `tests/goal2769_hit_stream_same_stream_row_reduction_consumer_test.py`
- `docs/reports/goal2769_hit_stream_same_stream_row_reduction_consumer_2026-05-31.md`
- Context:
  - `tests/goal2768_hit_stream_same_stream_row_window_consumer_test.py`
  - `docs/reports/goal2768_hit_stream_same_stream_row_window_consumer_consensus_2026-05-31.md`
  - `tests/goal2767_hit_stream_async_input_upload_test.py`

## Required Review Questions

1. Does the new CuPy RawKernel actually reduce all stored `ray_ids` and
   `primitive_ids` on the same stream using device `row_count` before any host
   scalar read?
2. Does the Python method preserve the async owner lifetime until after the
   row-reduction consumer finishes?
3. Are metadata/report boundaries honest:
   `bounded_same_stream_row_reduction_consumer_only`,
   `device_resident_row_reduction_for_partner = True`,
   `host_row_materialization_before_consumer = False`,
   `query_rays_still_packed_on_host = True`, and no true-zero-copy or public
   speedup claim?
4. Do the tests cover the exact contract without turning this into a broad
   partner-continuation or release claim?
5. Is there any hidden host sync or app-specific engine logic introduced by
   this patch?

## Validation Evidence To Check

Local Windows:

- `tests.goal2769_hit_stream_same_stream_row_reduction_consumer_test`
  `tests.goal2768_hit_stream_same_stream_row_window_consumer_test`
  `tests.goal2767_hit_stream_async_input_upload_test`
  `tests.goal2764_hit_stream_same_stream_status_consumer_test`: 24 tests OK,
  5 live CUDA tests skipped.
- Python compile check for `src/rtdsl/optix_runtime.py` and
  `tests/goal2769_hit_stream_same_stream_row_reduction_consumer_test.py`: OK.

Pod:

- SSH target used: `root@69.30.85.171 -p 22167`.
- Pod base commit: `95614865416099ff950273b6b75390505bc49e85`.
- Method: reset to latest `origin/main`, apply Goal2769 patch only, rebuild
  OptiX with `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`, run with
  `PYTHONPATH=src:.` and
  `RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so`.
- Focused live tests: 24 OK.
- Hit-stream regression slice: 41 OK.

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
