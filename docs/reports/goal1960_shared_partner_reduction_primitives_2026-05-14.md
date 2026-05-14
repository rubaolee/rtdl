# Goal1960 Shared Partner Reduction Primitives

Date: 2026-05-14

Status: first implementation slice

## Why This Goal Exists

Goal1958 identified that v2.0's remaining weakness is not a single slow kernel.
The design problem is that several app continuations still encode their own
one-off reduction logic:

- database analytics has an app-local RawKernel for grouped counts and sums;
- graph analytics uses a closed-form app summary rather than reusable graph
  reductions;
- segment/polygon row-output paths still need device-resident compaction and
  grouped counting;
- polygon set metrics need reusable identity-preserving set reductions;
- richer proxy apps need top-k, max-distance, cluster expansion, or vector
  accumulation contracts before their full app semantics can be claimed.

The shared missing layer is a small partner reduction algebra over RTDL identity
tables.

## Implemented Slice

`src/rtdsl/partner_adapters.py` now exposes reusable partner primitives:

- `partner_group_count_by_key(keys, group_count, partner=...)`
- `partner_group_sum_by_key(keys, values, group_count, partner=...)`
- `partner_group_any_by_key(keys, flags, group_count, partner=...)`
- `partner_unique_pair_keys(left_keys, right_keys, partner=...)`

These run on Torch or CuPy tensors and return partner tensors without host
materialization. They are deliberately generic: the engine does not see database,
graph, polygon, DBSCAN, or Barnes-Hut names.

The first adapter migration is the robot collision pose-flag reduction:

```text
generic per-ray any-hit flags + dense pose_indices
  -> partner_group_any_by_key(...)
  -> one pose collision flag per pose
```

This replaces a bespoke scatter/max implementation with the shared primitive.

## What This Solves

This is the first concrete move from app-specific continuation kernels toward a
reusable v2 partner continuation layer. It directly supports:

- pose/ray flag grouping;
- future graph frontier and visibility grouping;
- DB grouped count/sum rewrites;
- shape/set candidate aggregation;
- device-side row compaction and duplicate-pair handling.

## What It Does Not Solve Yet

This goal does not by itself finish:

- generic graph traversal/triangle-count primitives;
- exact polygon overlay or arbitrary set-union reductions;
- ranked KNN assignment;
- exact directed Hausdorff max-distance;
- full DBSCAN cluster expansion;
- Barnes-Hut force-vector accumulation.

Those app semantics need additional contracts built on top of this primitive set.

## Design Answer

The v2.0 design problem is not that users cannot write app continuations. They
can. The problem is that RTDL must give those continuations common, reusable
building blocks so every serious app does not become a fresh custom GPU program.

The next required layer is:

```text
RTDL identity table -> partner grouped reductions / compaction / top-k -> app result
```

Goal1960 lands the first part of that layer.

