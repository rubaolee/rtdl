# Goal 364: v0.6 split-bound next-scale Linux graph evaluation

## Why

Goal 363 showed that the next real-data scale step should split by workload:
- BFS can move higher without stress
- triangle count reaches Python timing pressure much earlier

This goal converts that plan into one real bounded Linux evaluation slice.

## Scope

Bound this slice to:
- `SNAP wiki-Talk`
- Linux host `lestat-lx1`
- corrected PostgreSQL timing split
- workload-specific bounds:
  - BFS: `1000000` directed edges
  - triangle count: `200000` canonical undirected edges

Keep the existing triangle-count transform:
- simple undirected
- self-loops dropped
- canonical undirected edges deduped

## Non-goals

- full dataset closure
- new datasets
- paper-scale reproduction
- accelerated graph backend work

## Closure

Close when:
- Linux results are real for both workloads
- parity is clean across Python/oracle/PostgreSQL
- report language stays explicit that Python triangle count is truth-preserving
  but increasingly impractical as a timing baseline
