# Goal 357 Report: v0.6 wiki-Talk BFS Bounded Evaluation

Date: 2026-04-13

## Summary

This slice prepares the first bounded real-data BFS evaluation on SNAP
`wiki-Talk`.

## What was added

- fetch helper for `wiki-Talk`
- bounded BFS evaluation script for an edge-capped `wiki-Talk` slice
- focused script-level smoke test

## Bounded execution result

### Local

- dataset: `snap_wiki_talk`
- max edges loaded: `200000`
- vertex count: `2394381`
- edge count: `200000`
- Python: `0.056229250 s`
- oracle: `0.337273541 s`
- oracle parity: `true`

### Linux (`lestat-lx1`)

- dataset: `snap_wiki_talk`
- max edges loaded: `200000`
- vertex count: `2394381`
- edge count: `200000`
- Python: `0.053139454 s`
- oracle: `0.412102957 s`
- PostgreSQL query: `0.000543500 s`
- PostgreSQL setup: `11.957648676 s`
- oracle parity: `true`
- PostgreSQL parity: `true`

## Current boundary

This is a bounded real-data BFS slice:

- not full `wiki-Talk` closure
- not a triangle-count real-data slice
- not a large-scale benchmark claim
- earlier combined PostgreSQL timing for this slice is superseded by the split
  query/setup measurement
