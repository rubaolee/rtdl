# Codex Consensus: Phoenix V3 AABB Native Query-Handle Final M7 Review

Status: `claude_codex_consensus_complete_approve_two_row_scoped_m7_rows`.

This is the Codex consensus response to the external Claude review:

- `docs/reviews/claude_phoenix_v3_aabb_native_query_handle_final_m7_review_2026-06-21.md`
- Raw Claude stream log:
  `docs/reviews/claude_phoenix_v3_aabb_native_query_handle_final_m7_review_2026-06-21.stream.jsonl`
- Review request:
  `docs/reviews/call_for_review_phoenix_v3_aabb_native_query_handle_final_m7_review_2026-06-21.md`

## Decision

Codex accepts Claude's `approve-with-conditions` verdict and closes the sole
remaining P0 blocker, `codex_consensus_response_missing_after_external_review`.

Exactly two row-scoped M7 rows may now be counted for the reusable generic
`aabb_candidate_stream` capability:

- `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50`
- `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50`

This consensus does not authorize aggregate Phoenix V3 release, broad
V3-over-V2 wording, broad AABB-index wording, Contact Manifold solver wording,
physics throughput wording, or any prepare-phase speedup wording.

## Accepted Conditions

Claude's P1 conditions are accepted as mandatory promotion-record requirements:

- The promotion record must state that the POD source directory did not expose
  a git commit; provenance rests on SHA-256 source manifest
  `f7d8a0ae6e39c691bf7c949b23741181abcc24fc3e3ef405f73c7a113d1e4422`.
- Public row wording must include the prepare-phase disclosure:
  "OptiX prepare alone remains slower than Embree".

If either condition is omitted from the generated promotion packet, the packet
must fail its gate.

## Allowed Row-Scoped Wording

For
`aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50`:

On an NVIDIA RTX 4000 Ada Generation GPU, RTDL's OptiX native
prepared-query-handle route for `AABB_INDEX_QUERY_2D range_intersection_rows`
was `1.719x` faster than the RTDL Embree route on a jittered-grid workload with
32,768 AABBs and 32,768 packed box queries, measured as cold prepare plus
collect wall time with warmup=3 and repeat=50. Query total was `1.867x` faster.
OptiX prepare alone remains slower than Embree; the speedup applies to
end-to-end prepared-session time. This result is row-scoped and does not claim
Contact Manifold solver acceleration, broad AABB-index acceleration, or
V3-over-V2 speedup.

For
`aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50`:

On an NVIDIA RTX 4000 Ada Generation GPU, RTDL's OptiX native
prepared-query-handle route for `AABB_INDEX_QUERY_2D range_intersection_rows`
was `1.637x` faster than the RTDL Embree route on a jittered-grid workload with
65,536 AABBs and 65,536 packed box queries, measured as cold prepare plus
collect wall time with warmup=3 and repeat=50. Query total was `1.743x` faster.
OptiX prepare alone remains slower than Embree; the speedup applies to
end-to-end prepared-session time. This result is row-scoped and does not claim
Contact Manifold solver acceleration, broad AABB-index acceleration, or
V3-over-V2 speedup.

## Forbidden Wording

- V3 is faster than V2.
- Phoenix V3 is release-ready.
- Contact Manifold solver acceleration.
- Physics engine or collision solver throughput.
- Broad AABB-index acceleration.
- All `AABB_INDEX_QUERY_2D` operations are faster.
- OptiX prepare is faster than Embree prepare.
- Any hardware, scale, dataset, app, or operation outside the exact two row IDs.

## Release Boundary

Aggregate Phoenix V3 release authorization remains false. These two rows are
additional row-scoped M7 evidence only.

## Goal-Level Decision Self-Audit

Decision: accept Claude's AABB approve-with-conditions verdict, close the
Codex-consensus P0, and permit exactly two row-scoped AABB native-query-handle
M7 rows while keeping release and broad claims false.

1. Was I foolish?
   No. The external review was real this time, read the evidence files, and
   left only a Codex consensus step plus P1 wording/provenance conditions.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to ignore Claude's conditions,
   omit the slower-prepare disclosure, or turn these two rows into a Contact
   Manifold or broad V3 claim.
3. Was there another path that would have avoided getting stuck on one idea?
   Yes. I could leave AABB pending and continue RTNN, but that would waste a
   now-reviewed generic engine improvement with material wall evidence.
4. Can I now try a different path that actually solves the problem?
   Yes. Promote only the two scoped AABB rows through generated gates, update
   M7 classification/readiness counts, and keep V3 release blocked until the
   broader release blockers close.
