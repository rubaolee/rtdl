# Goal2254: RayJoin Same-Query Current Comparison 2-AI Consensus

Status: accepted with boundary.

## Scope

This consensus covers Goal2252, the current RTDL OptiX same-query RayJoin learner
comparison after the prepared closed-shape membership path landed.

## Evidence

- Report:
  `docs/reports/goal2252_rayjoin_same_query_current_comparison_2026-05-17.md`
- LSI artifact:
  `docs/reports/goal2252_rayjoin_lsi_current_same_query_pod_2026-05-17.json`
- PIP artifact:
  `docs/reports/goal2252_rayjoin_pip_current_same_query_pod_2026-05-17.json`
- Gemini review:
  `docs/reviews/goal2253_gemini_review_goal2252_rayjoin_current_comparison_2026-05-17.md`

## Consensus

Codex verdict: `accept-with-boundary`.

Gemini independent review verdict: `accept`.

Consensus verdict: `accept-with-boundary`.

Accepted narrow table:

| Workload | RTDL route | Queries | Rows | Median seconds | Parity |
| --- | --- | ---: | ---: | ---: | --- |
| LSI | `compiled_rtdl_kernel` | 100,000 | 8,921 | 0.08359288796782494 | true |
| PIP | `prepared_closed_shape_membership_2d_optix` | 100,000 | 8,686 | 0.06329288892447948 | true |

## Boundary

This consensus does not authorize full RayJoin reproduction, a claim that RTDL
beats RayJoin, paper-scale RayJoin speedup claims, broad LSI/PIP speedup claims,
or v2.0 release readiness.

The design direction is accepted: prepared scenes and device-resident output
streams are the next likely generic runtime direction for approaching RayJoin's
tighter pure-GPU query metric without putting app logic into the RTDL engine.
