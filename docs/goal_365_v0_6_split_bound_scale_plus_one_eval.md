# Goal 365: v0.6 split-bound scale-plus-one Linux graph evaluation

## Why

Goal 364 proved that the next `wiki-Talk` scale step should continue to split by
workload. This goal extends that split one more step with real Linux results.

## Scope

Bound this slice to:
- `SNAP wiki-Talk`
- Linux host `lestat-lx1`
- corrected PostgreSQL query/setup timing split
- workload-specific bounds:
  - BFS: `1500000` directed edges
  - triangle count: `250000` canonical undirected edges

Keep the existing triangle-count transform:
- simple undirected
- self-loops dropped
- canonical undirected edges deduped

## Non-goals

- full dataset closure
- paper-scale reproduction
- new datasets
- accelerated graph backends

## Closure

Close when:
- Linux runs are real for both workloads
- parity is clean across Python/oracle/PostgreSQL
- the report language stays explicit that Python triangle count is truth-only,
  not a practical timing baseline at this size
