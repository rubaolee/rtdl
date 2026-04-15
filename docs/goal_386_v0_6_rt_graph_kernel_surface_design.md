# Goal 386: v0.6 RT Graph Kernel Surface Design

## Objective

Define the RTDL kernel authoring surface for the paper-aligned `v0.6` graph
line so that users can express graph workloads through RTDL kernels rather than
through detached helper APIs.

## Why This Goal Exists

Goal 385 fixed the version direction, but the current DSL reference is still
geometry-only. Before any runtime or backend work can be honest, the repo needs
an explicit answer to:

- what graph inputs look like in RTDL
- what graph traversal means inside the RTDL kernel model
- how `bfs` and `triangle_count` fit the `input -> traverse -> refine -> emit`
  discipline, or where the graph line extends it

## Required Outcome

This goal is complete only when the repo contains a bounded design for:

- graph input declarations
- graph-oriented traverse/refine/emit semantics
- host-vs-kernel responsibility boundaries that stay consistent with the paper
- logical-CSR to RT-encoded-BVH mapping
- how a user writes a minimal RTDL `bfs` kernel
- how a user writes a minimal RTDL `triangle_count` kernel
- which parts reuse the current DSL and which parts are new `v0.6` additions

## Honesty Boundary

This goal is design only. It does not claim:

- graph lowering is implemented
- graph kernels execute today
- any backend supports the graph kernels yet

## Required Deliverables

- a design report in `docs/reports/`
- explicit BFS and triangle-count kernel examples in design form
- a Gemini review handoff and response file
- a Claude review handoff and response file
- a Codex closure note after reading the Gemini review
