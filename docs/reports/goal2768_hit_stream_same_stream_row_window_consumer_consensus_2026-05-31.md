# Goal2768 Consensus: Hit-Stream Same-Stream Row-Window Consumer

Date: 2026-05-31

Status: accepted with boundary as internal v2.5 runtime-hardening evidence.

## Scope

Goal2768 extends the Goal2764/Goal2767 same-stream proof from device status
only to a bounded row-window consumer. The CuPy partner kernel reads device
`row_count`, `hit_event_count`, `overflow`, and bounded `ray_id` /
`primitive_id` hit rows on the same CUDA stream before any host scalar or row
materialization.

This consensus does not authorize true zero-copy, public speedup claims, broad
partner continuation claims, or release readiness.

## Evidence

Codex implementation and validation:

- Added `rtdl_hit_stream_same_stream_row_window_summary_u64` as a CuPy RawKernel
  in `src/rtdsl/optix_runtime.py`.
- Added
  `PreparedOptixStaticTriangleScene3D.ray_triangle_hit_stream_same_stream_row_window_summary(...)`.
- Preserved the Goal2767 async owner lifetime: the native async launch owner is
  closed only after the same-stream row-window consumer completes.
- Metadata records
  `async_partner_continuation_authorization_scope =
  bounded_same_stream_row_window_consumer_only`,
  `device_resident_row_window_for_partner = True`,
  `host_row_materialization_before_consumer = False`, and
  `query_rays_still_packed_on_host = True`.
- Local validation:
  `tests.goal2768_hit_stream_same_stream_row_window_consumer_test`
  `tests.goal2767_hit_stream_async_input_upload_test`
  `tests.goal2764_hit_stream_same_stream_status_consumer_test`: 18 tests OK,
  4 live CUDA tests skipped.
- Pod validation from latest `origin/main` plus Goal2768 patch:
  focused live tests 18 OK and hit-stream regression slice 35 OK.

External review:

- `docs/reviews/goal2768_gemini_review_hit_stream_row_window_consumer_2026-05-31.md`
  gives verdict `accept`.
- Gemini accepted the bounded row-window contract, same-stream CuPy consumer,
  metadata/report boundaries, and absence of app-specific engine logic or
  misleading true-zero-copy/speedup claims.

## Decision

Codex + Gemini consensus accepts Goal2768 with boundary.

The accepted claim is narrow:

`async_partner_continuation_authorization_scope = bounded_same_stream_row_window_consumer_only`

The remaining boundary is explicit:

- query rays are still packed on the host;
- the consumer reads only a bounded row window, not an unbounded stream;
- final summary materialization still synchronizes after the consumer;
- cross-stream ordering, larger device-resident reductions, and full partner
  continuation need separate goals, pod evidence, and review.
