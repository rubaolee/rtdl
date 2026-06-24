# Goal2768: Hit-Stream Same-Stream Row-Window Consumer

Date: 2026-05-31

Status: accepted with boundary after pod validation and independent Gemini
review.

## Purpose

Goal2764 proved that a bounded CuPy consumer can read device-resident hit-stream
status on the same CUDA stream as the OptiX producer. Goal2767 removed the
blocking input-upload calls from that same-stream producer path.

Goal2768 takes the next narrow step: the partner consumer reads not only status
scalars, but also a bounded row window of actual hit-stream `ray_id` and
`primitive_id` columns before any host scalar or row materialization.

## What Changed

`src/rtdsl/optix_runtime.py` now contains a second same-stream CuPy RawKernel:

`rtdl_hit_stream_same_stream_row_window_summary_u64`

The kernel reads:

- device `row_count`;
- device `hit_event_count`;
- device `overflow`;
- bounded `ray_ids[i]`;
- bounded `primitive_ids[i]`.

It writes a compact summary containing row count, stored count, bounded row
window count, first/last row ids, and simple id sums. The summary is
materialized only after the same-stream partner consumer finishes.

The new Python method is:

`PreparedOptixStaticTriangleScene3D.ray_triangle_hit_stream_same_stream_row_window_summary(...)`

## Boundary

This goal proves a bounded row-window consumer only.
This goal does not authorize true zero-copy.
This goal does not authorize public speedup claims.
This goal does not authorize arbitrary partner continuation or release
readiness.

The accepted narrow contract, if pod validation and review pass, is:

`async_partner_continuation_authorization_scope = bounded_same_stream_row_window_consumer_only`

Important remaining limits:

- query rays are still packed on the host;
- the consumer reads only a caller-bounded row window, not an unbounded stream;
- final summary materialization still synchronizes after the consumer;
- broader row-stream continuation, event-based cross-stream ordering, and full
  partner reductions need separate goals.

## Validation Plan

Local static/runtime-gated tests:

`PYTHONPATH=src:. python3 -m unittest tests.goal2768_hit_stream_same_stream_row_window_consumer_test tests.goal2767_hit_stream_async_input_upload_test tests.goal2764_hit_stream_same_stream_status_consumer_test`

Pod validation should rebuild OptiX from this patch and run the same focused
Goal2764/2767/2768 gate with `RTDL_OPTIX_LIBRARY` pointing at the rebuilt
library.

## Validation

Windows local:

- `tests.goal2768_hit_stream_same_stream_row_window_consumer_test`
  `tests.goal2767_hit_stream_async_input_upload_test`
  `tests.goal2764_hit_stream_same_stream_status_consumer_test`: 19 tests OK,
  4 live CUDA tests skipped.
- `py -3 -m py_compile src\rtdsl\optix_runtime.py
  tests\goal2768_hit_stream_same_stream_row_window_consumer_test.py`: OK.

Pod:

- SSH target: `root@69.30.85.171 -p 22167`.
- Key: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`.
- Pod checkout base commit:
  `9ddc2a8c88e61a4e6a36f3eaa3c27faa10684ce8`
  (`Goal2767 harden async hit stream input upload`).
- Method: reset pod checkout to latest `origin/main`, apply the Goal2768 patch
  only, rebuild with `make build-optix
  OPTIX_PREFIX=/root/vendor/optix-sdk`, and run with `PYTHONPATH=src:.` plus
  `RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so`.
- Focused live tests:
  `tests.goal2768_hit_stream_same_stream_row_window_consumer_test`
  `tests.goal2767_hit_stream_async_input_upload_test`
  `tests.goal2764_hit_stream_same_stream_status_consumer_test`: 19 tests OK.
- Hit-stream regression slice:
  `tests.goal2756_reusable_hit_stream_device_output_buffers_test`
  `tests.goal2758_reusable_hit_stream_buffer_perf_probe_test`
  `tests.goal2760_hit_stream_async_promotion_requirements_test`
  `tests.goal2762_hit_stream_device_status_buffers_test`
  `tests.goal2764_hit_stream_same_stream_status_consumer_test`
  `tests.goal2767_hit_stream_async_input_upload_test`
  `tests.goal2768_hit_stream_same_stream_row_window_consumer_test`: 36 tests OK.

## Review

Independent Gemini review is recorded in
`docs/reviews/goal2768_gemini_review_hit_stream_row_window_consumer_2026-05-31.md`
with verdict `accept`.

Codex + Gemini consensus is recorded in
`docs/reports/goal2768_hit_stream_same_stream_row_window_consumer_consensus_2026-05-31.md`.
