# Goal5517 LibRTS Exact Range-Contains Batch

Status: `implemented__four_exact_count_matches__review_pending`

## Objective

Extend the LibRTS exact-input reproduction from the single Goal5493
range-contains case to four independently checkpointed cases from the official
`range-contains_queries_100000` family.

## Input provenance

Eight members were extracted from the MD5-verified official archive
`PPoPPAE-v2.tar.gz` (`89e589f086038f1cd3af9e3ed67da8c8`). The first
destination under `/workspace` failed with `Disk quota exceeded`; extraction
was repeated under `/tmp` and atomically promoted there. This changes storage
location only. Every geometry and query has a recorded SHA-256, and the same
files were passed to author and RTDL.

## Results

| Case | Geometry rows | Query rows | Author count | RTDL count |
|---|---:|---:|---:|---:|
| parks_Europe | 1,856,318 | 100,000 | 104,426 | 104,426 |
| dtl_cnty | 12,234 | 100,000 | 117,314 | 117,314 |
| USACensusBlockGroupBoundaries | 248,954 | 100,000 | 120,457 | 120,457 |
| USADetailedWaterBodies | 463,595 | 100,000 | 112,637 | 112,637 |

RTDL uses the generic public route:

```python
prepared = prepare_aabb_index_2d_columns(boxes, backend="optix")
count = prepared.count(box_queries=queries, operation="range_contains")
```

No LibRTS-specific RTDL primitive or native behavior was added.

## Phase boundary

Author internal query time, RTDL WKT load, index preparation, and prepared
query wall remain separate fields. The current app front door is dominated by
Python WKT parsing on large files; this is visible in the evidence and not
hidden behind prepared-query timing. No author/RTDL performance ratio is
authorized.

WKT parsing is app-owned and is not an RTDL system optimization target. RTDL's
responsibility begins at the generic column/buffer boundary represented here
by `Aabb2DColumns`.

## Claim boundary

This goal proves four exact-archive, same-input count matches. The author
binary exposes counts rather than relation rows, so pointwise containment
equivalence is not established. The full 14-pair range-contains inventory,
Figure 6, full paper reproduction, performance parity, zero-copy, author
algorithm equivalence, and Embree evidence remain closed.

Evidence:

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5517_range_contains_batch_extraction.json
Paper-reproduction-apps/librts-paper/results/goal5517_exact_range_contains_batch_gate.json
```
