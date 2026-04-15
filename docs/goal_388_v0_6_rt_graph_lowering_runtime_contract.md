# Goal 388: v0.6 RT Graph Lowering And Runtime Contract

## Objective

Define the lowering and runtime contract that turns the RT graph kernel surface
and execution interpretation into an implementable RTDL boundary.

## Why This Goal Exists

Goal 386 defines what users write.

Goal 387 defines what that authoring means at execution time.

The remaining missing piece before implementation is the contract between:

- RTDL graph kernels
- lowering
- runtime preparation
- backend execution

Without this goal, graph work can still drift back into detached helper APIs or
backend-specific ad hoc paths.

## Required Outcome

This goal is complete only when the repo contains a bounded contract for:

- graph kernel AST / IR expectations
- logical graph input normalization
- RT encoding preparation boundary
- runtime-owned state versus host-owned state
- backend-facing execution hooks
- bounded correctness hooks for Python/oracle/PostgreSQL validation

## Honesty Boundary

This goal is design only. It does not claim:

- graph lowering is implemented
- any backend executes RT graph kernels today
- the full compiler pipeline is frozen

## Required Deliverables

- a lowering/runtime-contract report in `docs/reports/`
- a Gemini review handoff and response file
- a Claude review handoff and response file
- a Codex closure note after reading the external reviews
