# Goal2770: Hit-Stream Event-Ordered Row-Reduction Consumer

Date: 2026-05-31

Status: accepted with boundary after pod validation and independent Gemini
review.

## Purpose

Goal2769 proved a same-stream CuPy consumer can reduce all stored generic
hit-stream rows before host scalar or row materialization.

Goal2770 proves the next ordering model: an OptiX producer stream records a
CUDA event, and a separate CuPy consumer stream waits on that event before
running the same bounded row-reduction consumer. This is the first
cross-stream continuation proof for the generic hit-stream path.

## What Changed

`src/rtdsl/optix_runtime.py` now contains:

`PreparedOptixStaticTriangleScene3D.ray_triangle_hit_stream_event_ordered_row_reduction_summary(...)`

The method:

- enqueues the OptiX hit-stream producer on a Torch CUDA producer stream;
- records a Torch CUDA event after the producer enqueue;
- passes the raw CUDA event pointer to a CuPy consumer stream;
- calls `cupy.cuda.runtime.streamWaitEvent(...)`;
- launches the generic row-reduction CuPy RawKernel on the separate consumer
  stream;
- materializes only the compact summary after the consumer stream finishes.

## Boundary

This goal proves a bounded event-ordered cross-stream row reduction over stored
generic hit rows.
This goal does not authorize true zero-copy.
This goal does not authorize public speedup claims.
This goal does not authorize arbitrary partner continuation or release
readiness.

Important remaining limits:

- query rays are still packed on the host;
- the reduction covers stored hit rows bounded by caller output capacity, not
  an unbounded stream;
- final summary materialization still synchronizes after the consumer;
- richer grouped reductions and multi-partner conformance need separate goals.

## Validation Plan

Local static/runtime-gated tests:

`PYTHONPATH=src:. python3 -m unittest tests.goal2770_hit_stream_event_ordered_row_reduction_consumer_test tests.goal2769_hit_stream_same_stream_row_reduction_consumer_test tests.goal2768_hit_stream_same_stream_row_window_consumer_test tests.goal2767_hit_stream_async_input_upload_test tests.goal2764_hit_stream_same_stream_status_consumer_test`

Pod validation should rebuild OptiX from this patch and run the same focused
Goal2764/2767/2768/2769/2770 gate with `RTDL_OPTIX_LIBRARY` pointing at the
rebuilt library.

## Validation

Windows local:

- `tests.goal2770_hit_stream_event_ordered_row_reduction_consumer_test`
  `tests.goal2769_hit_stream_same_stream_row_reduction_consumer_test`
  `tests.goal2768_hit_stream_same_stream_row_window_consumer_test`
  `tests.goal2767_hit_stream_async_input_upload_test`
  `tests.goal2764_hit_stream_same_stream_status_consumer_test`: 30 tests OK,
  6 live CUDA tests skipped.
- `py -3 -m py_compile src\rtdsl\optix_runtime.py
  tests\goal2770_hit_stream_event_ordered_row_reduction_consumer_test.py`: OK.

Pod:

- SSH target: `root@69.30.85.171 -p 22167`.
- Key: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`.
- Pod checkout base commit:
  `9f7611d85f4b65385c13b626d7191c5a23d7c8fd`
  (`Goal2769 add same-stream row reduction consumer`).
- Method: reset pod checkout to latest `origin/main`, apply the Goal2770 patch
  only, rebuild with `make build-optix
  OPTIX_PREFIX=/root/vendor/optix-sdk`, and run with `PYTHONPATH=src:.` plus
  `RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so`.
- Focused live tests:
  `tests.goal2770_hit_stream_event_ordered_row_reduction_consumer_test`
  `tests.goal2769_hit_stream_same_stream_row_reduction_consumer_test`
  `tests.goal2768_hit_stream_same_stream_row_window_consumer_test`
  `tests.goal2767_hit_stream_async_input_upload_test`
  `tests.goal2764_hit_stream_same_stream_status_consumer_test`: 30 tests OK.
- Hit-stream regression slice:
  `tests.goal2756_reusable_hit_stream_device_output_buffers_test`
  `tests.goal2758_reusable_hit_stream_buffer_perf_probe_test`
  `tests.goal2760_hit_stream_async_promotion_requirements_test`
  `tests.goal2762_hit_stream_device_status_buffers_test`
  `tests.goal2764_hit_stream_same_stream_status_consumer_test`
  `tests.goal2767_hit_stream_async_input_upload_test`
  `tests.goal2768_hit_stream_same_stream_row_window_consumer_test`
  `tests.goal2769_hit_stream_same_stream_row_reduction_consumer_test`
  `tests.goal2770_hit_stream_event_ordered_row_reduction_consumer_test`: 47 tests OK.

## Review

Independent Gemini review is recorded in
`docs/reviews/goal2770_gemini_review_hit_stream_event_ordered_row_reduction_2026-05-31.md`
with verdict `accept-with-boundary`.

Codex + Gemini consensus is recorded in
`docs/reports/goal2770_hit_stream_event_ordered_row_reduction_consumer_consensus_2026-05-31.md`.
