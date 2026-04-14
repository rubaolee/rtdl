# Goal 360: v0.6 real-data bounded triangle-count eval

## Why

After Goal 359, `v0.6` should have a symmetric bounded real-data opening line:
- BFS on real `wiki-Talk`
- triangle count on real `wiki-Talk` after an explicit simple-graph transform

This goal exists to record that symmetry explicitly instead of leaving triangle count as an isolated script run.

## Scope

Bound this slice to:
- summarize the first real-data triangle-count result
- preserve the transform boundary
- preserve Linux/PostgreSQL parity facts
- avoid broad graph-performance claims

## Closure

Close when the repo has a saved report and review that state:
- the first bounded real-data triangle-count slice is real
- parity is clean across Python/oracle/PostgreSQL on Linux
- the slice remains bounded and not overclaimed
