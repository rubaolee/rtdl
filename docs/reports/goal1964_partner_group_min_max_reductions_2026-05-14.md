# Goal1964 Partner Group Min/Max Reductions

Date: 2026-05-14

Status: implementation slice

## Why This Goal Exists

Goal1958 identified several v2.0 rows that are fast only for threshold proxies:
exact Hausdorff, ranked KNN, DBSCAN expansion, and Barnes-Hut force work still
need richer continuation algebra. Goal1960 and Goal1962 added count/sum/any and
unique-pair counts; this goal adds the next small reusable piece: grouped
min/max reductions.

## Implemented Slice

`src/rtdsl/partner_adapters.py` now exposes:

```text
partner_group_max_by_key(keys, values, group_count, partner=..., initial=...)
partner_group_min_by_key(keys, values, group_count, partner=..., initial=...)
```

Both functions support PyTorch and CuPy tensors and keep data in the selected
partner runtime. Torch uses `scatter_reduce` with `amax` / `amin`; CuPy uses
`cupy.maximum.at` / `cupy.minimum.at`.

## Design Boundary

This does not add app semantics to the native engine. RTDL native code still
emits generic candidates, hits, counts, distances, or payload columns. The
partner layer performs a generic grouped reduction. App code decides whether a
grouped max is a Hausdorff worst-case distance, a force bound, a graph score, or
something else.

## What This Enables Next

The immediate uses are:

- exact directed Hausdorff structure: nearest distance per query, then max over
  query groups;
- richer KNN and ANN summaries after top-k candidate output exists;
- Barnes-Hut and n-body style max/min bound filters;
- graph and polygon continuation scores that need extrema rather than counts.

## What Remains

This is still only algebra. To turn the weak rows into final v2.0 speedups, we
still need:

- a reusable top-k-by-key primitive for ranked KNN;
- prefix/paging/compaction for arbitrary row outputs;
- graph frontier and triangle-count contracts;
- exact polygon/set area accumulation;
- full DBSCAN cluster-label expansion.

