# Goal2770 Consensus: Hit-Stream Event-Ordered Row-Reduction Consumer

Date: 2026-05-31

Status: accepted with boundary as internal v2.5 runtime-hardening evidence.

## Scope

Goal2770 extends the hit-stream continuation path from same-stream ordering to
event-ordered cross-stream ordering. The OptiX producer enqueues on a Torch CUDA
producer stream, records a CUDA event after the producer enqueue, and a separate
CuPy consumer stream waits on that event before reducing stored generic
hit-stream rows.

This consensus does not authorize true zero-copy, public speedup claims, broad
partner continuation claims, or release readiness.

## Evidence

Codex implementation and validation:

- Added
  `PreparedOptixStaticTriangleScene3D.ray_triangle_hit_stream_event_ordered_row_reduction_summary(...)`.
- Added `_run_hit_stream_event_ordered_row_reduction_summary_cupy(...)`, which
  creates a non-blocking CuPy consumer stream and calls
  `cupy.cuda.runtime.streamWaitEvent(...)` before the row-reduction kernel.
- Preserved the async native owner, producer stream, and producer event until
  the consumer finishes.
- Metadata records
  `producer_consumer_stream_ordering = cuda_event_cross_stream`,
  `cuda_event_cross_stream_ordering_proven = True`,
  `cuda_event_wait_inserted_before_consumer = True`,
  `async_partner_continuation_authorization_scope =
  bounded_event_ordered_row_reduction_consumer_only`, and
  `query_rays_still_packed_on_host = True`.
- Local validation:
  `tests.goal2770_hit_stream_event_ordered_row_reduction_consumer_test`
  `tests.goal2769_hit_stream_same_stream_row_reduction_consumer_test`
  `tests.goal2768_hit_stream_same_stream_row_window_consumer_test`
  `tests.goal2767_hit_stream_async_input_upload_test`
  `tests.goal2764_hit_stream_same_stream_status_consumer_test`: 29 tests OK,
  6 live CUDA tests skipped.
- Pod validation from latest `origin/main` plus Goal2770 patch:
  focused live tests 29 OK and hit-stream regression slice 46 OK.

External review:

- `docs/reviews/goal2770_gemini_review_hit_stream_event_ordered_row_reduction_2026-05-31.md`
  gives verdict `accept-with-boundary`.
- Gemini accepted the event-ordered cross-stream contract, event wait, lifetime
  boundary, metadata/report boundaries, and absence of hidden pre-consumer host
  sync or app-specific engine logic.

## Decision

Codex + Gemini consensus accepts Goal2770 with boundary.

The accepted claim is narrow:

`async_partner_continuation_authorization_scope = bounded_event_ordered_row_reduction_consumer_only`

The remaining boundary is explicit:

- query rays are still packed on the host;
- the reduction covers stored hit rows bounded by caller output capacity, not an unbounded stream;
- final summary materialization still synchronizes after the consumer;
- richer grouped reductions, multi-partner conformance, and public performance
  claims need separate goals, pod evidence, and review.
