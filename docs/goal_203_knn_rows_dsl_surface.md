# Goal 203: KNN Rows DSL Surface

Date: 2026-04-10
Status: planned

## Goal

Add the public DSL/Python surface for the second `v0.4` workload:

- `knn_rows`

This goal covers the user-facing language/API layer only.

## Why this goal exists

Goal 202 froze the public contract.

The next step is to let users write RTDL kernels against that contract without
yet claiming that the runtime paths exist.

That means:

- the predicate must exist in the public API
- the package export must exist
- the language docs must mention the new surface honestly
- the lowering path must produce a stable plan shape for later runtime work

## Required result

This goal is complete when:

- `rt.knn_rows(...)` exists in the public API
- the package export is available from `import rtdsl as rt`
- a kernel using that predicate compiles
- lowering produces an explicit `knn_rows` execution plan
- language docs describe the surface honestly
- bounded tests prove all of the above

## Non-goals

This goal does not:

- add reference execution
- add native backend execution
- add public examples outside the language docs
- claim runtime support
