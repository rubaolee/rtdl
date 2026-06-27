# Claude External Review - Phoenix V3 Triangle Prepared-Graph 80000 M7 Refresh

Reviewer: Claude, via Claude CLI.

Date: 2026-06-21.

Review type: external Claude review to close the Phoenix rule gap left by the
earlier Codex subagent fallback review.

## Verdict

Approve with amendments.

No P0 blockers found. P1 amendments are required before the packet status may
be upgraded from Codex-subagent fallback to Claude-reviewed closure.

## Evidence Reading

Claude found the evidence chain internally consistent:

| Field | Packet value | Evidence reading |
| --- | ---: | --- |
| Embree query median | 547.887 ms | matches evidence |
| OptiX query median | 1.578 ms | matches evidence |
| Hot OptiX/Embree ratio | 347.232x | matches evidence |
| Embree wall | 15.792 s | matches evidence |
| OptiX wall | 2.490 s | matches evidence |
| Wall OptiX/Embree ratio | 6.342x | matches evidence |
| Oracle triangles | 320,000 | matches evidence |

Both backends use the same
`rt_graph_2a1_mapped_to_generic_ray_triangle_any_hit` contract. The hot-query
metric is characterized as a post-warmup median. The phase contract remains
valid, and the OptiX RT-core versus Embree non-RT-core distinction is recorded.

## P0 Findings

None.

Claude found oracle match, phase timing, and RT-core distinction valid for the
exact row-scoped packet.

## P1 Required Amendments

1. Remove the duplicate `not automatic partner selection` entry from the JSON
   `non_claims` array.
2. Update JSON and Markdown review status fields from the Codex subagent
   fallback review to:
   `claude_reviewed_approved_with_amendments_2026-06-21`.
3. Update JSON and Markdown consensus fields to:
   `claude_codex_consensus_complete`.
4. Add a `claude_review` field pointing to this review file.
5. Replace the JSON closed promotion condition
   `second_ai_fallback_review_completed` with
   `claude_external_review_completed_2026-06-21`.

## P2 Recommended Amendments

1. Tighten the forbidden wording from "all Triangle rows are M7-qualified" to
   "any Triangle row other than the exact 80,000-clique non-graph stream row is
   M7-qualified".
2. Add the prior Codex Triangle intake consensus to the packet source list so
   the visible provenance chain is complete.

## Non-Claim Check

Claude confirmed that the packet correctly forbids:

- RT-Graph paper reproduction;
- graph database acceleration;
- M113 graph-capture readiness;
- full Triangle app speedup;
- automatic partner selection;
- broad V3-over-V2 speedup.

Claude also confirmed that the `347.232x` hot-query figure is correctly paired
with the `6.342x` benchmark wall-time figure.

## Final Recommendation

After the P1 amendments are applied, keep the exact row:

```text
prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream
```

as row-scoped M7-qualified.

Nothing beyond that exact row is authorized.
