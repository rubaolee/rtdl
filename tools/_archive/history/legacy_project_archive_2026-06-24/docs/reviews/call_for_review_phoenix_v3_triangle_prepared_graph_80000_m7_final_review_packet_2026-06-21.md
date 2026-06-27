# Call For Review: Phoenix V3 Triangle Prepared-Graph 80000 M7 Final Review Packet

Reviewer: Claude, Gemini, or another independent AI reviewer.

Project: RTDL Phoenix V3 rebuild.

## Review Target

Please critically review this V3-only final public-row review packet:

```text
docs/rebuild/v3/phoenix_v3_triangle_prepared_graph_80000_m7_final_review_packet_2026-06-21.md
docs/rebuild/v3/phoenix_v3_triangle_prepared_graph_80000_m7_final_review_packet_2026-06-21.json
tutorials/current/10_triangle_prepared_graph_chunk.md
```

Evidence sources:

```text
docs/rebuild/v3/phoenix_v3_triangle_prepared_graph_intake_2026-06-20.md
docs/rebuild/v3/phoenix_v3_triangle_prepared_graph_tutorial_candidate_2026-06-21.md
docs/rebuild/v3/evidence/phoenix_v3_triangle_prepared_graph_20260620/triangle_prepared_graph_intake_summary.json
docs/reports/goal4531_v3_0_m134_triangle_weighted_replay_graph_capture_2026-06-17.md
docs/reports/goal4540_v3_0_m141_triangle_non_graph_stream_closure_gate_2026-06-17.md
docs/reviews/codex_phoenix_v3_triangle_prepared_graph_intake_2ai_consensus_2026-06-20.md
```

## Proposed Decision

Approve exactly this row as M7-qualified row-scoped public wording, or reject it
if the non-graph stream executor boundary is not release-grade:

```text
prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream
```

Key facts:

- generic capability: `prepared_graph_chunk`;
- source row: `triangle_count_rt_graph_2a1_cliques_80000`;
- workload: generated K4 clique ladder, 80,000 cliques;
- oracle triangle count: 320,000;
- same contract: `rt_graph_2a1_mapped_to_generic_ray_triangle_any_hit`;
- hot OptiX/Embree: 347.232x;
- wall OptiX/Embree: 6.342x;
- both routes match oracle;
- Goal4531 validates a generic prepared ray-batch weighted-summary
  device-output stream executor;
- Goal4540 closes Triangle only as non-graph stream continuation;
- M113 graph capture remains blocked;
- not RT-Graph paper reproduction;
- not graph database acceleration;
- not full Triangle app speedup;
- not V3-over-V2 wording.

## Questions For The Reviewer

1. Does Goal4531 plus Goal4540 adequately resolve the old
   `prepared_graph_chunk_executor_linkage_not_closed` blocker if the approved
   wording says `non-graph stream` and explicitly forbids M113 graph capture?
2. Is synthetic K4 clique-ladder scope acceptable for row-scoped M7 wording if
   explicitly named as synthetic and not paper/graph-database evidence?
3. Is the 347.232x hot-query ratio safe to publish beside the 6.342x wall ratio,
   or is it still too easy to misread as end-to-end speedup?
4. Should only the 80,000-clique row become M7-qualified, with the 20,000-clique
   row staying supporting evidence only?
5. What P0 wording or evidence fixes are required before promotion, if any?

## Required Review Style

Please be strict. Reject if the packet makes the row sound like graph-capture
readiness, RT-Graph paper reproduction, graph database acceleration, full
Triangle app speedup, automatic partner selection, or broad V3-over-V2 speedup.

If you approve, list any P0 wording changes required before promotion.
