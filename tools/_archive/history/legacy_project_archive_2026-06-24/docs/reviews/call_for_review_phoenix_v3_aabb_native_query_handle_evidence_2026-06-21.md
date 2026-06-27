# Call For Review: Phoenix V3 AABB Native Query-Handle Evidence

Review target:

- `docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_evidence_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_evidence_2026-06-21.json`

Question:

Should Phoenix V3 promote a new row-scoped M7 claim for the generic
`aabb_candidate_stream` capability from the native prepared-query-handle
evidence?

Candidate summary:

- Generic change: OptiX AABB `range_intersection_rows` reuses prepared native
  box-query handles through
  `rtdl_optix_collect_prepared_aabb_index_2d_range_intersection_rows_packed_queries`.
- Evidence harness: Contact Manifold fixture only.
- Material wall-speedup floor: `1.20x`.
- RTX 4000 Ada POD rows:
  - 32,768 AABBs, repeat 50: `1.719x` cold-plus-collect wall vs Embree.
  - 65,536 AABBs, repeat 50: `1.637x` cold-plus-collect wall vs Embree.
- CPU reference: true for both rows.
- Complete candidate coverage: true for both rows.
- Native prepared-query cache observed: one miss and 52 hits for both rows.

Required review checks:

1. Is this actually a reusable generic engine capability, not a Contact
   Manifold-specific native shortcut?
2. Are the OptiX and Embree rows same-contract enough for a row-scoped M7
   comparison?
3. Are the two serious rows and the `1.20x` material floor sufficient?
4. Are correctness, overflow, coverage, and cache-lifetime checks strong
   enough?
5. Does any phase/wall wording hide the fact that OptiX prepare and collect
   are still slower than Embree on these rows?
6. What exact public wording is allowed?
7. What exact public wording must remain forbidden?
8. What tests or gates must be added before promotion?

Non-negotiable boundaries:

- Do not approve broad V3-over-V2 speedup wording.
- Do not approve full Contact Manifold solver speedup wording.
- Do not approve broad AABB-index acceleration wording.
- Do not approve all benchmark apps, physics throughput, or automatic backend
  selection wording.
- If approved, the result must remain row-scoped and release authorization
  must remain false unless the aggregate Phoenix release gate is separately
  closed.

Goal-level decision audit:

1. Was I foolish? No. AABB native query-handle is the current queue item closest
   to a legitimate new M7 row, so seeking review is the correct next step.
2. If yes, what made it foolish? It would be foolish to promote from this packet
   without review, to generalize from Contact Manifold, or to hide the slower
   prepare/collect phases.
3. Was there another path? Continue RTNN ingestion work. That remains useful,
   but the current AABB candidate is already evidence-complete enough to deserve
   review first.
4. Can I try a different path now? Yes. If review blocks promotion, return to
   generic engine overhead work rather than forcing the AABB row.
