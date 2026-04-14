# Goal 359: v0.6 wiki-Talk triangle-count bounded eval

## Why

`v0.6` already has a bounded real-data BFS line on `SNAP wiki-Talk`, but triangle count does not yet have a matching real-data slice. We need a first honest real-data triangle-count result before claiming the opening graph-evaluation line is balanced across the two starter workloads.

## Scope

Bound this slice to:
- `SNAP wiki-Talk`
- first bounded real-data `triangle_count` run
- explicit real-data transform:
  - symmetrize
  - dedupe
  - drop self-loops
  - simple undirected CSR
- Python truth path
- RTDL compiled CPU/oracle
- PostgreSQL baseline on Linux

Do not claim:
- full `wiki-Talk` closure
- large-scale graph benchmarking
- paper-equivalent graph-system comparison

## Required work

- add an explicit simple-undirected SNAP loader instead of relying on an implicit `directed=False` interpretation
- add a bounded `wiki-Talk` triangle-count eval script
- validate the loader and script with focused tests
- run the bounded real-data case locally
- run the bounded real-data case on Linux with PostgreSQL enabled

## Closure

Close when:
- the transform policy is explicit in code and docs
- the bounded real-data triangle-count run is parity-clean for Python/oracle
- the Linux PostgreSQL baseline also matches
- the report language stays bounded and honest
