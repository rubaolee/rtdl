# Goal4043 RT-DBSCAN Route Refresh After Partition Candidate Timing

Date: 2026-06-08

## Purpose

Goal4043 refreshes the live benchmark route/adequacy registries after the
Goal4040/4041 partition-convergence work.

The important decision is conservative:

- the promoted RT-DBSCAN-style route remains the unblocked RTDL/OptiX grouped
  stream plus Numba column-signature continuation;
- `partition_convergence_hybrid` remains an explicit candidate route, not a
  default route;
- Goal4041 shows the new device ambiguous-partition continuation is correct and
  useful for residency, but the timing is mixed and therefore not enough to
  promote the partition path.

## What Changed

The live route registry now tells readers that:

- `partition_convergence_hybrid` is not promoted after Goal4041;
- the current partition candidate’s next real engineering target is a fused
  resident component-label continuation or a prepared/native partition handle;
- more Python-side toggling is not expected to deliver a large improvement.

The live benchmark adequacy row for `rt_dbscan` now cites Goal4040/4041 as
evidence while preserving the current recommended path.

## Why This Matters

Without this refresh, the codebase would contain two technically true but
reader-confusing facts:

1. Goal4040/4041 advanced the partition-convergence candidate.
2. The benchmark route registry still pointed only at the earlier grouped-stream
   and Numba evidence.

Goal4043 makes the relationship explicit: partition convergence is a useful
design line, but the current benchmark default does not change until a larger
generic runtime primitive or prepared resident handle wins.

## Boundary

This is a route-registry and benchmark-adequacy consistency update. It does not
authorize release action, public speedup wording, broad RT-core wording,
whole-app benchmark wording, RayJoin/RT-DBSCAN paper-reproduction wording,
hidden dispatch, automatic partner selection, app-specific native-engine logic,
a native ABI addition, or true-zero-copy wording.

