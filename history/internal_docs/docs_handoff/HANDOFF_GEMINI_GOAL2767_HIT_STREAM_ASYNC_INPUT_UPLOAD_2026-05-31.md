# Handoff: Gemini Review For Goal2767 Hit-Stream Async Input Upload

Please perform an independent review of Goal2767 and write the review to:

`docs/reviews/goal2767_gemini_review_hit_stream_async_input_upload_2026-05-31.md`

## Context

Goal2764 added a same-stream OptiX hit-stream producer plus bounded CuPy status
consumer. A prior Claude review accepted the direction with boundary but noted
that the producer still used synchronous host-to-device `upload()` calls for
input rays and launch parameters.

Goal2767 addresses only that gap. It does not claim true zero-copy, broad
partner continuation, public speedup, or release readiness.

## Files To Inspect

- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `tests/goal2767_hit_stream_async_input_upload_test.py`
- `docs/reports/goal2767_hit_stream_async_input_upload_2026-05-31.md`
- Relevant predecessor tests/reports for context:
  - `tests/goal2764_hit_stream_same_stream_status_consumer_test.py`
  - `docs/reports/goal2764_hit_stream_same_stream_status_consumer_2026-05-31.md`
  - `docs/reviews/goal2765_claude_review_goal2764_hit_stream_same_stream_status_consumer_2026-05-31.md`
  - `docs/reviews/goal2766_gemini_review_goal2764_hit_stream_same_stream_status_consumer_2026-05-31.md`

## Required Review Questions

1. Does Goal2767 actually replace the same-stream producer's blocking
   `upload()` calls for input rays and launch parameters with stream-ordered
   `cuMemcpyHtoDAsync` copies?
2. Does the native async launch owner keep pinned host staging memory alive
   until the caller releases the async owner, and does release synchronize the
   recorded producer stream before freeing staging memory?
3. Are the Python metadata and report honest about the boundary:
   `producer_input_upload_mode =
   stream_ordered_pinned_host_to_device_async`,
   `producer_input_upload_host_blocking_cuda_copy = False`,
   `query_rays_still_packed_on_host = True`, and no true-zero-copy or public
   speedup claim?
4. Do the tests cover the exact contract without overclaiming?
5. Is there any risk that the patch introduces a lifetime bug, hidden host sync,
   app-specific engine logic, or misleading public claim wording?

## Validation Evidence To Check

Local Windows:

- `tests.goal2767_hit_stream_async_input_upload_test`
  `tests.goal2764_hit_stream_same_stream_status_consumer_test`: 12 tests OK,
  3 live CUDA tests skipped.
- Python compile check for `src/rtdsl/optix_runtime.py` and
  `tests/goal2767_hit_stream_async_input_upload_test.py`: OK.

Pod validation:

- SSH target used: `root@69.30.85.171 -p 22167`.
- Pod base commit: `06f80b4c5782448112833495039850676cd8d167`.
- Method: reset to `origin/main`, apply Goal2767 patch only, rebuild OptiX with
  `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`, run with
  `PYTHONPATH=src:.` and
  `RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so`.
- Dependencies: Torch `2.8.0+cu128`, CuPy `14.1.0`, pytest `9.0.3`.
- Focused live tests: 12 OK.
- Corrected status-buffer live slice: 17 OK.
- Reusable-buffer / async-promotion slice: 29 OK.

## Expected Output Format

Use one of these verdicts exactly: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

Please include:

- verdict;
- short technical reasoning;
- any blocking issues;
- any non-blocking follow-up debt;
- explicit statement that this review is independent Gemini review and not
  Codex self-review.
