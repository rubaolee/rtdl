# Goal2251: Prepared Closed-Shape Membership 2-AI Consensus

Status: accepted with boundary.

## Scope

This consensus covers Goal2248 and Goal2249:

- Goal2248 implemented a prepared generic OptiX closed-shape membership
  primitive.
- Goal2249 recorded pushed-commit RTX pod evidence for the RayJoin same-query
  PIP learner workload using that prepared primitive.

## Evidence

- Implementation report:
  `docs/reports/goal2248_prepared_closed_shape_membership_2026-05-17.md`
- Pod evidence report:
  `docs/reports/goal2249_rayjoin_pip_prepared_closed_shape_pod_evidence_2026-05-17.md`
- Pod artifact:
  `docs/reports/goal2249_rayjoin_pip_prepared_closed_shape_same_query_pod_2026-05-17.json`
- Gemini review:
  `docs/reviews/goal2250_gemini_review_goal2248_2249_prepared_closed_shape_2026-05-17.md`

## Consensus

Codex implementation verdict: `accept-with-boundary`.

Gemini independent review verdict: `accept`.

Consensus verdict: `accept-with-boundary`.

The accepted narrow claim is:

> On the RayJoin-exported 100,000-query same-query PIP stream, RTDL OptiX can
> execute the app-agnostic prepared closed-shape membership primitive with exact
> row parity against the CPU reference, 8,686 rows per run, and median time
> `0.06389576941728592` seconds on the recorded RTX A5000 pod at commit
> `9e8c60ef6ae6a1311940b76861fc9a665a52dcc5`.

This improves the Goal2245 non-prepared but prepacked generic closed-shape
measurement (`0.08343074284493923` seconds median) by about `1.31x` on the
same query stream.

## Boundary

This consensus does not authorize:

- full RayJoin reproduction,
- a claim that RTDL beats RayJoin,
- paper-scale RayJoin speedup claims,
- v2.0 release readiness,
- broad PIP acceleration claims,
- or any app-specific native engine customization.

The design lesson is accepted for the future-version to-do list: prepared
generic scenes and device-resident output streams are likely needed for a
stronger RayJoin-style fight, but that is future work unless separately
promoted.
