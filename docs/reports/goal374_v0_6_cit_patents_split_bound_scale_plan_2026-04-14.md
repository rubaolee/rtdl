# Goal 374 Report: v0.6 cit-Patents split-bound scale plan

Date: 2026-04-14

## Summary

The `cit-Patents` line now has enough real Linux evidence to justify a
split-bound next step rather than a single shared cap.

## Current measured base

### BFS base

- dataset:
  - `graphalytics_cit_patents`
- current bound:
  - `500000` directed edges
- Linux result:
  - Python `0.10589127999264747`
  - oracle `0.9401946720317937`
  - PostgreSQL query `0.0003507979563437402`
  - PostgreSQL setup `23.093791443970986`

### Triangle-count base

- dataset:
  - `graphalytics_cit_patents`
- current bound:
  - `50000` canonical undirected edges
- Linux result:
  - Python `3.606278282997664`
  - oracle `0.7714257469633594`
  - PostgreSQL query `0.011647004052065313`
  - PostgreSQL setup `2.557821645983495`

## Recommended next split

### BFS

Next bounded step:
- `1000000` directed edges

Why:
- Python and oracle are both still comfortable at `500000`
- PostgreSQL query time is still tiny
- setup time dominates, which means a larger bound is still informative

### Triangle count

Next bounded step:
- `100000` canonical undirected edges

Why:
- Python is still practical at `50000`
- but triangle count grows less gently than BFS
- a 2x step is a safer next measurement than a large jump copied from the
  `wiki-Talk` line

## Why a split is required

The `wiki-Talk` line already showed that:

- BFS can usually advance faster
- triangle count becomes truth-only much earlier

The first `cit-Patents` measurements are consistent with that same pattern.

## Boundary

This is a scale-decision slice only:

- not a live larger result
- not a final accepted production bound
- not a benchmark claim
- not a paper-scale reproduction claim
