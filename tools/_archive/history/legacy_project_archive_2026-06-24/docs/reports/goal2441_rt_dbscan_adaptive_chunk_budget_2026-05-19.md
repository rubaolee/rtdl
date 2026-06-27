# Goal2441 RT-DBSCAN Adaptive Chunk Budget

Date: 2026-05-19

Status: implemented locally, pending optional pod smoke.

## Purpose

The Goal2433/2435 chunked adjacency continuation accepted
`max_directed_edges_per_chunk`, but fixed 4096-point chunks were chosen before
degree counts were known. That meant a dense chunk could exceed the requested
edge budget and fail instead of splitting.

Goal2441 makes the chunk planner degree-budget-aware while keeping the runtime
generic and app-agnostic.

## What Changed

`src/rtdsl/partner_adapters.py` now adds:

- `_radius_graph_degree_budget_chunk_ranges(...)`
- `count_chunk_ranges` metadata
- `chunk_planning_policy`
- `max_directed_edges_per_chunk` metadata

The prepared chunked adapter now:

1. counts exact fixed-radius degrees in count chunks;
2. copies the degree column to a small host planning vector;
3. builds adjacency chunk ranges that obey both `max_chunk_points` and
   `max_directed_edges_per_chunk`;
4. runs the existing single-pass chunked union/label continuation.

The benchmark app now exposes:

```text
--chunk-adjacency-edge-budget
```

This is passed to
`prepare_optix_cupy_radius_graph_chunked_adjacency_3d(...,
max_directed_edges_per_chunk=...)`.

## Boundary

This is a memory-control improvement, not a speedup claim. It does not add a
DBSCAN-native ABI, does not change native engine semantics, and does not make a
paper-reproduction or release claim.

The only intended behavior change is that dense chunks can be split according to
a user-visible directed-edge budget after exact degree counts are known.

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2441_rt_dbscan_adaptive_chunk_budget_test
```

The focused test verifies:

- chunk ranges obey point and edge limits;
- old fixed point-count chunking is preserved when no edge budget is supplied;
- impossible single-query budgets fail clearly;
- runtime/app/docs expose the new budget and metadata;
- claim boundaries remain explicit.

## Verdict

`accept-with-boundary`.
