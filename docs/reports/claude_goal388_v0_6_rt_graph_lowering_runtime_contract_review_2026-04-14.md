# Claude Review: Goal 388 v0.6 RT Graph Lowering And Runtime Contract

## Verdict: Pass with minor caveats

### Finding 1 — Boundary clarity is good, but asymmetric

The lowering/runtime/host split is described well at a logical level. Host-owned
state versus runtime-owned state is correctly separated. The only softer part is
that the lowering side is still less concrete than the runtime side, which could
allow future lowering drift if not tightened later in implementation goals.

### Finding 2 — Kernel model integrity is preserved

The report correctly prohibits detached `bfs(graph, source)` or
`triangle_count(graph)` APIs as the primary product story and bars raw backend
graph structures from the public surface. This keeps the RTDL kernel model
intact.

### Finding 3 — Backend hook contract needed equivalence tightening

The backend hook was honest but initially underspecified because "semantically
equivalent" could be read too loosely. The updated report now tightens this to
mean:

- the same bounded candidate relation set for the current step
- or the same emitted partial-row content after the same `refine` / `emit`
  semantics

That resolves the main ambiguity.

### Finding 4 — Implementation ordering is correct

The staged sequence (graph-aware IR, then bounded Python/oracle truth, then
backend RT mapping) is the right risk order and keeps the honesty boundary
clean.

## Final Decision

Accept.

The contract draws a defensible line between host, runtime, and backend without
leaking backend structure into the public surface, and it preserves the RTDL
kernel model from Goals 386 and 387.
