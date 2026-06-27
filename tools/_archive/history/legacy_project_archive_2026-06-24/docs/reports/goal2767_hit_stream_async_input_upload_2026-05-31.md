# Goal2767: Hit-Stream Async Input Upload

Date: 2026-05-31

Status: accepted with boundary after pod validation and independent Gemini
review.

## Purpose

Goal2764 proved a narrow same-stream OptiX hit-stream producer plus bounded CuPy
status consumer without a producer-side host scalar sync. Claude accepted that
proof with boundary and called out one real remaining gap: the async native path
still used synchronous `upload()` calls for input rays and launch parameters.

Goal2767 closes that gap for the on-stream hit-stream producer path.

## What Changed

New helper in `src/native/optix/rtdl_optix_core.cpp`:

`upload_async(CUdeviceptr dst, const T* src, size_t count, CUstream stream)`

The helper uses `cuMemcpyHtoDAsync` and enqueues the copy onto the same
caller-provided CUDA stream as the status clears, flag clear, OptiX launch, and
CuPy consumer.

The native `NativeRayTriangleHitStreamAsyncLaunchOwner` now owns pinned host
staging memory:

- `host_rays`;
- `host_params`.

The on-stream producer now:

- allocates pinned host staging with `cuMemAllocHost`;
- copies packed rays and launch params into that staging memory;
- enqueues ray and launch-param copies with `upload_async`;
- keeps both device temporary storage and pinned host staging alive until the
  async owner release;
- synchronizes the recorded stream before freeing staging and temporary device
  memory.

## Boundary

This goal removes the synchronous CUDA H2D copy calls from the same-stream
producer path. It does not remove the CPU-side ray packing step, and it does not
make the query input itself device-resident.

This goal does not authorize true zero-copy.
This goal does not authorize public speedup claims.
This goal does not authorize broad partner continuation claims or release
readiness.

The precise stream-ordered improvement is:

`producer_input_upload_mode = stream_ordered_pinned_host_to_device_async`

The precise remaining limitation is:

`query_rays_still_packed_on_host = True`

## Validation

Local static/runtime-gated tests:

`PYTHONPATH=src:. python3 -m unittest tests.goal2767_hit_stream_async_input_upload_test tests.goal2764_hit_stream_same_stream_status_consumer_test`

Windows local result:

- `tests.goal2767_hit_stream_async_input_upload_test`
  `tests.goal2764_hit_stream_same_stream_status_consumer_test`: 12 tests OK,
  3 live CUDA tests skipped.
- `py -3 -m py_compile src\rtdsl\optix_runtime.py
  tests\goal2767_hit_stream_async_input_upload_test.py`: OK.

Pod validation:

- SSH target: `root@69.30.85.171 -p 22167`.
- Key: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`.
- Pod checkout base commit: `06f80b4c5782448112833495039850676cd8d167`
  (`Goal2764 record final pushed pod validation`).
- Validation method: reset pod checkout to `origin/main`, remove stale
  Goal2767 scratch files from the previous patch replay, apply the final
  Goal2767 patch only, rebuild with
  `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`, and run with
  `PYTHONPATH=src:.` plus
  `RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so`.
- Dependency probe: Torch `2.8.0+cu128`, CuPy `14.1.0`, pytest `9.0.3`.
- `tests.goal2767_hit_stream_async_input_upload_test`
  `tests.goal2764_hit_stream_same_stream_status_consumer_test`: 13 tests OK.
- Corrected status-buffer live slice:
  `tests.goal2762_hit_stream_device_status_buffers_test`
  `tests.goal2764_hit_stream_same_stream_status_consumer_test`
  `tests.goal2767_hit_stream_async_input_upload_test`: 17 tests OK on the
  first patch replay before review/consensus files were added.
- Reusable-buffer / async-promotion slice:
  `tests.goal2756_reusable_hit_stream_device_output_buffers_test`
  `tests.goal2758_reusable_hit_stream_buffer_perf_probe_test`
  `tests.goal2760_hit_stream_async_promotion_requirements_test`
  `tests.goal2762_hit_stream_device_status_buffers_test`
  `tests.goal2764_hit_stream_same_stream_status_consumer_test`
  `tests.goal2767_hit_stream_async_input_upload_test`: 30 tests OK on the
  final patch replay.

## Review Requirement

This is a code-bearing v2.5 runtime hardening goal. It received independent
Gemini review in
`docs/reviews/goal2767_gemini_review_hit_stream_async_input_upload_2026-05-31.md`
with verdict `accept-with-boundary`.

Codex + Gemini consensus is recorded in
`docs/reports/goal2767_hit_stream_async_input_upload_consensus_2026-05-31.md`.

Any future public zero-copy or speedup wording still requires separate 3-AI
consensus.
