# Goal2767 Consensus: Hit-Stream Async Input Upload

Date: 2026-05-31

Status: accepted with boundary as internal v2.5 runtime-hardening evidence.

## Scope

Goal2767 closes one concrete host-blocking gap left after Goal2764: the
same-stream OptiX hit-stream producer no longer uses blocking `upload()` calls
for input rays and launch parameters. It now stages those inputs in
owner-retained pinned host memory and enqueues stream-ordered `cuMemcpyHtoDAsync`
copies on the caller stream.

This consensus does not authorize true zero-copy, public speedup claims, broad
partner continuation claims, or release readiness.

## Evidence

Codex implementation and validation:

- Added `upload_async(...)` in `src/native/optix/rtdl_optix_core.cpp`.
- Updated
  `run_prepared_static_triangle_scene_3d_ray_triangle_hit_stream_into_device_columns_with_status_on_stream_optix`
  to use pinned host staging plus `cuMemcpyHtoDAsync`.
- Extended the async launch owner to retain `host_rays` and `host_params` until
  owner release, and to synchronize the recorded producer stream before freeing
  staging and temporary device memory.
- Added Python metadata:
  `producer_input_upload_mode =
  stream_ordered_pinned_host_to_device_async`,
  `producer_input_upload_host_blocking_cuda_copy = False`, and
  `query_rays_still_packed_on_host = True`.
- Local validation:
  `tests.goal2767_hit_stream_async_input_upload_test`
  `tests.goal2764_hit_stream_same_stream_status_consumer_test`: 12 tests OK,
  3 live CUDA tests skipped.
- Pod validation from `origin/main` plus Goal2767 patch:
  focused live tests 12 OK, corrected status-buffer live slice 17 OK, and
  reusable-buffer / async-promotion slice 29 OK.

External review:

- `docs/reviews/goal2767_gemini_review_hit_stream_async_input_upload_2026-05-31.md`
  gives verdict `accept-with-boundary`.
- Gemini explicitly checked the async upload replacement, pinned staging
  lifetime/release ordering, boundary metadata, lack of true-zero-copy and
  public speedup claims, app-agnostic engine boundary, and absence of blocking
  issues.

## Decision

Codex + Gemini consensus accepts Goal2767 with boundary.

The accepted claim is narrow:

`same_stream_hit_stream_input_upload = stream_ordered_pinned_host_to_device_async`

The remaining boundary is explicit:

- query rays are still packed on the host;
- the input path is reduced host blocking, not true zero-copy;
- only the bounded same-stream status consumer is proven;
- fuller row-window or cross-stream partner continuations need separate goals,
  pod evidence, and review.
