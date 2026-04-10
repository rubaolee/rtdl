# Goal 197: Fixed-Radius Neighbors DSL Surface

Date: 2026-04-10
Status: planned

## Goal

Add the public DSL/Python surface for the first `v0.4` workload:

- `fixed_radius_neighbors`

This goal covers the user-facing language/API layer only.

## Why this goal exists

Goal 196 froze the public contract.

The next step is to let users write RTDL kernels against that contract without
yet claiming that the lowering or runtime paths exist.

That means:

- the predicate must exist in the public API
- the package export must exist
- the language docs must mention the new surface honestly
- the lowering path must reject it explicitly and truthfully until later goals

## Required result

This goal is complete when:

- `rt.fixed_radius_neighbors(...)` exists in the public API
- the package export is available from `import rtdsl as rt`
- a kernel using that predicate compiles
- lowering rejects it with an explicit planned-surface message
- language docs describe it as planned/not-yet-lowered
- bounded tests prove all of the above

## Non-goals

This goal does not:

- add reference execution
- add native backend execution
- add public examples outside the language docs
- claim runtime support
