# Goal4155 - Predicate-Aware Direct-Status Implementation Plan

Date: 2026-06-09

Verdict: implementation-plan-ready

## Purpose

Goal4153 showed that the fast direct-status component-signature route cannot be
compared with the conservative RT-DBSCAN route because the contracts differ. The
next implementation target is a generic predicate-aware fixed-radius grouped
union route that preserves the native-engine app-agnostic boundary while
allowing RT-DBSCAN to supply core flags from user/app code.

## Generic Contract

Inputs:

- point coordinate columns
- prepared partition columns and partition AABBs
- caller-supplied vertex predicate flags
- fixed-radius threshold
- explicit convergence mode

Operations:

- classify partition pairs as safe-skip, safe-full, or ambiguous
- union safe-full partitions only when both partitions contain predicate-true
  vertices
- for ambiguous partition pairs, scan point pairs and union only when both
  endpoints are predicate-true and within radius
- assign predicate-false border vertices through an explicit deterministic neighbor-root policy

Outputs:

- point ids
- component labels with `-1` for unassigned/noise vertices
- predicate flags
- optional component-size signature
- status counters: safe-skip, safe-full, ambiguous, comparisons, positive
  predicate edges, border assignments, convergence mode, final changed flag

## RT-DBSCAN Use

RT-DBSCAN should remain app code:

- RTDL/OptiX count-threshold primitive can produce core flags.
- The new generic predicate-aware direct-status continuation consumes those
  flags.
- The benchmark app compares its resulting cluster signature against the
  current grouped-stream/Numba route.

No native ABI may contain `dbscan`, `cluster`, `core`, `border`, or `noise`.
Those words can appear in the benchmark app and reports only.

## Acceptance

Before any route guidance changes:

1. Local/static tests must prove the new surface is generic and fail-closed.
2. Pod smoke at small scale must match the current route signature.
3. Pod scale probe must cover at least `clustered3d`, `road3d`, and
   `ngsim_dense`.
4. Timings must be same-contract only.
5. External review must accept the boundary.

## Boundary

Goal4155 does not authorize implementation promotion by itself. It does not
authorize release, public speedup wording, broad RT-core wording, whole-app
benchmark claims, paper reproduction, hidden dispatch, automatic partner
selection, automatic partition-cell-factor selection, automatic convergence-mode
selection, app-specific engine logic, native ABI additions, AMD claims, or
true-zero-copy claims.
