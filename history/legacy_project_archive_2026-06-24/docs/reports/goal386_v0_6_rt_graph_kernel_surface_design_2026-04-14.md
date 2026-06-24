# Goal 386 Report: v0.6 RT Graph Kernel Surface Design

Date: 2026-04-14
Status: drafted

## Summary

The next dependency for the corrected `v0.6` line is the RT graph kernel
surface. The current DSL is authoritative for geometry kernels only, so the
graph line must state its kernel contract explicitly instead of assuming it can
be inferred from existing shapes.

The critical design constraint is paper consistency:

- the RTDL graph line must map graph work into RT traversal
- BFS must remain a host-driven frontier loop with an RT-based expansion step
- triangle counting must remain a set-intersection-style search recast as RT
  traversal over encoded graph relations
- Embree, OptiX, and Vulkan are backends for this model, not the model itself

## Design Questions To Resolve

The design must answer, at minimum:

1. how graph inputs are declared in RTDL
2. whether CSR is represented directly as a graph input or as lower-level graph
   field bundles
3. how graph traversal maps to `rt.traverse(...)`
4. what `rt.refine(...)` means for:
   - `bfs`
   - `triangle_count`
5. how output rows are emitted from graph kernels
6. whether graph workloads need:
   - new graph predicates
   - new graph input types
   - new graph roles/layout helpers

## Chosen Design Position

The design should preserve the current RTDL kernel shape:

- preserve the RTDL kernel shape:
  - `input -> traverse -> refine -> emit`
- add graph-specific surface explicitly rather than hiding it
- keep the initial graph workloads bounded to:
  - `bfs`
  - `triangle_count`
- keep CSR as the canonical starting graph representation

But the host program must stay in charge of the outer algorithm loop when the
paper requires it.

## Host Versus Kernel Boundary

### BFS

The host owns:

- BFS level loop
- frontier dedupe between levels
- visited-state updates between levels
- termination when the frontier is empty

The RTDL kernel owns one bounded RT expansion step:

- read the current frontier work items
- traverse the RT-encoded graph structure
- materialize candidate neighbor rows
- refine by BFS discovery rules
- emit next-frontier rows

This stays consistent with the paper's structure:

- build the RT structure
- iterate frontier by frontier
- use RT expansion as the expensive neighbor-visit operation

### Triangle Count

The host owns:

- batching over seed vertices or edges
- optional aggregation of partial counts
- outer iteration and final reduction

The RTDL kernel owns one bounded candidate-search step:

- traverse the RT-encoded graph relations
- discover common-neighbor candidates or 2-hop/1-hop matches
- refine by uniqueness and ordering rules
- emit partial triangle rows or per-seed counts

## Graph Data Model

The logical graph contract remains CSR.

That means the public logical graph input is still:

- row offsets
- column indices
- vertex count
- edge count

But execution uses an RT encoding derived from CSR rather than raw pointer
chasing.

The design therefore separates:

- logical input:
  - `rt.GraphCSR`
- execution preparation:
  - RT-encodable primitive stream built from CSR
- execution target:
  - BVH or equivalent RT acceleration structure over that primitive stream

The language surface should expose the logical graph, not the primitive stream,
because users should author graph kernels at graph level.

## Proposed RTDL Surface Additions

### New Input Types

- `rt.GraphCSR`
  - canonical graph input
- `rt.VertexFrontier`
  - current BFS frontier or vertex seed set
- `rt.VertexSet`
  - visited set or generic vertex mask/set
- `rt.EdgeSet`
  - optional seed edge batch for triangle counting

### New Layout Helpers

- `rt.GraphCSRLayout`
- `rt.VertexFrontierLayout`
- `rt.VertexSetLayout`
- `rt.EdgeSetLayout`

These are logical layouts, not the final RT primitive encoding.

### New Traverse Modes

Keep `rt.traverse(...)`, but extend it with graph meaning.

Examples:

- `rt.traverse(frontier, graph, accel="bvh", mode="graph_expand")`
- `rt.traverse(seeds, graph, accel="bvh", mode="graph_intersect")`

The important point is that `traverse` remains the candidate-generation stage;
it just gains graph-specific execution meaning.

### New Predicates

- `rt.bfs_discover(visited=..., dedupe=True)`
- `rt.triangle_match(order="id_ascending", unique=True)`

These are graph-semantic refine operations.

## BFS Kernel Design

### Intended Authoring Shape

```python
@rt.kernel(backend="rtdl", precision="float_approx")
def bfs_expand():
    graph = rt.input("graph", rt.GraphCSR, role="build")
    frontier = rt.input("frontier", rt.VertexFrontier, role="probe")
    visited = rt.input("visited", rt.VertexSet, role="probe")

    candidates = rt.traverse(frontier, graph, accel="bvh", mode="graph_expand")
    fresh = rt.refine(
        candidates,
        predicate=rt.bfs_discover(visited=visited, dedupe=True),
    )
    return rt.emit(
        fresh,
        fields=["src_vertex", "dst_vertex", "level"]
    )
```

### Meaning

- the host provides the frontier and current visited state
- `traverse` issues the RT-based neighbor visit step
- `refine` filters already-seen vertices and duplicates
- `emit` materializes next-frontier rows

This is intentionally one BFS step, not a whole end-to-end BFS loop inside the
kernel.

## Triangle Count Kernel Design

### Intended Authoring Shape

```python
@rt.kernel(backend="rtdl", precision="float_approx")
def triangle_probe():
    graph = rt.input("graph", rt.GraphCSR, role="build")
    seeds = rt.input("seeds", rt.EdgeSet, role="probe")

    candidates = rt.traverse(seeds, graph, accel="bvh", mode="graph_intersect")
    triangles = rt.refine(
        candidates,
        predicate=rt.triangle_match(order="id_ascending", unique=True),
    )
    return rt.emit(
        triangles,
        fields=["u", "v", "w"]
    )
```

### Meaning

- the host supplies an edge or vertex batch
- `traverse` uses the RT structure to search the matching graph relations
- `refine` enforces triangle semantics and uniqueness
- `emit` returns triangle rows or inputs to a later reduction

## Non-Goals

This goal does not define:

- the exact primitive geometry used by the RT encoding
- full lowering details
- backend-specific API calls
- performance claims
- complete syntax stability for future graph workloads beyond:
  - `bfs`
  - `triangle_count`

## Closure Criteria

This goal should only close when the repo has:

- example RTDL graph kernels in design form
- explicit graph surface additions listed
- explicit host-versus-kernel boundaries listed
- explicit non-goals listed
- a review trail that agrees the design is honest and paper-aligned
