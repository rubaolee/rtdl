# Goal 387 Report: v0.6 RT Graph Execution Interpretation

Date: 2026-04-14
Status: drafted

## Summary

This goal defines how the RTDL graph kernel surface should be interpreted at
execution time so the `v0.6` graph line remains faithful to the SIGMETRICS 2025
paper rather than collapsing back into a detached graph runtime.

The core rule is:

- the user authors logical graph kernels
- RTDL lowers those kernels into RT-based search work
- the expensive candidate-generation step is realized through RT traversal
- host code still owns outer algorithm loops where the paper requires them

## Interpretation Layers

### 1. Logical Graph Contract

The user-facing graph contract remains CSR:

- `row_offsets`
- `column_indices`
- `vertex_count`
- `edge_count`

This is the semantic graph input seen by RTDL authors.

### 2. Execution Encoding Contract

The runtime does not execute over raw CSR pointer chasing directly.

Instead it derives:

- a primitive stream or relation encoding suitable for RT traversal
- an acceleration structure such as a BVH over that encoding

This is an execution concern, not a public authoring concern.

### 3. RT Traversal Contract

`rt.traverse(...)` in graph kernels means:

- prepare rays or ray-like RT queries from the current work-item batch
- traverse the RT acceleration structure
- materialize graph-relevant candidate hits

The exact primitive shape may differ by workload, but the invariant is:

- RT traversal performs candidate generation
- graph semantics are enforced later in `refine`

## BFS Interpretation

### Host Side

The host owns:

- source initialization
- current frontier
- visited set state
- BFS level counter
- termination when frontier becomes empty

### Kernel Side

The `bfs_expand` kernel owns one bounded expansion step:

1. frontier work items are converted into RT query work
2. RT traversal searches the encoded neighbor relations
3. candidate neighbor rows are returned
4. `refine` removes already-visited or duplicate discoveries
5. `emit` materializes next-frontier rows

This matches the paper's RT-based BFS structure at the execution-model level:

- host-controlled frontier progression
- RT-based neighbor visiting inside the bounded expansion step
- host-side continuation after each expansion round

### Meaning of `traverse`

For BFS, `traverse(frontier, graph, mode=\"graph_expand\")` means:

- for each frontier vertex, issue RT queries that realize neighbor visiting
- interpret RT hits as candidate outgoing neighbor relations

In `graph_expand` mode, the RT structure is interpreted so that a hit
represents a candidate neighbor-discovery relation for the current frontier
vertex.

### Meaning of `refine`

For BFS, `rt.bfs_discover(...)` means:

- reject already-visited vertices
- dedupe repeated discovery of the same vertex
- preserve level semantics for the current host-controlled BFS step

`rt.bfs_discover(...)` is intended as a proposed public graph-surface predicate
from Goal 386, not as an internal lowering-only alias.

### Meaning of `emit`

For BFS, `emit` should return rows sufficient for host-side next-frontier
construction, such as:

- `src_vertex`
- `dst_vertex`
- `level`

## Triangle Count Interpretation

### Host Side

The host owns:

- seed batching over vertices or edges
- optional aggregation or reduction over emitted partial results
- termination and scheduling across batches

### Kernel Side

The `triangle_probe` kernel owns one bounded relation-search step:

1. seed work items are converted into RT query work
2. RT traversal searches encoded graph relations
3. candidate common-neighbor or 2-hop/1-hop matches are returned
4. `refine` enforces triangle uniqueness and ordering
5. `emit` materializes triangle rows or per-seed partial counts

This matches the paper's RT-based triangle-count direction at the execution
model level:

- the expensive set-intersection-style search is recast as RT traversal
- host code still owns batching and final aggregation

### Meaning of `traverse`

For triangle count, `traverse(seeds, graph, mode=\"graph_intersect\")` means:

- issue RT queries that search relation matches consistent with the paper's
  set-intersection-style formulation
- treat RT hits as candidates for common-neighbor or relation-match discovery

In `graph_intersect` mode, the RT structure is interpreted so that a hit
represents a candidate relation match for triangle formation rather than a BFS
neighbor-discovery event.

### Meaning of `refine`

For triangle count, `rt.triangle_match(...)` means:

- enforce uniqueness
- avoid duplicate or reversed counting
- preserve the chosen ordering discipline

`rt.triangle_match(...)` is also intended as a proposed public graph-surface
predicate from Goal 386, not as an unannounced private alias.

### Meaning of `emit`

For triangle count, `emit` may return either:

- explicit triangle rows:
  - `u`
  - `v`
  - `w`
- or per-seed partial counts for later host reduction

The first public truth-path form should prefer explicit rows or obviously
checkable partial counts.

## Workload-Specific RT Encoding Direction

This goal does not freeze one primitive encoding, but it does impose one rule:

- the encoding must preserve paper consistency

That means:

- BFS encoding must support RT-based neighbor visiting
- triangle-count encoding must support RT-based relation search for
  intersection-style counting

The runtime may use different RT encodings for different workloads if needed,
as long as the logical kernel surface stays stable.

## Stable Invariants

The following invariants must hold across later lowering and backend work:

- authors write logical RTDL graph kernels, not backend code
- RT traversal is the candidate-generation engine
- graph semantics live in `refine`
- host code owns outer control loops where required by the paper
- correctness is checked first on bounded cases

## Non-Goals

This goal does not define:

- exact backend API calls
- exact Embree/OptiX/Vulkan implementation details
- final performance claims
- all future graph workloads beyond:
  - `bfs`
  - `triangle_count`
