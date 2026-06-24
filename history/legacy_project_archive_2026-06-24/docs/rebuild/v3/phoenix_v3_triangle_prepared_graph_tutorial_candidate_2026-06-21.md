# Phoenix V3 Triangle Prepared-Graph Tutorial Candidate

Status: `triangle_prepared_graph_tutorial_candidate_not_m7`.

This packet turns the reviewed Triangle prepared-graph intake into a V3 rebuild
tutorial candidate. It is not release evidence and not public speedup wording.

## Bottom Line

```text
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
paper_reproduction_claim_authorized: false
graph_database_claim_authorized: false
m7_promotion_authorized: false
Phoenix M7-qualified release rows: 0
current_packet_external_review_status: blocked_current_packet
```

The underlying intake already has Claude/Codex 2-AI consensus as reviewed
internal candidate evidence:

```text
docs/reviews/codex_phoenix_v3_triangle_prepared_graph_intake_2ai_consensus_2026-06-20.md
```

This new packet does not upgrade that status. It only makes the current teaching
surface explicit.

## What Users May Learn

Triangle is the clearest current V3 rebuild example of
`prepared_graph_chunk`: the same generated RT-Graph 2A1 contract is run through
Embree and OptiX, both rows match the triangle-count oracle, and the hot-query
OptiX path wins strongly.

The reusable engine idea is:

```text
prepared graph input -> repeated ray-triangle weighted-any-hit query -> compact
triangle summary
```

That is a useful RTDL programming shape. It is not yet a release row.

## Evidence

Source:

```text
docs/rebuild/v3/phoenix_v3_triangle_prepared_graph_intake_2026-06-20.md
docs/rebuild/v3/evidence/phoenix_v3_triangle_prepared_graph_20260620/triangle_prepared_graph_intake_summary.json
```

| Workload | Hot OptiX / Embree | Wall OptiX / Embree | Oracle triangles | Boundary |
| --- | ---: | ---: | ---: | --- |
| K4 clique ladder, 20,000 cliques | 116.060x | 1.677x | 80,000 | synthetic, not paper |
| K4 clique ladder, 80,000 cliques | 347.232x | 6.342x | 320,000 | synthetic, not paper |

The hot-query ratios are the reusable prepared-query signal. The wall ratios
are the release-safety correction. Both must be shown together.

## Current Blockers

- `synthetic_k4_clique_ladder_not_paper_dataset`
- `not_graph_database_or_full_triangle_counting_app`
- `no_author_code_or_paper_dataset_comparison`
- `prepared_graph_chunk_executor_linkage_not_closed`
- `hot_query_vs_wall_timing_ratio_not_characterized_for_release`
- `public_row_level_external_review_not_done`

## Allowed Wording

```text
Triangle prepared-graph chunk is a V3 rebuild tutorial candidate. On generated
K4 clique-ladder rows, the same RT-Graph 2A1 weighted-any-hit contract has
strong OptiX-over-Embree hot-query wins, while wall-time wins are smaller and
must stay visible.
```

## Forbidden Wording

```text
Do not claim Triangle V3 is 347x faster end to end.
Do not claim RTDL reproduces the RT-Graph paper.
Do not claim RTDL accelerates graph databases.
Do not claim prepared_graph_chunk executor linkage is closed.
Do not claim Triangle is M7-qualified.
```

## Tutorial

The current tutorial entry is:

```text
tutorials/current/10_triangle_prepared_graph_chunk.md
```

It is a rebuild tutorial, not a release tutorial.

## External Review

The underlying Triangle intake has prior Claude/Codex consensus. Fresh external
review of this tutorial-candidate packet is blocked:

```text
docs/reviews/external_review_blocked_phoenix_v3_triangle_prepared_graph_tutorial_candidate_2026-06-21.md
```

## Goal-Level Decision Audit

Decision: promote Triangle only to tutorial-grade internal candidate wording,
not M7.

1. Was I foolish?

   No. The underlying intake already has 2-AI internal-candidate consensus, and
   this packet keeps all release flags false.

2. If yes, what actions made the decision foolish?

   It would be foolish to turn the 116x and 347x hot-query ratios into
   end-to-end, paper, or graph-database claims.

3. Was there another path that avoided getting stuck on that idea?

   Yes. Rerun the pod or claim M7 immediately, but that would skip the
   synthetic-boundary and executor-linkage gaps.

4. Can I now try a different path that actually solves the problem?

   Yes. Teach the reusable prepared-graph chunk shape with exact hot and wall
   ratios while preserving all blockers.
