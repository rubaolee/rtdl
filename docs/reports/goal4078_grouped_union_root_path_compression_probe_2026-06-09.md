# Goal4078 Grouped-Union Root Path Compression Probe

Date: 2026-06-09

## Status

Implemented as a native OptiX probe; pod build/timing pending.

## Purpose

Goal4074 showed that RT-DBSCAN's recommended route is dominated by the native fixed-radius grouped-union continuation. Goal4078 tests a generic union-find improvement inside that native continuation: opportunistic monotonic path compression while reading parent roots.

This is not DBSCAN-specific. It applies to the generic prepared fixed-radius grouped-union primitive used by RT-DBSCAN's recommended route.

## Change

The OptiX grouped-union device root lookup now performs path halving:

- read `next = parent[root]`;
- read `grand = parent[next]`;
- if `grand < next`, apply `atomicMin(parent + root, grand)`;
- continue walking toward the root.

The update is monotonic because the grouped-union parent policy already uses smaller component roots as canonical representatives. The runtime metadata records:

`grouped_union_root_path_compression_policy = monotonic_atomic_min_path_halving_default`

## Acceptance Rule

This is a probe. It should be kept only if pod evidence shows stable correctness and a meaningful improvement or at least no material regression on the recommended route. If the extra atomics outweigh shorter root chains, the change should be reverted and recorded as negative evidence.

## Boundary

This does not add native ABI, app-specific engine logic, automatic dispatch, public speedup wording, release authorization, broad RT-core claims, whole-app claims, or true-zero-copy claims.

