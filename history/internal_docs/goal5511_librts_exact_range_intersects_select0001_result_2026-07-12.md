# Goal5511 LibRTS Exact `select_0.001` Range-Intersects Batch

Status: `implemented__four_of_four_checkpointed_count_matches__review_pending`

## Objective

Run a second exact archive query family through the pinned LibRTS author binary
and the generic RTDL AABB columnar front door. Each case must be independently
checkpointed so a later process termination cannot erase completed evidence.

## Input provenance

The four query files were extracted from the MD5-verified `PPoPPAE-v2.tar.gz`
archive (`89e589f086038f1cd3af9e3ed67da8c8`). Geometry members were reused
from the verified Goal5500 extraction. The query family is:

```text
range-intersects_select_0.001_queries_10000
```

The per-case JSON records include geometry/query SHA-256 values and assert
that the same files were passed to the author and RTDL. The extraction
manifest is:

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5511_range_intersects_batch_extraction.json
```

## Runtime results

| Case | Geometry count | Query count | Author count | RTDL count | Result |
|---|---:|---:|---:|---:|---|
| parks_Europe | 1,856,318 | 10,000 | 23,962,096 | 23,962,096 | match |
| dtl_cnty | 12,234 | 10,000 | 239,884 | 239,884 | match |
| USACensusBlockGroupBoundaries | 248,954 | 10,000 | 3,478,660 | 3,478,660 | match |
| USADetailedWaterBodies | 463,595 | 10,000 | 6,436,810 | 6,436,810 | match |

The four independent checkpoints are:

```text
results/goal5511_parks_Europe_select_0.001_10000.json
results/goal5511_dtl_cnty_select_0.001_10000.json
results/goal5511_USACensusBlockGroupBoundaries_select_0.001_10000.json
results/goal5511_USADetailedWaterBodies_select_0.001_10000.json
```

The RTDL route uses the generic public contract
`Aabb2DColumns + prepare_aabb_index_2d_columns + prepared.count` and the
Goal5508 native library. No LibRTS-specific primitive or behavior was added
to RTDL core for this goal.

## Phase accounting

The records keep author internal query time, RTDL WKT loading, RTDL index
preparation, and RTDL prepared query time in separate fields. They do not
share a denominator or a runtime regime, so this goal authorizes no
author-vs-RTDL performance ratio. The large RTDL load times are retained as
evidence; they are not hidden by reporting only prepared query time.

## Claim boundary

This goal establishes four exact-archive, same-input, count-level matches for
one query family. It does not establish pointwise intersection relation
equality because the standard author binary does not expose pair rows for
this operation. It does not claim a complete 42-pair matrix, Figure 6
reproduction, full paper reproduction, author algorithm equivalence,
performance parity, zero-copy, or Embree evidence.

The result gate is:

```text
Paper-reproduction-apps/librts-paper/results/goal5511_exact_range_intersects_select0001_gate.json
```

Remaining exact archive pairs and the two unresolved Goal5509 large cases
remain separate work. Missing checkpoints are not treated as semantic
mismatches or as matches.
