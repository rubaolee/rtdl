# Goal 230: Clean v0.4 Release-Prep Workspace

Date: 2026-04-10
Status: implemented

## Goal

Create and verify a clean release-prep workspace for `v0.4` so final release
goals can proceed without the unrelated local docs reorganization churn present
in the primary working checkout.

## Acceptance

- a fresh git worktree exists at the current pushed `main`
- the worktree is globally clean
- the worktree is confirmed to contain the post-Goal-229 blocker fix
- a focused verification slice passes in that clean worktree

## Boundary

- This goal does not release `v0.4.0`
- This goal only establishes a trustworthy clean workspace for the remaining
  release-prep goals
