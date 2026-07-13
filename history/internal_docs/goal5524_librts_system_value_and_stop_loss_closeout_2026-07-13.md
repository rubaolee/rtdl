# Goal5524 LibRTS System-Value and Stop-Loss Closeout

Status: `implemented__scoped_correctness_and_system_extraction_complete__review_pending`

## Conclusion

The LibRTS paper app has reached its useful completion boundary:

- exact point-contains count matrix: **14/14 matches**;
- exact range-contains count matrix: **14/14 matches**;
- exact range-intersects: 14 matches, 2 author CUDA capacity failures, 26
  explicitly uncheckpointed pairs;
- representative PIP relation gate: **71,626 canonical pair rows equal**;
- bounded mutation sequence: author and RTDL both `[2,1,0,1,0]`.

This supports `LibRTS scoped correctness and system extraction complete`. It
does not support full all-dataset/all-figure paper reproduction or performance
parity.

## What RTDL gained

LibRTS pressured the system into reusable, app-neutral capabilities:

1. public AABB column front doors and prepared count operations;
2. a generic mutable AABB index with stable IDs;
3. native fixed-cardinality and sparse-slot OptiX refit;
4. rollback recovery and persistent fail-closed invalidation tests;
5. operation-scoped packed-AABB validity semantics;
6. prepared-column/batch reuse contracts.

No core API contains LibRTS/paper identity. Archive/WKT/cache/comparator work
remains in the app.

## Stop-loss decision

Do not enumerate the remaining 26 range-intersects combinations merely to turn
ledger cells green. Fourteen exact count matches already cover three query
selectivity families, the observed semantic disagreements were resolved by a
generic validity fix, and two large parks cases establish the author capacity
boundary. More rows produce no new generic capability and no new semantic
answer.

Keep all 26 entries visibly `not_checkpointed`. Reopen only for a new semantic
disagreement, an explicitly authorized denominator-aligned paper figure, or a
new generic capability with a non-LibRTS consumer.

## Forbidden summaries

Do not call this full LibRTS paper reproduction, Figure 6 reproduction,
performance parity, author algorithm equivalence, complete range-intersects
coverage, pointwise equality for the count-only cases, zero-copy, or Embree
support.
