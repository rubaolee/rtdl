# Huygens Review: Phoenix V3 AABB Native Query-Handle Evidence

Reviewer: Codex subagent `Huygens`

Status: `blocked_as_is`

## Verdict

Reject/block promotion as-is. The AABB native query-handle packet is a strong
M7 candidate, but the current `.md`/`.json` evidence is not sufficient to
promote a row.

## P0 Blockers

1. No completed external/2-AI gate. The packet still keeps
   `m7_promotion_authorized=false`.
2. The current "CPU reference" is not same-contract enough for generic AABB row
   promotion. It validates Contact Manifold final witness rows after exact
   refinement, not raw `range_intersection_rows` against an independent AABB CPU
   oracle.
3. Remote provenance is weak. The POD summary reports `git_head` as
   `fatal: not a git repository`, so the release row is not tied to immutable
   source revision/build evidence.
4. The promoted row is not formally materialized: no stable promoted
   `candidate_row_id`, `m7_qualified_release_rows_added=0`, and the packet still
   says promotion is pending review.

## P1/P2 Improvements

- The implementation path does look generic, not app-specific:
  - `OptixAabbIndex2D.intersection_rows` reuses cached native query handles.
  - `collect_range_intersection_rows_prepared_queries` calls the packed-query
    native symbol.
  - The C++ symbol is app-name-free.
- Add run-to-run stability, not only repeated queries inside one run.
- Add non-one-to-one raw AABB fixtures with multiple overlaps, zero overlaps,
  duplicate-prone overlaps, and capacity pressure.

## Allowed Wording

None yet, because promotion is blocked.

After P0 closure, safe wording would be row-scoped:

> On an NVIDIA RTX 4000 Ada Generation pod, RTDL's OptiX route for the generic
> `AABB_INDEX_QUERY_2D` prepared-session `range_intersection_rows` candidate
> stream reused prepared native box-query handles and was 1.719x faster than
> the RTDL Embree route at 32,768 indexed/query AABBs and 1.637x faster at
> 65,536 indexed/query AABBs for cold-plus-collect wall time on the jittered-grid
> evidence fixture. This is row-scoped evidence for generic AABB candidate
> streaming only; Contact Manifold is only the harness. It is not a full Contact
> Manifold solver speedup, not broad AABB-index acceleration, and not a V3-over-V2
> speedup claim.

## Forbidden Wording

- Contact Manifold is accelerated.
- Full contact solver speedup.
- V3 is faster than V2.
- Broad AABB-index acceleration.
- LibRTS/spatial-index acceleration.
- All AABB workloads are M7.
- Full broadphase acceleration.
- CPU-reference-proven generic AABB rows, until the raw AABB oracle exists.

## Required Gates

Promotion must fail unless:

- Raw Embree/OptiX `range_intersection_rows` match an independent CPU AABB oracle.
- Remote `git_head` or source/build digest is present.
- External review/consensus is recorded.
- A stable row id exists.
- Broad/public flags stay false except explicit row-scoped wording.
- Cold-plus-collect wall remains above the material floor across repeated fresh
  runs.

## Goal-Level Decision Audit

1. Was I foolish? No. I asked for review before promotion and accepted the block
   rather than overriding it.
2. If yes, what made it foolish? It would be foolish to treat Contact Manifold
   witness correctness as raw generic AABB correctness or to promote without
   provenance.
3. Was there another path? Continue RTNN ingestion work. That would avoid this
   blocker but leave the closest AABB M7 candidate unresolved.
4. Can I try a different path now? Yes. Add a raw AABB oracle gate and provenance
   requirements before any M7 promotion.
