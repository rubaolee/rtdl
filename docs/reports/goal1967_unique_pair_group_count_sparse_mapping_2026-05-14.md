# Goal1967 Unique-Pair Group Count Sparse Mapping

Date: 2026-05-14

Status: implementation refinement

## Why This Goal Exists

Goal1962 made unique-pair grouped counts reusable, but the first implementation
used a dense output-group by witness-pair match matrix. That preserved arbitrary
sparse group IDs, but it was the wrong performance shape for the same reason
earlier v2 control rows were weak: the partner continuation layer must avoid
rebuilding large dense app-shaped intermediates.

## Implemented Refinement

`partner_group_count_unique_pairs_by_key` now maps arbitrary sparse group IDs to
output positions with `sort/searchsorted`:

```text
output group ids -> sorted ids + original positions
group keys -> searchsorted lookup -> output positions
output positions + item ids -> unique pairs -> per-group counts
```

Torch uses `torch.sort` / `torch.searchsorted`; CuPy uses `cupy.argsort` /
`cupy.searchsorted`. The validation still fails closed when a group key is not
present in `output_group_keys`.

## Design Boundary

The engine remains app-agnostic. This change only improves a generic partner
identity-table reduction. It does not add polygon, segment, hit-count, or graph
semantics to native code.

## Expected Impact

This avoids the old dense `groups x pairs` match matrix and keeps the primitive
better aligned with large v2 workloads where IDs are stable but not necessarily
dense. Pod timing is still required before making a new performance claim.

