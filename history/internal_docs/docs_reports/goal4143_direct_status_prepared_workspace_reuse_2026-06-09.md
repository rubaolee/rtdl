# Goal4143 - Direct-Status Prepared Workspace Reuse

Date: 2026-06-09

Verdict: superseded-by-goal4144-negative-pod-result

## Purpose

Goal4143 tested an attack on the remaining RT-DBSCAN direct-status replay overhead without
adding DBSCAN-specific engine logic.

The prepared direct-status component-signature path already reuses point,
partition, and AABB columns. The replay helper still allocated parent and
counter arrays for every component-signature run. Goal4143 moves those temporary
arrays into the prepared handle and resets them with a generic device kernel.

## Candidate Change

The candidate prepared direct-status handle owned reusable device workspaces:

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

The non-prepared direct-status helper remained available and used the same reset
path with newly allocated arrays.

## Supersession

Goal4144 measured this candidate on the pod and rejected it as a performance
default. Replay timing was essentially neutral and one-shot total timing got
worse because workspace allocation moved into the prepare phase. The active
runtime is therefore restored to the pre-Goal4143 allocation path while keeping
the Goal4143/Goal4144 evidence as a documented negative probe.

## Boundary

This is a generic fixed-radius partition/component workspace reuse change. It
does not add DBSCAN-specific native logic, app-specific engine logic, a native
ABI, hidden dispatch, automatic partner selection, automatic factor selection,
release authorization, public speedup authorization, broad RT-core wording,
paper-reproduction claims, AMD claims, or true-zero-copy claims.

Goal4144 provides the required pod timing. Do not promote prepared workspace
reuse as the default direct-status route.
