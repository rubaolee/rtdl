# Goal2265: Exact Prepared Closed-Shape Count 2-AI Consensus

Status: accepted with boundary.

## Scope

This consensus covers Goal2262 and Goal2263:

- Goal2262 changed prepared closed-shape count so native count no longer
  materializes final membership rows.
- Goal2263 recorded pushed-commit pod evidence for exact scalar count on the
  RayJoin same-query PIP learner stream.

## Evidence

- Implementation report:
  `docs/reports/goal2262_exact_prepared_closed_shape_count_without_final_rows_2026-05-17.md`
- Pod evidence report:
  `docs/reports/goal2263_exact_prepared_closed_shape_count_probe_pod_evidence_2026-05-17.md`
- Pod artifact:
  `docs/reports/goal2263_exact_prepared_closed_shape_count_probe_pod_2026-05-17.json`
- Gemini review:
  `docs/reviews/goal2264_gemini_review_goal2262_2263_exact_count_2026-05-17.md`

## Consensus

Codex verdict: `accept-with-boundary`.

Gemini independent review verdict: `accept`.

Consensus verdict: `accept-with-boundary`.

Accepted narrow claim:

> On the RayJoin-exported 100,000-query same-query PIP stream, the generic exact
> prepared closed-shape scalar count path returns the exact count `8,686` with
> median `0.04043779522180557` seconds, versus `0.055270278826355934` seconds
> for Python-visible row materialization in the same probe.

This is about `1.37x` faster than row materialization for this exact-count
probe. Compared with Goal2259's first count implementation, the timing
improvement is modest (`1.04x`), but the semantic cleanup is accepted: count mode
no longer produces final membership rows and frees them.

## Boundary

This consensus does not authorize RayJoin reproduction claims,
RTDL-beats-RayJoin claims, broad PIP speedup claims, v2.0 release readiness, or
true device-resident output-stream claims.
