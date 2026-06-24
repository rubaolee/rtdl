# Goal 233 Report: Final Release Decision Package

Date: 2026-04-10
Status: implemented

## Summary

The clean release-prep worktree now holds the complete pre-release evidence
package for `v0.4`.

That package includes:

- whole-line Gemini and Claude audits
- reopened GPU closure for:
  - `fixed_radius_neighbors`
  - `knn_rows`
- the heavy Linux nearest-neighbor benchmark
- the Goal 229 accelerated fixed-radius boundary repair
- final clean-worktree pre-release verification:
  - `Ran 525 tests in 116.882s`
  - `OK (skipped=59)`

## Current Technical Verdict

`v0.4` is technically ready for release decision in this clean worktree.

What that means:

- the nearest-neighbor line is closed across:
  - CPU/oracle
  - Embree
  - OptiX
  - Vulkan
- the later heavy-case blocker is fixed
- the release-surface docs now match the post-Goal-229 truth
- the clean packaging checkout is verified

## Explicit Remaining Action

The remaining step is not an engineering unknown. It is a user-authorized
release action:

1. bump `VERSION` from `v0.3.0` to `v0.4.0`
2. create the `v0.4.0` tag
3. publish that final release state

## Explicit Non-Actions

This goal does **not** do any of the following:

- bump `VERSION`
- create a tag
- declare release without authorization

## Release-Prep Workspace

- path:
  - `/Users/rl2025/worktrees/rtdl_v0_4_release_prep`
- branch:
  - `codex/v0_4_release_prep`

## Outcome

The engineering side of `v0.4` is complete enough that the project is now at a
clean user-decision point rather than an engineering-blocked point.
