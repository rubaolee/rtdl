# Call For Review: Phoenix V3 Triangle Prepared-Graph Tutorial Candidate

Reviewer: Claude or Gemini.

Project: RTDL Phoenix V3 rebuild.

## Review Target

Please critically review this V3-only tutorial-candidate packet:

```text
docs/rebuild/v3/phoenix_v3_triangle_prepared_graph_tutorial_candidate_2026-06-21.md
docs/rebuild/v3/phoenix_v3_triangle_prepared_graph_tutorial_candidate_2026-06-21.json
tutorials/current/10_triangle_prepared_graph_chunk.md
```

Underlying reviewed intake:

```text
docs/rebuild/v3/phoenix_v3_triangle_prepared_graph_intake_2026-06-20.md
docs/rebuild/v3/evidence/phoenix_v3_triangle_prepared_graph_20260620/triangle_prepared_graph_intake_summary.json
docs/reviews/codex_phoenix_v3_triangle_prepared_graph_intake_2ai_consensus_2026-06-20.md
```

## Intended Decision

Triangle may be taught as a V3 rebuild `prepared_graph_chunk` candidate, but it
must not be promoted to M7 or public performance wording.

The teaching row must show hot-query and wall-time ratios together:

| Workload | Hot OptiX / Embree | Wall OptiX / Embree |
| --- | ---: | ---: |
| K4 clique ladder, 20,000 cliques | 116.060x | 1.677x |
| K4 clique ladder, 80,000 cliques | 347.232x | 6.342x |

## Questions For The Reviewer

1. Is it fair to teach this as `prepared_graph_chunk` candidate evidence?
2. Does the tutorial make the synthetic K4/clique boundary clear enough?
3. Does it prevent readers from treating 116x/347x as end-to-end performance?
4. Does it prevent paper-reproduction and graph-database overclaims?
5. Would you approve this as a rebuild tutorial candidate, not as M7?

## Required Review Style

Please be strict. Reject if the packet or tutorial makes the strong Triangle
hot-query ratios too easy to misread as release performance.
