# Gemini Next-Gen Workload Plan Review

Date: `2026-04-04`

Source document reviewed:

- [/Users/rl2025/gemini-work/RTDL_NextGen_Workload_Support_Plan_2026.md](/Users/rl2025/gemini-work/RTDL_NextGen_Workload_Support_Plan_2026.md)

## Purpose

This memo preserves the current Gemini proposal and the current Codex review of
that proposal. It is a local review note only. It is not a published roadmap
decision.

## Gemini Proposal Summary

Gemini proposes extending RTDL beyond its current RayJoin-oriented slice toward
a broader non-graphics tree-traversal platform.

Main proposed feature groups:

1. Data-to-space mappers
   - map abstract data into RT-friendly geometric/task layouts
   - example direction: Hilbert-style index mapping

2. Programmable refinement
   - user-visible `@rt.refine`-style hooks for post-hit exact logic
   - intended to support high-precision or domain-specific checks

3. Non-Euclidean and nearest-neighbor queries
   - nearest / radius style operators
   - beyond simple segment/polygon intersection style workloads

4. Hierarchical tree alignment APIs
   - direct mapping of non-geometry trees to traversal hardware
   - examples named in the proposal include B-trees, radix trees, and page tables

5. Architectural simulation export
   - backend/export path for simulation environments such as Vulkan-Sim

Gemini frames these as a path from a spatial-join-focused DSL toward a more
general “tree-traversal language.”

## Codex Review

### Overall judgment

Useful as exploratory research input.

Not acceptable as an authoritative near-term roadmap without revision.

### What is strong

- It correctly identifies that RTDL may eventually grow beyond spatial joins.
- It highlights plausible future workload directions:
  - data-to-space mapping
  - nearest/radius style queries
  - broader tree-search workloads
- It is valuable as a brainstorming memo for post-v0.1 research.

### Main problems

1. Strategic overstatement

The proposal says RTDL “must evolve” into a generalized tree-traversal
language. That is stronger than the current accepted project position.

Current accepted position is narrower:

- RTDL v0.1 is a bounded non-graphical RT DSL/runtime
- RayJoin-style workloads are the validated vertical slice
- broader expansion is possible, but not yet committed as the immediate product
  identity

2. Unsafe abstraction boundary around programmable refinement

The proposal treats `@rt.refine` as though user-injected native refine logic
would be a straightforward DSL feature.

In the current project, refine behavior is tightly bound to:

- correctness contracts
- backend/runtime ownership
- cross-backend parity expectations
- ABI stability
- auditability
- security boundaries

So this is not a small language extension. It would be a major architecture and
trust-model change.

3. Near-term and long-term ideas are mixed together

Some ideas are plausible near-term research extensions, while others are much
more speculative:

- near-term plausible:
  - data-to-space mapping helpers
  - nearest/radius query surface
  - additional bounded workload classes
- longer-term speculative:
  - direct hardware-tree alignment APIs
  - Vulkan-Sim export
  - broader architectural-simulation workflow

The proposal should separate those classes explicitly.

## Recommended Use

Keep this Gemini document as:

- exploratory design input
- research brainstorming material
- candidate source for a future RTDL post-v0.1 roadmap discussion

Do not use it as:

- the canonical live roadmap
- an accepted implementation plan
- evidence that the project has already chosen a generalized tree-accelerator
  direction

## Recommended Rewrite Direction

If this material is turned into a formal RTDL planning document later, it
should be split into two sections:

### 1. Near-term feasible RTDL extensions

- data-to-space helpers
- nearest / radius query support
- carefully bounded new workload families that fit the current audit model

### 2. Long-term speculative research directions

- programmable native refinement
- direct tree/hardware alignment APIs
- simulation/export targets such as Vulkan-Sim

## Current Conclusion

The Gemini proposal is worth preserving.

The current Codex conclusion is:

- **keep as exploratory memo**
- **do not adopt as official roadmap without rewrite**
