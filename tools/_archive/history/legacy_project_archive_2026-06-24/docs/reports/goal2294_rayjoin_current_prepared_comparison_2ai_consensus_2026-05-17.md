# Goal2294: Current Prepared RayJoin-Style Comparison 2-AI Consensus

Status: accepted.

## Scope

Goal2294 closes the Goal2292 current prepared RayJoin-style comparison package.
The accepted claim is narrow: on one recorded RTX A5000 pod and the two
RayJoin-exported 100k query streams, the current v2 learner routes are:

- LSI: prepared segment-pair intersection with a prepacked left/query batch;
- PIP: prepared closed-shape membership with prepacked points.

Goal2252's LSI number remains useful historical context, but it is not the
current v2 learner route after Goal2287/2291.

## Evidence

- Report:
  `docs/reports/goal2292_rayjoin_current_prepared_comparison_2026-05-17.md`
- Pod artifact:
  `docs/reports/goal2292_rayjoin_current_prepared_comparison_pod_2026-05-17.json`
- Runner:
  `scripts/goal2292_rayjoin_current_prepared_comparison.py`
- Gemini review:
  `docs/reviews/goal2293_gemini_review_goal2292_current_rayjoin_comparison_2026-05-17.md`

## Consensus

Codex verdict: `accept`.

Gemini/Antigravity verdict: `accept`.

The agreed interpretation is:

- the Goal2252 LSI route is stale-route context, not current v2 learner
  performance;
- the Goal2292 script uses the intended prepared routes for both LSI and PIP;
- the artifact supports the narrow current comparison;
- the report's boundaries are strict enough to avoid RayJoin paper reproduction,
  RTDL-beats-RayJoin, whole-app speedup, true zero-copy, or v2.0 release
  readiness claims.

## Claim Boundary

Allowed claim:

On the recorded RTX A5000 pod and two RayJoin-exported 100k query streams, the
current prepared v2 learner routes measured `0.010591023s` LSI raw rows,
`0.010393109s` LSI scalar count, `0.052356653s` PIP positive rows, and
`0.039025227s` PIP scalar count.

Not allowed:

- full RayJoin reproduction;
- RTDL beats RayJoin;
- paper-scale RayJoin speedup claims;
- broad LSI or PIP speedup claims;
- whole-application speedup;
- true zero-copy;
- v2.0 release readiness.
