# Goal5514 LibRTS Exact `select_0.01` Six-Geometry Resolution

Status: `implemented__five_exact_count_matches__one_author_cuda_capacity_failure__review_pending`

## Objective

Complete the six-geometry state for the exact
`range-intersects_select_0.01_queries_10000` family. Each case is resolved
independently as either a same-input count match or a clearly classified
author-side capacity failure.

## Results

| Case | Author status | RTDL status | Result |
|---|---|---|---|
| parks_Europe | `216,977,211` | `216,977,211` | count match |
| dtl_cnty | `1,570,285` | `1,570,285` | count match |
| USACensusBlockGroupBoundaries | `33,404,355` | `33,404,355` | count match |
| USADetailedWaterBodies | `55,205,607` | `55,205,607` | count match |
| lakes.bz2 | `1,113,229,623` | `1,113,229,623` | count match |
| parks.bz2 | CUDA `bad_alloc` | not run after author failure | author capacity failure |

The parks.bz2 failure is from the pinned author Thrust/CUDA allocation path.
It is not an author/RTDL semantic mismatch. The five matching cases use the
same extracted geometry/query files on both sides and carry per-case
SHA-256 identity. Large WKT runs use a temporary serialize directory where
the workspace quota path is known to produce output-stream errors.

## Claim boundary

This resolves all six geometry states for one exact query family, but it does
not complete the 42-pair range-intersects archive matrix. The standard author
binary exposes counts rather than pair rows for this operation, so no
pointwise relation equality is claimed. No Figure 6, full-paper reproduction,
performance ratio, author parity, zero-copy, author algorithm equivalence, or
Embree evidence is authorized.

Machine-readable evidence:

```text
Paper-reproduction-apps/librts-paper/results/goal5514_exact_range_intersects_select001_resolution_gate.json
Paper-reproduction-apps/librts-paper/results/goal5514_lakes_bz2_select_0.01_10000.json
Paper-reproduction-apps/librts-paper/results/goal5514_parks_bz2_select001_10000.json
```

Remaining exact archive pairs and relation-level validation remain separate
work. The parks capacity boundary must not be “fixed” by adding
paper-specific RTDL behavior.
