# Goal 388 Report: v0.6 RT Graph Lowering And Runtime Contract

Date: 2026-04-14
Status: drafted

## Summary

This goal defines the first honest lowering/runtime boundary for RTDL graph
kernels.

The contract must preserve the decisions already made:

- authors write logical RTDL graph kernels
- graph input remains logical CSR
- RT traversal is the candidate-generation engine
- host code still owns outer loops where the paper requires them

The contract must also prevent a regression into detached runtime helpers.

## Lowering Boundary

The lowering contract should accept RTDL graph kernels that use the graph
surface from Goal 386 and produce an internal graph-aware IR with explicit
meaning for:

- graph inputs
- graph traverse modes
- graph predicates
- graph emit schemas
- host-owned versus runtime-owned algorithm state references

At minimum, lowering should preserve the distinction between:

- `graph_expand`
- `graph_intersect`

and between:

- `rt.bfs_discover(...)`
- `rt.triangle_match(...)`

## Runtime Preparation Boundary

The runtime should own the conversion from logical graph inputs into execution
artifacts.

That means runtime preparation is responsible for:

- validating logical CSR inputs
- deriving RT-searchable relation encoding
- building the acceleration structure
- preparing workload-specific metadata needed by the RT traversal step

The host should not need to construct backend-specific RT artifacts directly.

## Host-Owned State

The host remains responsible for algorithm state outside the bounded kernel
step.

### BFS host-owned state

- current frontier
- visited set
- BFS level
- loop termination

### Triangle-count host-owned state

- seed batch schedule
- partial-count aggregation or triangle-row reduction
- outer iteration control

## Runtime-Owned State

The runtime owns state needed to execute one bounded graph RT step:

- normalized graph package
- RT encoding package
- acceleration structure handle
- workload-step invocation contract

The runtime may also own reusable cached structures, as long as the cache does
not leak backend details into the public RTDL kernel surface.

## Backend Hook Contract

The backend-facing contract should be explicit but narrow.

Each backend implementation should receive:

- prepared RT graph structure
- bounded work-item batch
- traverse mode:
  - `graph_expand`
  - `graph_intersect`
- emit schema information

Each backend should return:

- candidate rows or partial rows for later `refine` / `emit`
- or a backend-native bounded result that is semantically equivalent to those
  rows

The public RTDL meaning must remain backend-independent.

For this contract, "semantically equivalent" means:

- the same bounded candidate relation set for the current step
- or the same emitted partial-row content after applying the same declared
  `refine` / `emit` semantics

A backend may choose a different internal representation, but it may not change
which bounded graph-step facts become visible to RTDL at that stage.

## Correctness Hook Contract

The lowering/runtime design must preserve bounded correctness checks.

That means the runtime needs explicit validation hooks for:

- Python bounded truth path
- oracle/native bounded truth path
- PostgreSQL supporting external baseline

For large development-speed runs:

- target RT backend plus PostgreSQL is enough
- Python/oracle may be skipped

For closure:

- bounded Python/oracle parity remains required

## Public API Boundary

The public API should expose:

- RTDL kernels
- logical graph inputs
- host-side loop orchestration helpers only if they are RTDL-kernel-oriented and
  not replacements for the kernel model

The public API should not expose:

- raw backend graph structures
- backend-specific graph helper entry points as the main authoring path
- a detached `bfs(graph, source)` or `triangle_count(graph)` runtime shortcut as
  the primary product story

## Initial Implementation Direction

The safest first implementation path after this goal is:

1. lower RT graph kernels into a graph-aware IR extension
2. implement bounded Python/oracle truth execution for the RT-kernel form
3. only then add backend-specific RT execution mapping

## Non-Goals

This goal does not define:

- final IR data structures in code
- final cache policy
- exact backend ABI layouts
- performance claims
