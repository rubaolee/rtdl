# Goal 230 Report: Clean v0.4 Release-Prep Workspace

Date: 2026-04-10
Status: implemented

## Summary

The primary checkout contains a large unrelated local docs reorganization and
deletion set that is not part of the pushed `v0.4` engineering line. That makes
it a poor base for final release-prep work.

This goal creates a separate clean git worktree from current `origin/main` and
uses that as the new workspace for the remaining release goals.

## Workspace

- source repo:
  - `/Users/rl2025/rtdl_python_only`
- clean release-prep worktree:
  - `/Users/rl2025/worktrees/rtdl_v0_4_release_prep`
- branch:
  - `codex/v0_4_release_prep`
- checked-out commit:
  - `2d51d38`

## Findings

- the clean worktree is globally clean:
  - `## codex/v0_4_release_prep...origin/main`
- the clean worktree is exactly aligned with pushed `main`
- the post-Goal-229 blocker fix is present in the clean worktree
- the clean worktree still reflects the current committed docs surface, not the
  unrelated local docs reorganization from the primary checkout

## Verification

Focused release-prep verification in the clean worktree:

- `PYTHONPATH=src:. python3 -m unittest tests.goal228_v0_4_nearest_neighbor_perf_harness_test tests.goal200_fixed_radius_neighbors_embree_test tests.goal216_fixed_radius_neighbors_optix_test tests.goal218_fixed_radius_neighbors_vulkan_test`
  - `Ran 28 tests`
  - `OK (skipped=18)`

## Outcome

The remaining `v0.4` release-prep work should proceed in:

- `/Users/rl2025/worktrees/rtdl_v0_4_release_prep`

That isolates the release path from unrelated local dirt in the primary
checkout while preserving the latest pushed `v0.4` technical state.
