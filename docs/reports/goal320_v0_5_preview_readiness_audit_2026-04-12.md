# Goal 320 Report: v0.5 Preview Readiness Audit

Date:
- `2026-04-12`

Goal:
- assess whether the current `v0.5` line is honestly ready for a preview-level
  release claim

## Inputs Considered

Primary current-state inputs:
- `docs/reports/comprehensive_v0_5_transition_audit_report_2026-04-12.md`
- `docs/release_reports/v0_5_preview/support_matrix.md`
- `docs/reports/goal314_v0_5_current_linux_nn_perf_report_2026-04-12.md`
- `docs/reports/goal317_v0_5_current_linux_4backend_nn_perf_report_2026-04-12.md`
- `docs/reports/goal319_v0_5_cross_platform_embree_correctness_2026-04-12.md`
- previously closed CPU/oracle, PostGIS, Embree, OptiX, and Vulkan `v0.5`
  nearest-neighbor goals

## What Is Closed

### Surface

The 3D nearest-neighbor trio is closed on the RTDL side for:
- `fixed_radius_neighbors`
- `bounded_knn_rows`
- `knn_rows`

### Linux backend line

On Linux, the current backend story is materially real:
- Python reference truth path
- native CPU/oracle correctness baseline
- PostGIS external correctness/timing anchor
- Embree accelerated CPU backend
- OptiX accelerated GPU backend
- Vulkan accelerated GPU backend

### Linux evidence

The repo now contains same-scale large Linux nearest-neighbor evidence at
`32768 x 32768` on real KITTI-derived packages.

Current Linux ordering:
- `OptiX < Vulkan < Embree < PostGIS`

### Cross-platform bounded correctness

Windows and local macOS are not part of the Linux performance story, but they
are no longer vague placeholders.

Bounded Embree correctness on the 3D nearest-neighbor trio is verified on:
- Linux
- local macOS
- Windows

## What Is Only Bounded

- Windows support is bounded to Embree correctness/bring-up, not large-scale NN
  performance
- local macOS support is bounded to Embree correctness/development checks, not
  large-scale NN performance
- Vulkan is accepted in the current Linux preview story but still bounded as a
  cross-platform maturity claim
- cuNSearch remains a bounded external comparison path, not a clean universal
  backend claim

## What Is Still Missing For A Final v0.5 Release

- final release statement for `v0.5`
- final release-facing support matrix instead of preview matrix
- final consolidated audit packaging the current goal chain into one release
  closure artifact
- explicit final decision on whether any bounded external comparison paths stay
  in the release-facing top-level story or move to supporting documentation only

## Decision

### Preview readiness

Decision:
- `preview-ready`

Reason:
- the Linux nearest-neighbor backend story is already real
- the main correctness line is closed
- the accelerated backend line is closed on Linux
- the support matrix is now explicit and honest
- Windows/macOS bounded correctness status is explicit rather than implied

### Final release readiness

Decision:
- `not final-release-ready`

Reason:
- the repo still lacks the final release-facing closure artifacts
- the current public statement is still a preview state, not a final sign-off

## Honest Summary

The current `v0.5` line is ready to be described as a real preview-quality
state:

- real 3D nearest-neighbor surface
- real Linux backend closure
- real large-scale Linux backend evidence
- bounded cross-platform Embree correctness

It is not yet ready to be described as fully signed off final `v0.5` release
state.
