# Goal2764 Consensus: Same-Stream Hit-Stream Status Consumer

Date: 2026-05-31

## Verdict

Goal2764 is accepted as internal v2.5 evidence for a narrow runtime-contract
claim:

RTDL can launch an OptiX hit-stream producer into caller-owned CUDA columns and
status buffers on a caller-provided CUDA stream, then launch a bounded CuPy
RawKernel consumer on the same stream that reads device-resident `row_count`,
`hit_event_count`, and `overflow` before any host scalar row-count read.

This does not authorize true zero-copy wording, broad async partner continuation,
public speedup claims, event-based cross-stream continuation, arbitrary
row-stream consumers, or release readiness.

## Reviews

- Codex implementation and validation: accepted with boundary.
- Gemini review:
  `docs/reviews/goal2766_gemini_review_goal2764_hit_stream_same_stream_status_consumer_2026-05-31.md`
  verdict `accept`.
- Claude review:
  `docs/reviews/goal2765_claude_review_goal2764_hit_stream_same_stream_status_consumer_2026-05-31.md`
  verdict `accept-with-boundary`.

Codex+Codex does not count as external consensus. This record uses distinct
external systems, Gemini and Claude.

## Evidence

- Local Windows: `tests.goal2764_hit_stream_same_stream_status_consumer_test`,
  `tests.goal2760_hit_stream_async_promotion_requirements_test`, and
  `tests.goal2762_hit_stream_device_status_buffers_test` ran with 15 total
  tests, 12 passed and 3 skipped for local CUDA/OptiX availability.
- Pod `root@69.30.85.171 -p 22167` rebuilt OptiX with
  `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`.
- Pod live Goal2764 test: 6 passed, 0 skipped.
- Pod corrected hit-stream gate: 58 passed.

## Boundaries And Follow-Up

Accepted now:

- same-stream producer/consumer ordering for the bounded CuPy status consumer;
- device-resident status consumed by partner code;
- no producer-side host scalar sync before that consumer;
- async launch owner keeps temporary native storage alive until release.

Still future work:

- switch input ray/launch-param upload to a fully host-async lifetime-owned path;
- add event-based cross-stream ordering;
- add bounded row-window/full-row partner consumers;
- keep scoped metadata distinct from general partner continuation authorization;
- require separate review before any public true-zero-copy or speedup wording.
