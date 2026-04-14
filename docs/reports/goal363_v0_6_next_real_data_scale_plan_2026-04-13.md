# Goal 363 Report: v0.6 next real-data scale plan

## Summary

After Goal 362, the next bounded scale step should split by workload instead of
using one shared growth rule.

## Current evidence

### BFS

- `500000` directed edges on Linux is still easy for:
  - Python truth path
  - oracle
  - PostgreSQL query path
- local probe at `1000000` directed edges is still parity-clean:
  - Python `0.084742250 s`
  - oracle `7.206675375 s`

### Triangle count

- `150000` canonical undirected edges on Linux:
  - Python `27.710148987 s`
  - oracle `0.450658018 s`
  - PostgreSQL query `0.671557261 s`
- local probe at `250000` canonical undirected edges:
  - Python `46.240866375 s`
  - oracle `0.458041209 s`

## Recommended next bound

Use workload-specific next bounds:

- BFS:
  - next bounded target: `1000000` directed edges
- triangle count:
  - next bounded target: `200000` to `250000` canonical undirected edges
  - but only if the report language explicitly treats Python as a truth path,
    not as a practical timing baseline

## Why this is the right next move

- BFS still has room to scale without losing the truth/oracle comparison shape.
- Triangle count already shows strong Python timing degradation.
- The next step should increase evidence without letting the slice turn into an
  unbounded “wait on Python” exercise.

## Non-goals

- full `wiki-Talk` closure
- new datasets in the same slice
- accelerated graph backend work
- paper-scale reproduction
