# Goal 220 Report: v0.4 GPU Status Refresh

Date: 2026-04-10
Status: completed

## Summary

This slice updates the live `v0.4` status story so it no longer claims that the
nearest-neighbor GPU line is out of scope.

The refreshed support matrix now reflects the reopened bar established in Goal
215 and the engineering state reached through Goals 216 through 219:

- OptiX is part of the accepted `v0.4` execution closure surface
- Vulkan is part of the accepted `v0.4` execution closure surface under a
  correctness-first, bounded-performance interpretation
- both new nearest-neighbor workloads are described as running across CPU,
  Embree, OptiX, and Vulkan

## Files updated

- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_4/support_matrix.md`
- `/Users/rl2025/rtdl_python_only/docs/goal_220_v0_4_gpu_status_refresh.md`

## Why this matters

Without this refresh, the live `v0.4` pages still describe the older
CPU/oracle-plus-Embree interpretation and are therefore stale against the
reopened GPU-required milestone.

## Honest boundary

This goal updates status language only.

It does not itself close:

- external review for Goals 217 through 219
- benchmark/performance evidence for the reopened GPU line
- final `v0.4` re-audit
