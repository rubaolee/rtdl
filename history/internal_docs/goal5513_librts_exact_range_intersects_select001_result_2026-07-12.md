# Goal5513 LibRTS Exact `select_0.01` Range-Intersects Batch

Status: `implemented__four_of_four_checkpointed_count_matches__review_pending`

## Objective

Run a second selectivity family through the pinned author binary and the
generic RTDL AABB columnar front door. The batch uses independent per-case
checkpoints and a temporary serialize path where the POD workspace quota
would otherwise produce an author output-stream error.

## Input provenance

The four query files are members of the MD5-verified `PPoPPAE-v2.tar.gz`
archive (`89e589f086038f1cd3af9e3ed67da8c8`). Geometry members are reused from
the verified Goal5500 extraction. The query family is:

```text
range-intersects_select_0.01_queries_10000
```

The extraction manifest and per-case JSONs record SHA-256 identity. The
workspace output quota path produced an author output-stream error on the
first parks_Europe invocation; rerunning the same case with `/tmp` serialize
storage completed successfully. This is an environment workaround, not an
algorithmic change.

## Runtime results

| Case | Geometry count | Query count | Author count | RTDL count | Result |
|---|---:|---:|---:|---:|---|
| parks_Europe | 1,856,318 | 10,000 | 216,977,211 | 216,977,211 | match |
| dtl_cnty | 12,234 | 10,000 | 1,570,285 | 1,570,285 | match |
| USACensusBlockGroupBoundaries | 248,954 | 10,000 | 33,404,355 | 33,404,355 | match |
| USADetailedWaterBodies | 463,595 | 10,000 | 55,205,607 | 55,205,607 | match |

The gate is:

```text
Paper-reproduction-apps/librts-paper/results/goal5513_exact_range_intersects_select001_gate.json
```

## Phase accounting and boundary

Author internal query time, RTDL WKT loading, index preparation, and prepared
query time remain separate. No performance ratio is authorized. The standard
author binary exposes counts rather than pair rows for this operation, so the
result is count-level only.

This goal does not claim a complete 42-pair archive matrix, pairwise relation
equality, Figure 6 reproduction, full-paper reproduction, author algorithm
equivalence, performance parity, zero-copy, or Embree evidence. Remaining
exact archive pairs are separate work.
