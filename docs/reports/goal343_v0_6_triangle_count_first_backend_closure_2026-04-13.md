# Goal 343 Report: v0.6 Triangle Count First Backend Closure

Date: 2026-04-13

## Summary

This slice defines the intended first backend closure order for
`triangle_count` in `v0.6`.

## Recommended sequence

1. Python truth path
2. first compiled CPU/native closure
3. first accelerated backend closure on Linux
4. bounded Linux performance and correlation review

## Why this is the right order

It preserves the working discipline established in `v0.5` and now reused in
the BFS backend plan:

- semantics first
- backend correctness second
- acceleration claims later

For triangle counting, that ordering matters because count semantics can drift
silently if backend work begins before the truth-path boundary is fully locked.

## Concrete backend interpretation

For the opening triangle-count line, the intended backend meanings are:

- compiled CPU/native closure:
  - RTDL's first compiled CPU implementation for the CSR simple-undirected
    triangle-count truth-path contract
- accelerated backend closure:
  - the first Linux accelerated backend chosen for triangle count after the
    compiled CPU baseline is count-correct

The specific accelerated backend should be selected explicitly in its own goal
slice rather than implied here.

Likely candidate families for that later selection include:

- Vulkan
- OptiX
- CUDA-class compute paths if a non-RT-core route is justified

This goal does not choose among them yet.

## Closure criteria

For this plan, a backend is only "closed" when:

- it matches the bounded triangle-count truth-path semantics
- its output parity is proven on selected bounded cases, including:
  - empty graph
  - single-triangle graph
  - graph with zero triangles
  - at least one bounded sparse graph
  - at least one bounded denser graph
- its boundary language is documented honestly
- a saved external review and Codex consensus exist for that slice

## Scope confirmation

The first backend closures in this sequence are for:

- scalar graph-level triangle count
- CSR input
- `uint32_t` vertex IDs
- `uint64_t` output count
- simple undirected graphs
- sorted neighbor lists

No broader graph-analytics claim is implied by this opening backend plan.

## Performance review boundary

The first bounded Linux performance and correlation review should mean:

- one explicit dataset family or bounded synthetic graph set
- one explicit backend comparison table including at least:
  - elapsed time
  - graph size summary
  - backend name
- correctness already closed before timing claims
- clear statement of what "correlation" means against the chosen truth path

For the opening slice, "correlation" should mean:

- the timed backend produces the same bounded triangle-count result as the
  truth path on the selected evaluation cases

## Recommendation

Use the same truth-path-first backend sequence for triangle count that is now
defined for BFS, while keeping the triangle-count contract narrow and explicit.
