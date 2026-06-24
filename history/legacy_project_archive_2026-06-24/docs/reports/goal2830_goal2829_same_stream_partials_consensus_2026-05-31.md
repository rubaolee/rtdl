# Goal2830 Consensus for Goal2829 Same-Stream Device Partials

Date: 2026-05-31

## Scope

Goal2830 records Codex + Gemini consensus for Goal2829:

- Native OptiX fixed-radius aggregate CUDA graph can now expose graph-owned device partial rows and the native CUDA stream pointer through an explicit C ABI.
- Python can explicitly invoke `PreparedOptixFixedRadiusRankedSummaryAggregateBatchGraph3D.replay_same_stream_device_partials_summary_cupy()`.
- The bounded CuPy rawkernel consumer reduces those partial rows on the same native CUDA stream before any producer-side host scalar read or host partial-row materialization.

## Evidence

- Codex implementation and pod validation:
  - `docs/reports/goal2829_fixed_radius_graph_same_stream_device_partials_2026-05-31.md`
  - `docs/reports/goal2829_fixed_radius_graph_same_stream_device_partials_pod/goal2829_summary.json`
- Gemini independent review:
  - `docs/reviews/goal2830_gemini_review_goal2829_fixed_radius_graph_same_stream_partials_2026-05-31.md`

## Consensus Table

| Question | Consensus |
| --- | --- |
| App-agnostic native ABI | accept |
| No producer-side sync/download before consumer | accept |
| Explicit opt-in Python API | accept |
| Same native stream plus graph-owned partial buffer | accept |
| Pod evidence supports 4096-point, 4-request parity | accept |
| Broad public performance/release claims | not authorized |
| v2.5 direction toward typed primitive-payload columns | accept-with-boundary |

## Verdict

Codex + Gemini consensus accepts Goal2829 with boundary.

The accepted claim is narrow: one bounded CuPy rawkernel consumer can reduce fixed-radius graph partial rows on the same native CUDA stream and match the existing host-reduced `graph.replay()` output for the recorded pod smoke.

The following remain unauthorized:

- public RTDL-beats-CuPy claims;
- public RTDL-beats-RTNN-paper claims;
- paper reproduction claims;
- whole-app speedup claims;
- broad RT-core speedup claims;
- broad true-zero-copy claims;
- arbitrary partner continuation claims;
- v2.5 release claims.

## Next Goal

Move from this fixed aggregate summary proof to a partner-neutral typed primitive-payload column descriptor: column dtype, shape, stride, ownership, stream/event visibility, lifetime token, and explicit fallback reason should all be visible to user code and tests.
