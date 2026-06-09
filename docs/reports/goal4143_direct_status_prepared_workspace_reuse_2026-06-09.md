# Goal4143 - Direct-Status Prepared Workspace Reuse

Date: 2026-06-09

Verdict: implementation-complete-pod-needed

## Purpose

Goal4143 attacks the remaining RT-DBSCAN direct-status replay overhead without
adding DBSCAN-specific engine logic.

The prepared direct-status component-signature path already reuses point,
partition, and AABB columns. The replay helper still allocated parent and
counter arrays for every component-signature run. Goal4143 moves those temporary
arrays into the prepared handle and resets them with a generic device kernel.

## Change

The prepared direct-status handle now owns reusable device workspaces:

- `parents`
- `changed`
- `safe_skip_count`
- `safe_full_count`
- `ambiguous_count`
- `comparison_count`
- `positive_count`

The direct-status union helper accepts optional workspaces and uses
`reset_direct_partition_status_workspaces_kernel` to reset parent identity and
counters before each replay.

The non-prepared direct-status helper remains available and uses the same reset
path with newly allocated arrays.

## Boundary

This is a generic fixed-radius partition/component workspace reuse change. It
does not add DBSCAN-specific native logic, app-specific engine logic, a native
ABI, hidden dispatch, automatic partner selection, automatic factor selection,
release authorization, public speedup authorization, broad RT-core wording,
paper-reproduction claims, AMD claims, or true-zero-copy claims.

Pod timing is required before making any performance conclusion.
