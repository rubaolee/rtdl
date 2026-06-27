# Goal2531: Barnes-Hut Generic Aggregate Opening Rows

Date: 2026-05-23

## Decision

Implement the first generic Barnes-Hut reconstruction primitive as a local
CPU/Python reference contract:

```text
weighted source points
+ aggregate tree nodes
+ optional candidate node rows
+ opening predicate theta
-> accepted aggregate-node rows
+ fallback exact-body rows
```

The public contract name is:

```text
generic_aggregate_opening_rows_2d_v1
```

This is app-name-free. It does not add native Embree/OptiX code and does not
authorize performance wording.

## What Was Added

New module:

- `src/rtdsl/aggregate_tree_reference.py`

New exports:

- `AGGREGATE_OPENING_ROWS_2D_CONTRACT`
- `WeightedPointRow`
- `AggregateNodeRow`
- `normalize_weighted_point_rows`
- `normalize_aggregate_node_rows`
- `evaluate_aggregate_opening_rows_2d`

Benchmark wrapper update:

- `examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py`
  now exposes `--mode opening_rows_cpu`.

## Semantics

For each weighted source point and candidate aggregate node:

1. Compute the source-to-node-center distance.
2. Compute `opening_ratio = 2 * half_size / distance`; zero distance maps to
   infinity.
3. Accept the aggregate node if it does not contain the source point and
   `opening_ratio < theta`.
4. Otherwise emit fallback exact rows for each member point in the node except
   the source point.

The result contains:

- `accepted_aggregate_rows`;
- `fallback_exact_rows`;
- `per_source_summary`;
- global `summary`;
- metadata that blocks paper reproduction, authors-code comparison, and public
  speedup claims.

## Why This Matters

Before this goal, the Barnes-Hut app had RTDL candidate rows and separate
Python opening logic. Goal2531 lifts that opening decision into a reusable
generic contract. This is the first step toward a real RT-BarnesHut-style
benchmark app without adding a Barnes-Hut-specific native engine path.

The next runtime options are now clearer:

- promote `generic_aggregate_opening_rows_2d_v1` into a native or partner path;
- define generic vector force contribution rows from accepted aggregate and
  fallback exact rows;
- define grouped vector reductions or partner-resident vector accumulation.

## Claim Boundary

Authorized:

- generic CPU/Python reference semantics for aggregate opening rows;
- benchmark wrapper mode for Barnes-Hut reconstruction work;
- local correctness tests over the existing bounded fixture.

Not authorized:

- full RT-BarnesHut paper reproduction;
- authors-code comparison;
- public speedup wording;
- native Barnes-Hut ABI;
- native hierarchical traversal claim;
- force-vector acceleration claim.

## Validation

Focused validation:

```bash
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest tests.goal2531_barnes_hut_generic_opening_rows_test
```
