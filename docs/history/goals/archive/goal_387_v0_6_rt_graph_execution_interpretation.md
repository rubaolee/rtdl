# Goal 387: v0.6 RT Graph Execution Interpretation

## Objective

Define how the RTDL graph kernel surface from Goal 386 maps onto the
SIGMETRICS-2025-style ray-tracing execution model for:

- `bfs`
- `triangle_count`

## Why This Goal Exists

Goal 386 defines what users write. This goal defines what that authoring means
at execution time.

Without this interpretation layer, the graph kernel surface is still only
syntax. The repo needs an explicit explanation of:

- how logical CSR-backed graph data is recast into an RT-searchable structure
- what `traverse` means for RT graph work
- what `refine` means after RT candidate generation
- what `emit` means for the two opening workloads

## Required Outcome

This goal is complete only when the repo contains a bounded execution design
that states:

- the logical graph input versus execution encoding split
- the RT structure build step
- the workload-specific ray/query issuance model
- the workload-specific refine semantics
- the emitted row or partial-count contracts
- what stays host-controlled versus kernel-controlled

## Honesty Boundary

This goal is design only. It does not claim:

- graph lowering is implemented
- RT graph execution works on any backend yet
- the exact primitive geometry is frozen forever

## Required Deliverables

- an execution-interpretation report in `docs/reports/`
- a Gemini review handoff and response file
- a Claude review handoff and response file
- a Codex closure note after reading the external reviews
