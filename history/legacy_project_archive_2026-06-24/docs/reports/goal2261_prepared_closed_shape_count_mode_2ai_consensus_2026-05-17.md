# Goal2261: Prepared Closed-Shape Count Mode 2-AI Consensus

Status: accepted with boundary.

## Scope

This consensus covers Goal2258 and Goal2259:

- Goal2258 added a generic count-only surface for prepared closed-shape
  membership.
- Goal2259 recorded pushed-commit RTX pod evidence for that count surface on the
  RayJoin same-query PIP learner stream.

## Evidence

- Implementation report:
  `docs/reports/goal2258_prepared_closed_shape_membership_count_mode_2026-05-17.md`
- Pod evidence report:
  `docs/reports/goal2259_prepared_closed_shape_count_probe_pod_evidence_2026-05-17.md`
- Pod artifact:
  `docs/reports/goal2259_prepared_closed_shape_count_probe_pod_2026-05-17.json`
- Gemini review:
  `docs/reviews/goal2260_gemini_review_goal2258_2259_count_mode_2026-05-17.md`

## Consensus

Codex verdict: `accept-with-boundary`.

Gemini independent review verdict: `accept`.

Consensus verdict: `accept-with-boundary`.

Accepted narrow claim:

> On the RayJoin-exported 100,000-query same-query PIP stream, the generic
> prepared closed-shape membership count path returns the exact count `8,686`
> with median `0.041955990716814995` seconds, versus `0.05280204117298126`
> seconds for Python-visible row materialization in the same probe.

This is about `1.26x` faster than row materialization for this count-style
probe.

## Boundary

This consensus does not authorize RayJoin reproduction claims,
RTDL-beats-RayJoin claims, broad PIP speedup claims, v2.0 release readiness, or
true device-resident output-stream claims.
