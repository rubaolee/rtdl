# Goal 231: v0.4 Release-Surface Alignment

Date: 2026-04-10
Status: implemented

## Goal

Align the clean worktree's `v0.4` release package with the actual post-Goal-229
state so the release-facing docs no longer describe stale pre-GPU or pre-fix
conditions.

## Acceptance

- the `v0.4` release statement reflects CPU/oracle, Embree, OptiX, and Vulkan
  closure for the nearest-neighbor workloads
- the audit and tag-preparation docs preserve the Goal 228 heavy benchmark and
  Goal 229 boundary-fix evidence
- the final release handoff hub no longer claims local-only banner/docs-reorg
  changes that are not present in the clean release-prep worktree

## Boundary

- This goal is docs-only
- It does not bump `VERSION` or create a tag
