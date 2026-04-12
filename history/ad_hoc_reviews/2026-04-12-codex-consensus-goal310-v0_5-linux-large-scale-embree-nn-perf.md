# Codex Consensus: Goal 310

Date: 2026-04-12
Workspace: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`

## Scope

Review Goal 310 as the first honest Linux large-scale Embree nearest-neighbor
performance slice on duplicate-free KITTI data, including the first KNN
optimization required by that scale.

## Consensus

Codex agrees with the saved Gemini review:

- the Linux benchmark is technically coherent
- the setup-versus-hot timing split is the correct reporting shape
- parity against the native CPU/oracle baseline is preserved honestly
- the KNN optimization is defensible and materially improves large-scale Embree
  behavior
- the report keeps the platform boundary explicit and does not overclaim
  Windows or final performance closure

## Most Important Result

At `16384` points on duplicate-free KITTI packages:

- Embree remains faster than the native CPU/oracle path for:
  - `fixed_radius_neighbors`
  - `bounded_knn_rows`
- Embree `knn_rows` improved from about `45.68 s` hot median to about
  `18.86 s` hot median after the top-`k` radius-shrinking optimization
- that path is still slower than the native CPU/oracle `knn_rows` baseline at
  this scale, so more KNN optimization work is still required

## Honest Boundary

Goal 310 closes a Linux large-scale performance slice only.

It does not close:

- Windows large-scale Embree performance
- macOS large-scale Embree performance
- final Embree KNN optimization completeness
- broader backend performance closure beyond Embree

## Decision

Goal 310 is ready to close.
