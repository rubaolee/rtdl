# Goal 371 Report: v0.6 bounded cit-Patents triangle-count plan

Date: 2026-04-14

## Summary

After the first bounded Linux `cit-Patents` BFS result, the next bounded
real-data step should be:

- `triangle_count` on `graphalytics_cit_patents`

but only under an explicit simple-graph transform policy.

## Recommended transform

The first `cit-Patents` triangle-count slice should follow the same simple-graph
discipline already used on `wiki-Talk`:

- read the raw directed edge list
- drop self-loops
- canonicalize each edge as `(min(src, dst), max(src, dst))`
- dedupe canonical undirected edges
- materialize a simple undirected CSR graph

## Why this is the right first step

### 1. It keeps the workload contract honest

Current `triangle_count` truth/oracle line assumes:

- simple graph
- strictly ascending neighbor lists
- no self-loops

The transform above preserves those expectations.

### 2. It matches the current real-data method

`wiki-Talk` triangle count already uses this transform.

Using the same policy on `cit-Patents` keeps the second dataset line comparable
without claiming that the raw directed graph is being counted directly.

### 3. It keeps the first `cit-Patents` triangle slice bounded

The first slice should be:

- bounded by canonical undirected edge count
- explicit that Python remains the truth path
- explicit that Python may not remain a practical timing baseline at larger
  bounds

## Recommended first bounded evaluation shape

- dataset:
  - `graphalytics_cit_patents`
- transform:
  - `simple_undirected`
- workload:
  - `triangle_count`
- first bound:
  - start conservatively, smaller than the latest `wiki-Talk` triangle slice
  - choose the bound from a quick local/Linux probe rather than guessing

## Boundary

This is a planning slice only:

- not a live `cit-Patents` triangle result
- not full dataset closure
- not a benchmark claim
- not a paper-scale reproduction claim
