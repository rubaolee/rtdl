# Goal 342 Report: v0.6 BFS First Backend Closure

Date: 2026-04-13

## Summary

This slice defines the intended first backend closure order for `bfs` in
`v0.6`.

## Recommended sequence

1. Python truth path
2. first native/runtime closure
3. first accelerated backend closure on Linux
4. bounded Linux performance and correlation review

## Why this is the right order

It matches the successful `v0.5` discipline:

- semantics first
- backend correctness second
- acceleration claims later

For the first graph workload, that discipline matters even more because the new
surface is not yet battle-tested.

## Concrete backend interpretation

For the opening BFS line, the intended backend meanings are:

- native/runtime closure:
  - RTDL's first compiled CPU implementation for the single-source CSR BFS
    truth-path contract
- accelerated backend closure:
  - the first Linux accelerated backend chosen for BFS after the compiled CPU
    baseline is row-correct

The specific accelerated backend should be selected explicitly in its own goal
slice rather than implied here.

## Closure criteria

For this plan, a backend is only "closed" when:

- it matches the bounded BFS truth-path semantics
- its row/output parity is proven on the selected bounded cases
- its boundary language is documented honestly
- a saved external review and Codex consensus exist for that slice

## Scope confirmation

The first backend closures in this sequence are for:

- single-source BFS
- CSR input
- `uint32_t` vertex IDs
- simple graphs

No broader BFS or graph-surface claim is implied by this opening backend plan.

## Performance review boundary

The first bounded Linux performance and correlation review should mean:

- one explicit dataset family or bounded synthetic graph set
- one explicit backend comparison table
- correctness already closed before timing claims
- clear statement of what "correlation" means against the chosen truth path

## Platform boundary

- Linux:
  - first backend and performance platform
- Windows:
  - correctness-first later
- macOS:
  - correctness-first later

## Recommendation

Use the same truth-path-first backend sequence for BFS that worked for the
nearest-neighbor line in `v0.5`.
