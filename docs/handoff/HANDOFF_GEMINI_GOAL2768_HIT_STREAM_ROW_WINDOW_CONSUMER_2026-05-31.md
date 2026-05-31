# Handoff: Gemini Review For Goal2768 Hit-Stream Row-Window Consumer

Please perform an independent review of Goal2768 and write the review to:

`docs/reviews/goal2768_gemini_review_hit_stream_row_window_consumer_2026-05-31.md`

## Context

Goal2764 proved a same-stream OptiX hit-stream producer plus bounded CuPy
status consumer. Goal2767 moved the same-stream producer's input ray and
launch-param upload onto stream-ordered pinned-host `cuMemcpyHtoDAsync`.

Goal2768 is the next narrow proof: a CuPy same-stream consumer reads not only
device status, but also a bounded row window of actual hit-stream `ray_id` and
`primitive_id` columns before host scalar or row materialization.

This goal does not claim true zero-copy, public speedup, arbitrary partner
continuation, or release readiness.

## Files To Inspect

- `src/rtdsl/optix_runtime.py`
- `tests/goal2768_hit_stream_same_stream_row_window_consumer_test.py`
- `docs/reports/goal2768_hit_stream_same_stream_row_window_consumer_2026-05-31.md`
- Context:
  - `tests/goal2764_hit_stream_same_stream_status_consumer_test.py`
  - `tests/goal2767_hit_stream_async_input_upload_test.py`
  - `docs/reports/goal2767_hit_stream_async_input_upload_2026-05-31.md`
  - `docs/reports/goal2767_hit_stream_async_input_upload_consensus_2026-05-31.md`

## Required Review Questions

1. Does the new CuPy RawKernel actually read bounded `ray_ids[i]` and
   `primitive_ids[i]` on the same stream, using device `row_count` before any
   host scalar read?
2. Does the Python method preserve the async owner lifetime from Goal2767 until
   after the row-window consumer finishes?
3. Are metadata/report boundaries honest:
   `bounded_same_stream_row_window_consumer_only`,
   `device_resident_row_window_for_partner = True`,
   `host_row_materialization_before_consumer = False`,
   `query_rays_still_packed_on_host = True`, and no true-zero-copy or public
   speedup claim?
4. Do the tests cover the exact contract without turning this into a broad
   partner-continuation or release claim?
5. Is there any hidden host sync or app-specific engine logic introduced by
   this patch?

## Validation Evidence To Check

Local Windows:

- `tests.goal2768_hit_stream_same_stream_row_window_consumer_test`
  `tests.goal2767_hit_stream_async_input_upload_test`
  `tests.goal2764_hit_stream_same_stream_status_consumer_test`: 18 tests OK,
  4 live CUDA tests skipped.
- Python compile check for `src/rtdsl/optix_runtime.py` and
  `tests/goal2768_hit_stream_same_stream_row_window_consumer_test.py`: OK.

Pod:

- SSH target used: `root@69.30.85.171 -p 22167`.
- Pod base commit: `9ddc2a8c88e61a4e6a36f3eaa3c27faa10684ce8`.
- Method: reset to latest `origin/main`, apply Goal2768 patch only, rebuild
  OptiX with `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`, run with
  `PYTHONPATH=src:.` and
  `RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so`.
- Focused live tests: 18 OK.
- Hit-stream regression slice: 35 OK.

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
