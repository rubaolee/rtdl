# Goal 341 Report: v0.6 Triangle Count Truth Path

Date: 2026-04-13

## Summary

This slice defines the intended opening truth-path contract for
`triangle_count` in `v0.6`.

## Input assumptions

- graph layout:
  - CSR
- vertex IDs:
  - `uint32_t`
- graph type:
  - simple undirected graph
- adjacency ordering:
  - sorted neighbor lists within each CSR segment

## Initial triangle-count truth semantics

The opening truth path should prioritize deterministic count semantics over
backend concerns.

Recommended opening output:

- one scalar `uint64_t` triangle count for the full graph

Counting rule:

- each unique undirected triangle should be counted exactly once

Edge-case rule:

- an empty graph should produce a triangle count of `0`

## Why this is the right first truth path

It keeps the first graph-counting workload narrow:

- one graph layout
- one graph class
- one count convention

That removes the usual ambiguity around duplicate counting and directed-graph
variants.

## Recommendation

Proceed with a CSR-based simple-undirected triangle-count truth path as the
second `v0.6` implementation workload.
