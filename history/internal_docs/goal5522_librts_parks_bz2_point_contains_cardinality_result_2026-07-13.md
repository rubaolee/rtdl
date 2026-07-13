# Goal5522 LibRTS Parks.bz2 Point-Contains Cardinality Matrix

Status: `implemented__five_exact_count_matches__point_contains_10_of_14__review_pending`

## Objective

Reuse the exact parks.bz2 prepared artifacts from Goal5521 to checkpoint every
available point-contains query cardinality without redoing the 8.3 GiB WKT
geometry preparation.

## Result

| Query rows | Author | RTDL | Pinned author log |
|---:|---:|---:|---:|
| 50,000 | 56,428 | 56,428 | 56,428 |
| 100,000 | 112,729 | 112,729 | 112,729 |
| 200,000 | 225,699 | 225,699 | 225,699 |
| 400,000 | 451,007 | 451,007 | 451,007 |
| 800,000 | 901,103 | 901,103 | 901,103 |

All five query hashes are distinct, and every completed cardinality has an
independent checkpoint. The existing 100K row was already part of the
Goals5481-5484 exact six-case matrix, so Goal5522 adds four unique inventory
matches and moves coverage from 6/14 to 10/14.

## Ownership

The incremental archive extraction and WKT-derived cache remain in the paper
app. RTDL receives the neutral cached AABB columns, prepares one generic AABB
index, and applies `prepared.count(operation="point_contains")` to five point
query batches. No LibRTS/paper primitive was added to RTDL core.

This is count-level evidence, not pointwise relation equality, performance,
Figure 6, full-paper reproduction, author algorithm equivalence, zero-copy, or
Embree work.
