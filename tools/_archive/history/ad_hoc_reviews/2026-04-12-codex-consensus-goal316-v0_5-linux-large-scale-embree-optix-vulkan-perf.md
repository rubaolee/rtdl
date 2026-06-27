# Codex Consensus: Goal 316

Date: 2026-04-12
Workspace: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`

## Scope

Review Goal 316 as the first Linux large-scale accelerated backend table at
`32768 x 32768` across Embree, OptiX, and Vulkan on duplicate-free real KITTI
data.

## Consensus

Codex agrees with the saved Gemini review:

- the checked-in benchmark script and saved Linux summary support the reported
  `32768 x 32768` table
- the initial Vulkan KNN mismatch is described honestly
- the slack-and-exact-finalize repair is technically coherent
- the repaired Vulkan KNN line becomes parity-clean on the saved package pair
- the PostGIS and platform boundaries are explicit

## Most Important Result

At `32768 x 32768` on duplicate-free
`2011_09_26_drive_0014_sync` frame `0000000000` vs `0000000004`:

- fixed-radius:
  - Embree `1.2434870510478504 s`
  - OptiX `0.04714724700897932 s`
  - Vulkan `0.057063574029598385 s`
- bounded-KNN:
  - Embree `1.3748652570066042 s`
  - OptiX `0.18232789495959878 s`
  - Vulkan `0.2053437699796632 s`
- KNN:
  - Embree `75.73891976498999 s`
  - OptiX `2.123993885994423 s`
  - Vulkan `2.3458052719943225 s`

Parity is clean across Embree, OptiX, and Vulkan for all three workloads.

## Honest Boundary

Goal 316 closes only the accelerated Linux backend race for this saved `32768`
package pair.

It does not close:

- PostGIS re-validation inside this slice
- Windows large-scale Vulkan performance
- macOS large-scale Vulkan performance
- final cross-platform backend maturity

## Decision

Goal 316 is ready to close.
