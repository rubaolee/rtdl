# Goal 287 Report

Date: 2026-04-12
Workspace: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`

## Summary

Goal 287 added a bounded selector that finds the first duplicate-free KITTI frame pair within a search window.

## What Changed

- `src/rtdsl/rtnn_kitti_selector.py`
  - added `KittiDuplicateFreePair`
  - added `find_duplicate_free_kitti_pair(...)`
- `tests/goal287_kitti_duplicate_free_selector_test.py`
  - shows the selector skips a duplicate pair and chooses the next clean pair

## Honest Read

This is a bounded selection utility, not a paper-level dataset policy.

What it does:

- starts from a chosen query frame index
- scans forward within a bounded search window
- builds the bounded point packages for each candidate pair
- rejects any pair with exact cross-package duplicate points
- returns the first clean pair

That gives the cuNSearch line a practical strict-parity path without pretending duplicate-point cases are solved.
