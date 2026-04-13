# Codex Consensus: Goal 317

Date: 2026-04-12
Workspace: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`

## Scope

Review Goal 317 as a consolidation of the current Linux nearest-neighbor
backend line across PostGIS, Embree, Vulkan, and OptiX.

## Consensus

Codex agrees with the saved Gemini review:

- the report is a technically honest consolidation of already closed Linux
  slices
- the four-backend table is supported by the referenced reports
- the current backend ordering is stated clearly and matches the recorded
  numbers
- the PostGIS role and full-3D `knn_rows` boundary stay explicit instead of
  being blurred into an unsupported acceleration claim

## Most Important Result

At the current large-scale Linux point (`32768 x 32768`):

- fixed-radius:
  - PostGIS `14.218156 s`
  - Embree `1.246501 s`
  - Vulkan `0.057063574029598385 s`
  - OptiX `0.04714724700897932 s`
- bounded-KNN:
  - PostGIS `14.293810 s`
  - Embree `1.362631 s`
  - Vulkan `0.2053437699796632 s`
  - OptiX `0.18232789495959878 s`
- KNN:
  - PostGIS `452.598168 s`
  - Embree `75.158956 s`
  - Vulkan `2.3458052719943225 s`
  - OptiX `2.123993885994423 s`

Current ordering:
- OptiX
- Vulkan
- Embree
- PostGIS

## Honest Boundary

Goal 317 is a consolidation slice only.

It does not close:

- new backend validation beyond the already closed inputs
- Windows nearest-neighbor backend performance
- macOS nearest-neighbor backend performance
- final cross-platform backend maturity

## Decision

Goal 317 is ready to close.
