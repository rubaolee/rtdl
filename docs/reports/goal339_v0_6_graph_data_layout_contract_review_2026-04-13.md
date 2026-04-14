# Goal 339 Review: v0.6 Graph Data / Layout Contract

Date: 2026-04-13

## Decision

Goal 339 is accepted after tightening the implementation-critical contract.

## What changed before closure

Gemini correctly identified that the original contract direction was coherent
but still too vague for BFS and triangle-count truth-path work.

The report was tightened to make the first contract explicit:

- canonical layout:
  - CSR
- ID/index types:
  - `uint32_t`
- topology assumption:
  - simple graphs
  - no self-loops
  - no multi-edges
- BFS opening frontier boundary:
  - materialized list of vertex IDs
- triangle-count opening boundary:
  - undirected simple graphs with sorted neighbor lists

## Result

The graph data/layout contract is now specific enough to support:

- Goal 340:
  - BFS truth path
- Goal 341:
  - triangle-count truth path

## Boundary preserved

- application still owns graph ingestion and preprocessing
- RTDL still owns workload semantics and backend execution over prepared graph
  data
- this is still a bounded starting contract, not a claim of a general graph
  ingestion system
