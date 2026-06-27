# Phoenix V3 Triangle Prepared-Graph 80000 M7 Final Review Packet

Status: `triangle_prepared_graph_chunk_80000_m7_qualified_row_scoped`.

This packet closes one exact Triangle prepared-graph row as row-scoped
M7-qualified after second-AI fallback review, P1 wording fixes, and Codex
consensus. It does not authorize V3 release wording.

## Bottom Line

```text
release_authorized: false
public_speedup_claim_authorized: false
row_scoped_public_speedup_claim_authorized: true
whole_app_speedup_claim_authorized: false
paper_reproduction_claim_authorized: false
graph_database_claim_authorized: false
m113_graph_capture_claim_authorized: false
m7_promotion_authorized: true
Phoenix M7-qualified release rows: 1
current_packet_external_review_status: claude_reviewed_approved_with_amendments_2026-06-21
current_packet_2ai_consensus_status: claude_codex_consensus_complete
```

The proposed row is:

```text
prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream
```

Source comparison group:

```text
triangle_count_rt_graph_2a1_cliques_80000
```

## Why This Packet Exists

The earlier Triangle intake was correctly closed as internal candidate evidence
only because it mixed three different issues:

- synthetic K4 clique-ladder scope;
- hot-query versus wall-time interpretation;
- prepared-graph executor linkage.

The first two can be handled by exact row-scoped wording. The third cannot be
handled by pretending M113 graph capture works. The narrower evidence is:

```text
Goal4531: generic prepared ray-batch weighted-summary device-output stream
executor validated.

Goal4540: Triangle current target is closed only through non-graph stream
continuation; M113 graph capture remains blocked.
```

This packet therefore asks for review of a narrower claim: a synthetic
non-graph device-output stream prepared-chunk row, not graph-capture readiness.
It is not graph database acceleration.
It is not RT-Graph paper reproduction.

## Evidence

Primary row:

| Field | Value |
| --- | ---: |
| Workload | Generated K4 clique ladder, 80,000 cliques |
| Oracle triangle count | 320,000 |
| Same contract | `rt_graph_2a1_mapped_to_generic_ray_triangle_any_hit` |
| Embree query median | 547.887 ms |
| OptiX query median | 1.578 ms |
| Hot OptiX / Embree | 347.232x |
| Embree wall | 15.792 s |
| OptiX wall | 2.490 s |
| Wall OptiX / Embree | 6.342x |
| Oracle match | true |
| Phase timing accept | true |
| OptiX RT-core / Embree non-RT-core | true |

Supporting row, not proposed for promotion:

| Field | Value |
| --- | ---: |
| Workload | Generated K4 clique ladder, 20,000 cliques |
| Oracle triangle count | 80,000 |
| Hot OptiX / Embree | 116.060x |
| Wall OptiX / Embree | 1.677x |
| Promotion status | supporting evidence only, not M7 |

## Executor Boundary

The old intake blocker was:

```text
prepared_graph_chunk_executor_linkage_not_closed
```

This packet resolves only the non-graph stream half:

```text
closed only for non-graph device-output stream continuation by Goal4531 and
Goal4540; M113 graph capture remains blocked
```

That means any approved wording must say `non-graph stream` or equivalent. It
must not say graph capture, CUDA graph replay, M113 readiness, graph compiler,
or universal prepared graph execution.

## Promotion Closure

Closed promotion conditions:

- `claude_external_review_completed_2026-06-21`
- `p1_wording_fixes_applied`
- `codex_consensus_recorded`
- `exact_row_scope_only`

Remaining non-release boundaries:

- not V3 release authorization;
- not global public speedup authorization;
- not RT-Graph paper reproduction;
- not graph database acceleration;
- not full Triangle app speedup;
- not M113 graph-capture readiness;
- not automatic partner selection;
- not broad V3-over-V2 speedup;
- not any Triangle row beyond the exact 80,000-clique row.

## Draft Row-Scoped Public Wording

```text
For the generated K4 clique-ladder synthetic RT-Graph 2A1 weighted-any-hit
contract on an NVIDIA RTX 4000 Ada Generation pod, exactly
`prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream` shows RTDL
OptiX 347.232x faster than RTDL Embree for the measured hot-query median and
6.342x faster for the measured benchmark wall-time median for this exact row.
Both routes match the 320,000-triangle oracle. This is a synthetic non-graph
device-output stream prepared-chunk row; it is not RT-Graph paper
reproduction, graph-database acceleration, M113 graph-capture readiness, full
Triangle app speedup, automatic partner selection, or broad V3-over-V2
speedup.
```

## Forbidden Wording

```text
Do not claim Triangle V3 is 347x faster end to end.
Do not claim RTDL reproduces the RT-Graph paper.
Do not claim RTDL accelerates graph databases.
Do not claim prepared_graph_chunk executor linkage is fully closed.
Do not claim M113 graph capture is ready for Triangle.
Do not claim any Triangle row other than the exact 80,000-clique non-graph stream row is M7-qualified.
Do not claim Triangle automatically selects the best partner.
Do not claim V3 is broadly faster than V2 because of Triangle.
```

## Current Review

The current packet now has a Claude external review:

```text
docs/reviews/claude_phoenix_v3_triangle_prepared_graph_80000_m7_refresh_review_2026-06-21.md
verdict: approve with amendments
P0 findings: none on evidence
P1 status/review hygiene fixes: applied
```

Codex consensus:

```text
docs/reviews/codex_phoenix_v3_triangle_prepared_graph_80000_m7_final_review_packet_2ai_consensus_2026-06-21.md
status: exact Triangle row promoted to row-scoped M7-qualified wording
```

The P1 fixes add automatic-partner-selection non-claims, replace `measured wall
path` with `measured benchmark wall-time median for this exact row`, keep
347.232x hot-query wording paired with 6.342x wall-time wording, and frame
RT-Graph 2A1 as the synthetic contract name, not paper reproduction.

## Sources

```text
docs/rebuild/v3/phoenix_v3_triangle_prepared_graph_intake_2026-06-20.md
docs/rebuild/v3/phoenix_v3_triangle_prepared_graph_tutorial_candidate_2026-06-21.md
docs/rebuild/v3/evidence/phoenix_v3_triangle_prepared_graph_20260620/triangle_prepared_graph_intake_summary.json
docs/reports/goal4531_v3_0_m134_triangle_weighted_replay_graph_capture_2026-06-17.md
docs/reports/goal4540_v3_0_m141_triangle_non_graph_stream_closure_gate_2026-06-17.md
docs/reviews/codex_phoenix_v3_triangle_prepared_graph_intake_2ai_consensus_2026-06-20.md
docs/reviews/codex_subagent_phoenix_v3_triangle_prepared_graph_80000_m7_final_review_packet_review_2026-06-21.md
docs/reviews/claude_phoenix_v3_triangle_prepared_graph_80000_m7_refresh_review_2026-06-21.md
docs/reviews/codex_phoenix_v3_triangle_prepared_graph_80000_m7_final_review_packet_2ai_consensus_2026-06-21.md
```

## Goal-Level Decision Audit

Decision: promote only the exact 80,000-clique non-graph stream row to
row-scoped M7-qualified status.

1. Was I foolish?

   No. The old blocker was too broad: M113 graph capture remains blocked, but
   Goal4531 and Goal4540 provide a narrower non-graph device-output stream
   executor closure that can be reviewed honestly.

2. If yes, what actions made the decision foolish?

   It would be foolish to call this a graph compiler, RT-Graph paper result,
   graph database accelerator, or 347x end-to-end Triangle speedup.

3. Was there another path?

   Yes. Keep Triangle tutorial-only forever, or promote the old intake
   directly. The first wastes valid executor evidence; the second skips the
   exact non-claim boundary.

4. Can I now try a different path that actually solves the problem?

   Yes. Keep the promotion exact-row scoped, record the fallback review
   transparently, and keep release/global claims false.
