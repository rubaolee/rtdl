# Goal2769 Consensus: Hit-Stream Same-Stream Row-Reduction Consumer

Date: 2026-05-31

Status: accepted with boundary as internal v2.5 runtime-hardening evidence.

## Scope

Goal2769 extends the same-stream hit-stream continuation path from bounded row
inspection to an all-stored-row device reduction. The CuPy partner kernel reads
device `row_count`, `hit_event_count`, `overflow`, `ray_ids`, and
`primitive_ids` on the same CUDA stream before host scalar or row
materialization, then emits compact row-count/fingerprint/min/max summaries.

This consensus does not authorize true zero-copy, public speedup claims, broad
partner continuation claims, or release readiness.

## Evidence

Codex implementation and validation:

- Added `rtdl_hit_stream_same_stream_row_reduction_summary_u64` as a CuPy
  RawKernel in `src/rtdsl/optix_runtime.py`.
- Added
  `PreparedOptixStaticTriangleScene3D.ray_triangle_hit_stream_same_stream_row_reduction_summary(...)`.
- Preserved the Goal2767/2768 async owner lifetime: the native async launch
  owner is closed only after the same-stream row-reduction consumer completes.
- Metadata records
  `async_partner_continuation_authorization_scope =
  bounded_same_stream_row_reduction_consumer_only`,
  `device_resident_row_reduction_for_partner = True`,
  `host_row_materialization_before_consumer = False`, and
  `query_rays_still_packed_on_host = True`.
- Local validation:
  `tests.goal2769_hit_stream_same_stream_row_reduction_consumer_test`
  `tests.goal2768_hit_stream_same_stream_row_window_consumer_test`
  `tests.goal2767_hit_stream_async_input_upload_test`
  `tests.goal2764_hit_stream_same_stream_status_consumer_test`: 24 tests OK,
  5 live CUDA tests skipped.
- Pod validation from latest `origin/main` plus Goal2769 patch:
  focused live tests 24 OK and hit-stream regression slice 41 OK.

External review:

- `docs/reviews/goal2769_gemini_review_hit_stream_row_reduction_consumer_2026-05-31.md`
  gives verdict `accept`.
- Gemini accepted the same-stream device-row reduction contract, async owner
  lifetime, metadata/report boundaries, and absence of app-specific engine
  logic or misleading true-zero-copy/speedup claims.

## Decision

Codex + Gemini consensus accepts Goal2769 with boundary.

The accepted claim is narrow:

`async_partner_continuation_authorization_scope = bounded_same_stream_row_reduction_consumer_only`

The remaining boundary is explicit:

- query rays are still packed on the host;
- the reduction covers stored hit rows bounded by caller output capacity, not an unbounded stream;
- final summary materialization still synchronizes after the consumer;
- event-based cross-stream ordering and richer grouped reductions need separate
  goals, pod evidence, and review.
