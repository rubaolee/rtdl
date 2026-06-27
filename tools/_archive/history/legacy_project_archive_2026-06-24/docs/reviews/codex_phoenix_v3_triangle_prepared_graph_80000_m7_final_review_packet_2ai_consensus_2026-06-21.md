# Codex 2-AI Consensus: Phoenix V3 Triangle Prepared-Graph 80000 M7 Final Review Packet

Date: 2026-06-21

Status: exact Triangle 80,000-clique non-graph stream row promoted to
row-scoped M7-qualified wording after second-AI fallback review and P1 fixes.

This is not Claude/Gemini consensus. Local Claude/Gemini CLI access was not
available from this environment, so the second review was performed by a Codex
subagent and is recorded explicitly as such.

## Inputs

Final review candidate:

```text
docs/rebuild/v3/phoenix_v3_triangle_prepared_graph_80000_m7_final_review_packet_2026-06-21.md
docs/rebuild/v3/phoenix_v3_triangle_prepared_graph_80000_m7_final_review_packet_2026-06-21.json
```

Review request:

```text
docs/reviews/call_for_review_phoenix_v3_triangle_prepared_graph_80000_m7_final_review_packet_2026-06-21.md
```

Second-AI fallback review:

```text
docs/reviews/codex_subagent_phoenix_v3_triangle_prepared_graph_80000_m7_final_review_packet_review_2026-06-21.md
verdict: approve with required wording fixes
P0 findings: none on evidence
P1 wording fixes: applied
```

Source evidence:

```text
docs/rebuild/v3/phoenix_v3_triangle_prepared_graph_intake_2026-06-20.md
docs/rebuild/v3/phoenix_v3_triangle_prepared_graph_tutorial_candidate_2026-06-21.md
docs/rebuild/v3/evidence/phoenix_v3_triangle_prepared_graph_20260620/triangle_prepared_graph_intake_summary.json
docs/reports/goal4531_v3_0_m134_triangle_weighted_replay_graph_capture_2026-06-17.md
docs/reports/goal4540_v3_0_m141_triangle_non_graph_stream_closure_gate_2026-06-17.md
```

## Consensus Decision

Promote exactly this row to M7-qualified row-scoped status:

```text
prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream
```

Approved wording must remain row-scoped and must pair the hot-query and
wall-time ratios:

```text
347.232x measured hot-query median and 6.342x measured benchmark wall-time
median for this exact row
```

## Accepted Facts

- The row is a generated K4 clique-ladder synthetic workload with 80,000
  cliques and 320,000 oracle triangles.
- The row uses the same
  `rt_graph_2a1_mapped_to_generic_ray_triangle_any_hit` contract through Embree
  and OptiX.
- Both routes match the 320,000-triangle oracle.
- OptiX is 347.232x faster than Embree for the measured hot-query median.
- OptiX is 6.342x faster than Embree for the measured benchmark wall-time
  median for this exact row.
- Goal4531 validates the narrower generic prepared ray-batch weighted-summary
  device-output stream executor.
- Goal4540 closes Triangle only through non-graph stream continuation.
- M113 CUDA graph capture remains blocked.

## Non-Claims

This promotion does not authorize:

- RT-Graph paper reproduction;
- graph database acceleration;
- full Triangle application speedup;
- end-to-end 347x speedup;
- M113 graph-capture readiness;
- automatic partner selection;
- broad V3-over-V2 speedup;
- the 20,000-clique supporting row;
- any Triangle row beyond
  `prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream`.

## Gate Result

Focused verification after applying review fixes:

```text
py -3 -m unittest tests.v3_phoenix_triangle_prepared_graph_80000_m7_final_review_packet_test tests.v3_release_wording_gate_test
Ran 6 tests
OK
```

The local Python installation prints `Could not find platform independent
libraries <prefix>` before these runs, but the command returns success and the
test bodies pass.

## Goal-Level Decision Audit

Decision: promote only the exact 80,000-clique synthetic non-graph stream
Triangle row to M7-qualified row-scoped status after second-AI fallback review.

1. Was I foolish?

   No. The decision is bounded to the row and contract the evidence actually
   supports, and the second reviewer found no evidence P0 after requiring
   wording fixes.

2. If yes, what actions made the decision foolish?

   It would be foolish to cite 347.232x without the 6.342x wall-time ratio, to
   imply graph capture readiness, or to generalize this to graph databases,
   RT-Graph paper reproduction, full Triangle speedup, automatic partner
   selection, or broad V3-over-V2 speedup.

3. Was there another path?

   Yes. Keep Triangle internal-only until Claude/Gemini is available, or promote
   it without second review. The first is more conservative but leaves a valid
   row unclassified; the second would repeat the old self-approval failure.

4. Can I now try a different path that actually solves the problem?

   Yes. Record the fallback review transparently, promote only the exact row,
   and keep release/global claims false until more rows close.
