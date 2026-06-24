# Triangle Prepared-Graph Chunk

Status: V3 rebuild tutorial with one M7-qualified row-scoped claim; not a release claim and not release authorization.

This lesson shows how to read the current Triangle prepared-graph evidence
without turning it into a paper or graph-database claim.

## What This Example Teaches

Triangle counting is used here because it exposes a reusable RTDL shape:

```text
prepared graph input -> repeated ray-triangle weighted-any-hit query -> compact
triangle summary
```

That is the V3 `prepared_graph_chunk` idea. The current evidence uses generated
K4 clique-ladder workloads and the same RT-Graph 2A1 contract on Embree and
OptiX.

## Current Evidence

| Workload | Hot OptiX / Embree | Wall OptiX / Embree | Oracle triangles |
| --- | ---: | ---: | ---: |
| K4 clique ladder, 20,000 cliques | 116.060x | 1.677x | 80,000 |
| K4 clique ladder, 80,000 cliques | 347.232x | 6.342x | 320,000 |

Both backends match the oracle. OptiX is much faster for the hot repeated query,
but wall-time wins are smaller. That gap is part of the result. Only the
80,000-clique row is M7-qualified, and only under the exact non-graph stream
row ID `prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream`.

## What To Learn

- Use the hot-query column to understand the reusable prepared-query signal.
- Use the wall-time column to keep setup and end-to-end costs honest.
- Treat `prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream` as
  the exact M7-qualified row-scoped claim.
- Do not treat this as M113 graph-capture readiness or universal prepared graph
  execution.
- Keep this as a synthetic K4/clique-ladder lesson, not a paper dataset result.

## Source Packets

- `docs/rebuild/v3/phoenix_v3_triangle_prepared_graph_intake_2026-06-20.md`
- `docs/rebuild/v3/phoenix_v3_triangle_prepared_graph_tutorial_candidate_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_triangle_prepared_graph_80000_m7_final_review_packet_2026-06-21.md`
- `docs/rebuild/v3/evidence/phoenix_v3_triangle_prepared_graph_20260620/triangle_prepared_graph_intake_summary.json`
- `docs/reviews/codex_phoenix_v3_triangle_prepared_graph_intake_2ai_consensus_2026-06-20.md`
- `docs/reviews/codex_subagent_phoenix_v3_triangle_prepared_graph_80000_m7_final_review_packet_review_2026-06-21.md`
- `docs/reviews/codex_phoenix_v3_triangle_prepared_graph_80000_m7_final_review_packet_2ai_consensus_2026-06-21.md`

## Claim Boundary

Allowed:

```text
Exactly `prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream` is
M7-qualified row-scoped: on the generated K4 clique-ladder synthetic RT-Graph
2A1 contract, RTDL OptiX shows 347.232x measured hot-query speedup and 6.342x
measured benchmark wall-time speedup over RTDL Embree. V3 release
authorization remains false.
```

Forbidden:

```text
Do not claim Triangle V3 is 347x faster end to end.
Do not claim RTDL reproduces the RT-Graph paper.
Do not claim RTDL accelerates graph databases.
Do not claim M113 graph capture is ready.
Do not claim automatic partner selection is authorized.
Do not claim Triangle automatically selects the best partner.
Do not claim any Triangle row beyond `prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream` is M7-qualified.
```
