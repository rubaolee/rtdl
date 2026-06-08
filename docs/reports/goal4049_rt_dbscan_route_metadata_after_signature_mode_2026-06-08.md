# Goal4049 RT-DBSCAN Route Metadata After Signature Mode

Date: 2026-06-08

## Purpose

Goal4049 refreshes the live route and benchmark-adequacy metadata after
Goal4046/4047.

The intent is narrow: readers should see that the partition-convergence line
has a useful component-size-signature output contract, without reading that as
a promoted full RT-DBSCAN route.

## What Changed

The RT-DBSCAN live route now says:

- grouped-stream plus Numba column signature remains the promoted RT-DBSCAN
  route;
- `partition_convergence_hybrid` remains explicit and unpromoted;
- Goal4046/4047 show a positive result only for the narrower
  `fixed_radius_graph_component_size_signature_3d` contract;
- full DBSCAN core/border/noise semantics still require the grouped-stream
  route or future fused/prepared partition work.

The benchmark adequacy row now cites Goal4046/4047 and keeps the next runtime
action focused on fused resident component labels or a prepared/native
partition handle.

## Boundary

This is metadata synchronization after a benchmark-app mode. It does not
authorize release action, public speedup wording, broad RT-core wording,
whole-app benchmark wording, hidden dispatch, automatic partner selection,
full DBSCAN promotion for the partition path, app-specific native-engine
logic, a native ABI addition, or true-zero-copy wording.

