# Call For Review: Phoenix V3 AABB Native Query-Handle Final M7 Review

Reviewer: Claude or Gemini external AI.

Please critically review whether Phoenix V3 may promote exactly two
row-scoped M7 candidate rows for the reusable generic
`aabb_candidate_stream` capability.

## Review Target

Primary packets:

- `docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_evidence_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_aabb_raw_oracle_evidence_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_stability_evidence_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_row_wording_gate_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_review_gate_2026-06-21.md`

Machine-readable versions with the same basenames also exist as `.json`.

## Candidate Rows

Generic primitive:

- `AABB_INDEX_QUERY_2D`
- operation: `range_intersection_rows`
- contract: generic prepared AABB index query with native query-handle reuse
- evidence harness: Contact Manifold only; this must not become a Contact
  Manifold solver claim.

Stable candidate row IDs:

- `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50`
- `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50`

Material evidence on RTX 4000 Ada:

- 32,768 AABBs and 32,768 packed box queries, jittered_grid, warmup=3,
  repeat=50:
  - OptiX/Embree cold-plus-collect wall speedup: `1.719x`
  - OptiX/Embree query_total speedup: `1.867x`
  - OptiX prepare remains slower than Embree, so prepare-only wording is
    forbidden.
- 65,536 AABBs and 65,536 packed box queries, jittered_grid, warmup=3,
  repeat=50:
  - OptiX/Embree cold-plus-collect wall speedup: `1.637x`
  - OptiX/Embree query_total speedup: `1.743x`
  - OptiX prepare remains slower than Embree, so prepare-only wording is
    forbidden.

Stability:

- Six fresh POD runs across the two scales preserve the material floor.
- Weakest fresh cold-plus-collect wall speedup: `1.644x`.
- The declared material floor is `1.20x`.

Correctness and provenance:

- Raw Embree/OptiX `range_intersection_rows` matched an independent
  closed-boundary CPU AABB oracle on duplicate-prone, zero-overlap,
  edge-touch, and dense many-to-many fixtures.
- OptiX low-capacity overflow was observed as fail-closed.
- Source-manifest provenance is recorded with SHA-256:
  `f7d8a0ae6e39c691bf7c949b23741181abcc24fc3e3ef405f73c7a113d1e4422`.
- Stable candidate row IDs and draft wording are present.

Current gate status:

- `m7_promotion_authorized: false`
- `m7_qualified_release_rows_added: 0`
- `release_authorized: false`
- `public_speedup_claim_authorized: false`
- `broad_v3_faster_than_v2_claim_authorized: false`
- Remaining blockers before this review:
  `external_ai_review_missing`,
  `codex_consensus_response_missing_after_external_review`, and
  `external_public_wording_review_missing`.

## Questions

Please answer these directly:

1. Is the candidate genuinely a reusable generic engine capability
   (`aabb_candidate_stream`) rather than a Contact Manifold-specific native
   shortcut?
2. Are OptiX and Embree same-contract enough for the two exact row-scoped M7
   comparisons?
3. Are the two serious rows, six fresh-run stability samples, independent raw
   AABB oracle, source manifest, and fail-closed overflow behavior sufficient
   to promote the two stable row IDs to M7?
4. Does the draft wording properly avoid hiding slower OptiX prepare/collect
   phases?
5. What exact public wording may be used if you approve?
6. What exact public wording must remain forbidden?
7. Are any P0/P1 blockers still open before M7 promotion?
8. Is this approval only row-scoped, with aggregate V3 release authorization
   still blocked?

## Non-Negotiable Boundaries

Do not approve:

- broad V3-over-V2 speedup wording
- full Contact Manifold solver speedup
- broad AABB-index acceleration
- all-benchmark-app acceleration
- physics throughput claims
- release-ready wording
- paper/authors-code reproduction wording
- OptiX prepare-phase speedup wording

If approved, the approval must be limited to the exact two stable candidate row
IDs above and must keep aggregate Phoenix V3 release authorization false.

## Requested Output

Please write a concise but critical review with:

- Verdict: `approve`, `approve-with-conditions`, or `reject`.
- P0 blockers.
- P1 blockers or wording fixes.
- Allowed wording.
- Forbidden wording.
- A final statement saying whether the two rows may be promoted to M7, and
  whether aggregate V3 release remains blocked.

## Goal-Level Decision Self-Audit

Decision: request a final external review for the AABB native-query-handle
candidate after local raw-oracle, provenance, stability, and row-ID gates are
closed.

1. Was I foolish?
   No. This is the current closest reusable V3 engine candidate with material
   wall-speed evidence and local blocker closure.
2. If yes, what actions made the decision foolish?
   Not applicable. The foolish action would be to promote the rows without
   external review or to broaden them into Contact Manifold or V3-over-V2
   claims.
3. Was there another path that would have avoided getting stuck on one idea?
   Yes. Continue RTNN ingestion or Barnes-Hut vector accumulation work. Those
   remain important, but AABB is currently closest to a reviewable M7 row.
4. Can I now try a different path that actually solves the problem?
   Yes. If this review blocks or cannot be obtained, keep AABB not-M7 and move
   to the next generic engine queue item without weakening review discipline.
