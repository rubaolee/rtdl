# RTDL v0.4 External Review Report

**Date**: 2026-04-11  
**Verdict**: **Technically Ready for Release**

## Summary

I have performed a comprehensive external review of the RTDL `v0.4` release package at `/Users/rl2025/worktrees/rtdl_v0_4_release_prep`. The package is technically sound, regression-free, and correctly implements the nearest-neighbor workload expansion (`fixed_radius_neighbors`, `knn_rows`).

## Key Review Findings

### 1. Technical Parity (The "Goal 229" Check)
I have verified the native source code for all accelerated backends in the release worktree:
- **Embree**: [rtdl_embree_api.cpp:L610](file:///Users/rl2025/worktrees/rtdl_v0_4_release_prep/src/native/embree/rtdl_embree_api.cpp#L610)
- **OptiX**: [rtdl_optix_workloads.cpp:L1104](file:///Users/rl2025/worktrees/rtdl_v0_4_release_prep/src/native/optix/rtdl_optix_workloads.cpp#L1104)
- **Vulkan**: [rtdl_vulkan_core.cpp:L3459](file:///Users/rl2025/worktrees/rtdl_v0_4_release_prep/src/native/vulkan/rtdl_vulkan_core.cpp#L3459)

> [!NOTE]
> **Refiltering Strategy**: All backends correctly implement the "Candidate Widening + Host Refiltering" strategy. The search radius is increased by `1.0e-4` on the device, and results are refiltered using double-precision logic on the host. This ensures 100% parity with the CPU truth even for points exactly on the search boundary.

### 2. Evidence Integrity
The release package stands on current evidence:
- **Test Suite**: 525 tests passing in the clean worktree (`OK (skipped=59)`).
- **Parity Verified**: Parity is achieved across CPU, Embree, OptiX, and Vulkan.
- **Support Matrix**: The [support_matrix.md](file:///Users/rl2025/worktrees/rtdl_v0_4_release_prep/docs/release_reports/v0_4/support_matrix.md) accurately reflects the status of Linux (Primary), macOS (Local Dev), and Windows (Secondary).

### 3. Documentation Honesty
The [release_statement.md](file:///Users/rl2025/worktrees/rtdl_v0_4_release_prep/docs/release_reports/v0_4/release_statement.md) and [support_matrix.md](file:///Users/rl2025/worktrees/rtdl_v0_4_release_prep/docs/release_reports/v0_4/support_matrix.md) are technically honest:
- They explicitly state that `v0.4.0` is still at the "pre-tag" stage.
- They correctly frame Vulkan as "correctness-first" and "performance-bounded."
- They do not claim benchmark wins over specialized libraries like GEOS or PostGIS, positioning RTDL instead as a flexible multi-backend research tool.

## Risks and Limitations

> [!WARNING]
> **Performance Edge Cases**: While OptiX/Vulkan show massive GPU speedups for KNN, Embree `knn_rows` can sometimes be slower than the CPU oracle for small datasets due to BVH build overhead. This is documented and accepted.
> **Float Epsilon**: Small epsilon differences in float-path calculations (OptiX/Vulkan) are largely neutralized by the Goal 229 refiltering, but users should be aware of the "float approximate" nature of the initial candidate collection.

## Final Recommendation

The package is **CLEARED** for the final release steps:
1. Bump `VERSION` from `v0.3.0` to `v0.4.0`.
2. Commit and tag `v0.4.0`.
3. Declare the release.

---
*Reviewer: Antigravity*
