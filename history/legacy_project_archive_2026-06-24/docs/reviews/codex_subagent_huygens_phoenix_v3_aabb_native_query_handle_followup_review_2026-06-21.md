# Huygens Follow-Up Review: Phoenix V3 AABB Native Query-Handle

Reviewer: Codex subagent `Huygens`

Status: `block_m7_promotion_raw_oracle_and_stability_closed`

## Verdict

Still block M7 promotion.

The new evidence materially improves the candidate and closes the raw-oracle
and stability gaps, but the gate itself correctly remains
`aabb_native_query_handle_review_blocked_not_m7`.

## Closed Blockers

Raw AABB oracle is adequately closed:

- `docs/rebuild/v3/phoenix_v3_aabb_raw_oracle_evidence_2026-06-21.json`
- Raw generic `AABB_INDEX_QUERY_2D range_intersection_rows` is checked against
  an independent CPU oracle for Embree and OptiX.
- Fixtures include mixed overlaps, zero-overlap, closed-boundary touch,
  duplicate-prone boxes, dense many-to-many rows, and OptiX fail-closed
  overflow.

Fresh-run stability is adequately closed:

- `docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_stability_evidence_2026-06-21.json`
- Six fresh runs, three per scale.
- Weakest cold-plus-collect speedup: `1.644x`, above the `1.20x` floor.

Source provenance is acceptable for candidate-gate closure:

- Source manifest SHA is present.
- This satisfies the source/build digest fallback in the review gate.
- Caveat: `git_head` is still `fatal: not a git repository`, and no binary
  artifact digest is recorded, so this must not bypass review.

## Remaining Blockers

- External/2-AI review is still missing.
- Stable promoted row materialization is still missing:
  `stable_candidate_row_id_missing`.
- Public wording review is still missing.
- `m7_qualified_release_rows_added` remains `0`.
- Broad/public/release flags remain false.

## Allowed Wording

Internal/candidate-only wording is allowed:

> Phoenix V3 has candidate evidence that OptiX `AABB_INDEX_QUERY_2D
> range_intersection_rows` can reuse prepared native box-query handles for
> generic AABB candidate streaming. Raw AABB oracle and fresh-run stability
> blockers are now addressed, but M7 promotion and public speedup wording remain
> blocked pending external/2-AI review, stable row ID, and wording review.

No public speedup wording is allowed yet.

## Forbidden Wording

- M7-qualified.
- Release-ready.
- Public speedup.
- V3-over-V2 speedup.
- Contact Manifold solver speedup.
- Full contact acceleration.
- Broad AABB-index acceleration.
- Spatial-index acceleration.
- Any claim that a new AABB native-query-handle row has been promoted.

## Required Next Action

Obtain a real external review, then a Codex consensus response. Create a stable
candidate row ID and a row-scoped public wording packet. Keep broad, public, and
release flags false unless the final reviewed row explicitly authorizes only
row-scoped wording.

## Goal-Level Decision Audit

1. Was I foolish? No. I asked for a follow-up review after adding raw oracle and
   stability evidence, and accepted that the result is still not M7.
2. If yes, what actions made the decision foolish? It would be foolish to count
   a subagent follow-up as a real external review or to promote without stable
   row materialization.
3. Was there another path? Yes. I could continue RTNN or Spatial work, but that
   would leave the closest AABB candidate with partially closed review evidence.
4. Can I now try a different path? Yes. Keep the AABB candidate blocked, create
   a stable-row review packet only after true external review is available, and
   continue other generic engine work without broad release claims.
