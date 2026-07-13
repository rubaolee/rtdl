# Goal5521 LibRTS Parks.bz2 Range-Contains Cardinality Matrix

Status: `implemented__five_exact_count_matches__range_contains_14_of_14_complete__review_pending`

## Objective

Resolve the last five exact-archive `range_contains` pairs without hiding the
capacity risk of the 11,544,398-row `parks.bz2` prepared base.

## Capacity gate

The author runs first on the smallest 50K query. It completed with count
`52,849`, so the gate authorized the app-owned RTDL cache and the remaining
matrix. Had the author failed, the pipeline would have stopped before RTDL
cache construction.

## Result

| Query rows | Author | RTDL | Pinned author paper log |
|---:|---:|---:|---:|
| 50,000 | 52,849 | 52,849 | 52,849 |
| 100,000 | 105,826 | 105,826 | 105,826 |
| 200,000 | 211,714 | 211,714 | 211,714 |
| 400,000 | 423,396 | 423,396 | 423,396 |
| 800,000 | 846,860 | 846,860 | 846,860 |

All five query SHA-256 values are distinct. This is one prepared geometry base
consuming five different query batches, not replay of one answer.

## System boundary

WKT extraction and the 397 MiB AABB cache remain LibRTS app-owned. RTDL begins
at the neutral `Aabb2DColumns` contract, prepares one generic OptiX AABB index,
and calls `prepared.count(operation="range_contains")`. No LibRTS identity or
paper-specific predicate is introduced in RTDL core.

## Coverage

Goal5521 adds the final five matches to the nine prior checkpoints. The exact
archive `range_contains` inventory is therefore complete at **14/14 count
matches**.

This is a complete count matrix, not pointwise containment-relation equality.
It is also not a performance comparison, Figure 6 reproduction, full paper
reproduction, author algorithm equivalence, zero-copy claim, or Embree work.

Primary evidence:

```text
Paper-reproduction-apps/librts-paper/results/goal5521_parks_bz2_range_contains_cardinality_gate.json
```
