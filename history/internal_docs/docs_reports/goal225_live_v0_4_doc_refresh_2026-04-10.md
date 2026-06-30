# Goal 225 Report: Live v0.4 Doc Refresh (2026-04-10)

## Scope

This slice updates only the live user-facing `v0.4` documentation surface:

- `README.md`
- `docs/README.md`
- `docs/features/fixed_radius_neighbors/README.md`
- `docs/features/knn_rows/README.md`
- `docs/quick_tutorial.md`
- `docs/release_facing_examples.md`
- `docs/rtdl/dsl_reference.md`
- `docs/workloads_and_research_foundations.md`

## Changes

- clarified that the `v0.4` nearest-neighbor line is an active preview reopened
  for GPU completion
- updated feature-home pages so both nearest-neighbor workloads show OptiX and
  Vulkan as implemented backends
- updated the DSL reference so accelerated support is described as existing
  across Embree, OptiX, and Vulkan
- expanded the release-facing example page so backend-selection examples cover
  both nearest-neighbor workloads
- corrected the research-foundations summary so it no longer claims the Jaccard
  line lacks a named paper anchor after the pathology-paper mapping was added
- after external review, fixed the remaining `docs/rtdl/dsl_reference.md`
  contradiction that still claimed accelerated `knn_rows` closure was pending
- removed the stale `multiple backends` item from the DSL reference non-goals
  list because it contradicted RTDL's actual multi-backend surface

## Verification

- docs-only slice
- no runtime code changed
- verification consists of direct cross-page consistency review plus external
  review handoff
- Gemini's first review found two real blocking contradictions in the DSL
  reference; both were fixed in this same goal before closure
