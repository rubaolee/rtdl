# Goal2769: Hit-Stream Same-Stream Row-Reduction Consumer

Date: 2026-05-31

Status: accepted with boundary after pod validation and independent Gemini
review.

## Purpose

Goal2768 proved that a CuPy partner consumer can read a bounded window of
generic hit-stream rows on the same CUDA stream as the OptiX producer before
any host scalar or row materialization.

Goal2769 performs the next larger device-resident operation: it reduces all
stored hit rows in the caller-owned output buffers on the device. This is still
bounded by the output capacity, but it is no longer just a status read or a
small row-window inspection.

## What Changed

`src/rtdsl/optix_runtime.py` now contains:

`rtdl_hit_stream_same_stream_row_reduction_summary_u64`

The CuPy RawKernel reads device-resident `row_count`, `hit_event_count`,
`overflow`, `ray_ids`, and `primitive_ids` on the same CUDA stream as the OptiX
producer. It reduces all stored hit rows into a compact summary:

- stored row count;
- ray-id sum modulo `2^64`;
- primitive-id sum modulo `2^64`;
- ray-id xor fingerprint;
- primitive-id xor fingerprint;
- min/max ray id;
- min/max primitive id.

The new Python method is:

`PreparedOptixStaticTriangleScene3D.ray_triangle_hit_stream_same_stream_row_reduction_summary(...)`

## Boundary

This goal proves a bounded same-stream row reduction over all stored hit rows.
This goal does not authorize true zero-copy.
This goal does not authorize public speedup claims.
This goal does not authorize arbitrary partner continuation or release
readiness.

Important remaining limits:

- query rays are still packed on the host;
- the reduction covers stored hit rows bounded by caller capacity, not an
  unbounded stream;
- final summary materialization still synchronizes after the device consumer;
- cross-stream event handoff and richer grouped reductions need separate goals.

## Validation Plan

Local static/runtime-gated tests:

`PYTHONPATH=src:. python3 -m unittest tests.goal2769_hit_stream_same_stream_row_reduction_consumer_test tests.goal2768_hit_stream_same_stream_row_window_consumer_test tests.goal2767_hit_stream_async_input_upload_test tests.goal2764_hit_stream_same_stream_status_consumer_test`

Pod validation should rebuild OptiX from this patch and run the same focused
Goal2764/2767/2768/2769 gate with `RTDL_OPTIX_LIBRARY` pointing at the rebuilt
library.

## Validation

Windows local:

- `tests.goal2769_hit_stream_same_stream_row_reduction_consumer_test`
  `tests.goal2768_hit_stream_same_stream_row_window_consumer_test`
  `tests.goal2767_hit_stream_async_input_upload_test`
  `tests.goal2764_hit_stream_same_stream_status_consumer_test`: 25 tests OK,
  5 live CUDA tests skipped.
- `py -3 -m py_compile src\rtdsl\optix_runtime.py
  tests\goal2769_hit_stream_same_stream_row_reduction_consumer_test.py`: OK.

Pod:

- SSH target: `root@69.30.85.171 -p 22167`.
- Key: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`.
- Pod checkout base commit:
  `95614865416099ff950273b6b75390505bc49e85`
  (`Goal2768 add same-stream row-window consumer`).
- Method: reset pod checkout to latest `origin/main`, apply the Goal2769 patch
  only, rebuild with `make build-optix
  OPTIX_PREFIX=/root/vendor/optix-sdk`, and run with `PYTHONPATH=src:.` plus
  `RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so`.
- Focused live tests:
  `tests.goal2769_hit_stream_same_stream_row_reduction_consumer_test`
  `tests.goal2768_hit_stream_same_stream_row_window_consumer_test`
  `tests.goal2767_hit_stream_async_input_upload_test`
  `tests.goal2764_hit_stream_same_stream_status_consumer_test`: 25 tests OK.
- Hit-stream regression slice:
  `tests.goal2756_reusable_hit_stream_device_output_buffers_test`
  `tests.goal2758_reusable_hit_stream_buffer_perf_probe_test`
  `tests.goal2760_hit_stream_async_promotion_requirements_test`
  `tests.goal2762_hit_stream_device_status_buffers_test`
  `tests.goal2764_hit_stream_same_stream_status_consumer_test`
  `tests.goal2767_hit_stream_async_input_upload_test`
  `tests.goal2768_hit_stream_same_stream_row_window_consumer_test`
  `tests.goal2769_hit_stream_same_stream_row_reduction_consumer_test`: 42 tests OK.

## Review

Independent Gemini review is recorded in
`docs/reviews/goal2769_gemini_review_hit_stream_row_reduction_consumer_2026-05-31.md`
with verdict `accept`.

Codex + Gemini consensus is recorded in
`docs/reports/goal2769_hit_stream_same_stream_row_reduction_consumer_consensus_2026-05-31.md`.
