# Goal 372 Report: v0.6 bounded cit-Patents triangle-count probe

Date: 2026-04-14

## Summary

This slice adds the first runnable probe path for:

- `triangle_count` on `graphalytics_cit_patents`

using the same `simple_undirected` transform already adopted for real-data
triangle counting.

## What was added

- a bounded probe script:
  - `scripts/goal372_cit_patents_triangle_count_probe.py`
- focused script-level coverage:
  - `tests/goal372_v0_6_cit_patents_triangle_count_probe_test.py`

## Default bounded contract

- dataset path:
  - `build/graph_datasets/cit-Patents.txt.gz`
- transform:
  - `simple_undirected`
- workload:
  - `triangle_count`
- conservative first cap:
  - `50000` canonical undirected edges

## Why this shape is correct

- it matches the current triangle-count truth-path contract
- it mirrors the already-validated `wiki-Talk` real-data transform
- it gives a safe first probe point before a larger Linux run is chosen

## Boundary

This is a bounded probe-script slice only:

- not a live Linux result yet
- not full `cit-Patents` triangle-count closure
- not a benchmark claim
- not a paper-scale reproduction claim
