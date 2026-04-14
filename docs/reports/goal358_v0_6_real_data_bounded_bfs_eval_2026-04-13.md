# Goal 358 Report: v0.6 Real-Data Bounded BFS Evaluation

Date: 2026-04-13

## Summary

This slice records the first bounded real-data BFS evaluation for `v0.6`.

Dataset:

- SNAP `wiki-Talk`

Bound:

- first `200000` directed edges

## Backend table

### Local

- Python: `0.056229250 s`
- oracle: `0.337273541 s`
- oracle parity: `true`

### Linux (`lestat-lx1`)

- Python: `0.053139454 s`
- oracle: `0.412102957 s`
- PostgreSQL query: `0.000543500 s`
- PostgreSQL setup: `11.957648676 s`
- oracle parity: `true`
- PostgreSQL parity: `true`

## Boundary

- this is the first bounded real-data BFS result only
- the graph is still edge-capped
- this is not full `wiki-Talk` closure
- this is not a real-data triangle-count closure
- the earlier combined PostgreSQL timing is superseded by query/setup split
