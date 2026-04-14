# Goal 368 Report: v0.6 first bounded cit-Patents BFS evaluation

Date: 2026-04-13

## Summary

This slice adds the first bounded BFS evaluation path for:
- `graphalytics_cit_patents`

The script reuses the current graph-evaluation harness and honors the corrected
PostgreSQL timing split from Goal 361.

## What was added

- a bounded BFS script:
  - `scripts/goal368_cit_patents_bfs_eval.py`
- focused script-level coverage:
  - `tests/goal368_v0_6_cit_patents_bfs_eval_test.py`

## Default bounded contract

- dataset path:
  - `build/graph_datasets/cit-Patents.txt.gz`
- workload:
  - `bfs`
- default edge cap:
  - `500000`
- expected vertex count:
  - `3774768`

## Boundary

This is a bounded first-use script slice:

- not a live Linux result yet
- not full `cit-Patents` closure
- not a benchmark claim
- not a paper-scale reproduction claim
