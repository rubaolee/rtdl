# Goal 339 Report: v0.6 Graph Data / Layout Contract

Date: 2026-04-13

## Summary

This slice defines the intended starting graph representation boundary for
`v0.6`.

## Proposed initial contract

The first `v0.6` graph workloads should assume a bounded, explicit graph input
representation owned by the application layer and passed into RTDL in a stable
materialized form.

Initial expectation:

- application owns raw graph ingestion and preprocessing
- RTDL owns the bounded workload semantics and backend execution over that
  prepared graph representation

## Canonical starting layout

The first `v0.6` graph contract should explicitly use:

- **CSR (Compressed Sparse Row)**

for the initial public graph materialization boundary.

Why:

- it is the standard sparse graph traversal layout
- it is deterministic and truth-path friendly
- it avoids a vague "materialized form" contract that would drift during
  implementation

The first bounded RTDL graph surface should therefore assume application-owned
conversion into CSR before workload execution.

## Initial type and topology assumptions

The first contract should be explicit about:

- vertex IDs:
  - `uint32_t`
- edge / adjacency indices:
  - `uint32_t`
- topology:
  - simple graphs only for the first `v0.6` slice
  - no self-loops
  - no multi-edges

These assumptions can be widened later, but should not remain implicit during
the first truth-path work.

## Workload-specific contract notes

### `bfs`

The first `bfs` truth path should assume:

- CSR graph input
- one explicit frontier representation at the public boundary
- first recommendation:
  - frontier as a materialized list of vertex IDs

This is simpler and more explicit than bitset-style variation for the opening
slice.

### `triangle_count`

The first `triangle_count` truth path should assume:

- CSR graph input
- undirected simple graphs
- sorted neighbor lists in CSR adjacency segments

That keeps triangle semantics deterministic and removes duplicate-count
ambiguity in the first slice.

## Why this is the right starting point

It matches RTDL's existing positioning:

- RTDL remains a language/runtime core
- surrounding application orchestration can stay in Python
- the workload contract stays explicit instead of hiding graph ingest
  complexity inside the runtime from day one

## Contract direction

The first contract should prefer:

- one explicit graph representation
- deterministic semantics
- truth-path friendliness

It should avoid:

- multiple graph encodings in the first slice
- hidden auto-conversion rules
- backend-specific input formats at the public language surface
- implicit graph-property assumptions

## Recommendation

Adopt a single bounded graph data/layout contract before beginning BFS and
triangle-count implementation:

- CSR as the canonical starting layout
- `uint32_t` vertex and adjacency indexing
- simple-graph assumptions
- explicit frontier and triangle semantics
