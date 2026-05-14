# Goal1958 All-App v2 Optimization Debt Audit

Date: 2026-05-14

Status: implementation audit, final release still blocked

## Executive Result

After Goal1957, every one of the 16 tracked apps has a v2 row decision and at
least a bounded v2 path. That does not mean every app is equally optimized, nor
that v2.0 can claim broad whole-app acceleration.

Current classification from the refreshed Goal1931 analysis:

- `positive`: 12 apps
- `positive-subsecond`: 1 app
- `bounded-near-parity`: 1 app
- `bounded-slower`: 1 app
- `bounded-closed-form`: 1 app

The important change is that there are no longer blank “control” rows in the
all-app matrix. The remaining question is quality of the v2 path.

## Current App Table

| App | Current v2 state | Evidence | Main remaining optimization debt |
| --- | --- | --- | --- |
| `database_analytics` | positive bounded RawKernel row | v2/v1.8 `0.205x` | Generalize app-local DB RawKernel into reusable partner grouped scan/reduction primitives. |
| `graph_analytics` | bounded closed-form row | v2/v1.8 `0.000003x` | Not a generic graph primitive; needs reusable frontier traversal, visibility-edge aggregation, and triangle-count partner contracts. |
| `service_coverage_gaps` | positive | v2/v1.8 `0.006x` | Mostly healthy; keep prepared scene/output reuse and avoid row materialization. |
| `event_hotspot_screening` | positive | v2/v1.8 `0.002x` | Mostly healthy; same fixed-radius threshold shape. |
| `facility_knn_assignment` | positive threshold proxy | v2/v1.8 `0.000309x` | Not ranked KNN assignment; needs ranked/top-k partner output if the public app wants true assignment semantics. |
| `road_hazard_screening` | positive | v2/v1.8 `0.247x` | Smaller row counts are overhead-sensitive; improve batching/reuse before marketing broad speedups. |
| `segment_polygon_hitcount` | positive | v2/v1.8 `0.345x` | Healthy compact count row; avoid host witness materialization. |
| `segment_polygon_anyhit_rows` | positive row output | v2/v1.8 `0.222x` | Row materialization remains heavier than compact counts; needs device-resident row paging/compaction for larger arbitrary outputs. |
| `polygon_pair_overlap_area_rows` | bounded slower | v2/v1.8 `1.421x` | Goal1957 fixed the bad dense-mask handoff, but exact area still needs a better reusable partner reduction or native/partner co-designed summary. |
| `polygon_set_jaccard` | bounded near parity | v2/v1.8 `1.063x` | Near parity, not speedup; needs a more general set-union/intersection partner primitive for arbitrary shapes. |
| `hausdorff_distance` | positive threshold proxy | v2/v1.8 `0.000277x` | Current row is thresholded nearest-candidate, not exact directed Hausdorff max-distance. |
| `ann_candidate_search` | positive threshold proxy | v2/v1.8 `0.000263x` | Not an ANN index; needs candidate-generation/index contract if public app promises ANN behavior. |
| `outlier_detection` | positive | v2/v1.8 `0.000323x` | Healthy count-threshold shape; avoid returning full neighbor rows. |
| `dbscan_clustering` | positive threshold proxy | v2/v1.8 `0.000326x` | Core-point detection is accelerated; full transitive cluster labeling is still app/graph logic. |
| `robot_collision_screening` | positive-subsecond | v2/v1.8 `0.0187x` | Strong ratio but v1.8 is subsecond; keep exact pose-flag parity and scale evidence. |
| `barnes_hut_force_app` | positive threshold proxy | v2/v1.8 `0.000304x` | Node coverage is accelerated; force-vector accumulation is still app logic. |

## What Is Still Unoptimized

The remaining debt is not one bug. It is four patterns:

1. **Closed-form app shortcuts**

   `graph_analytics` is fast because the authored replicated graph admits a
   closed-form summary. That is useful as a v2 app version under the user-approved
   RawKernel boundary, but it is not a general graph runtime.

2. **Threshold proxies for richer app semantics**

   `hausdorff_distance`, `facility_knn_assignment`, `ann_candidate_search`,
   `dbscan_clustering`, and `barnes_hut_force_app` have strong v2 rows because
   they map to fixed-radius count/threshold outputs. The real richer semantics
   still need additional partner contracts: ranked top-k, exact max-distance,
   ANN indexing, cluster expansion, and vector accumulation.

3. **Row materialization**

   `segment_polygon_anyhit_rows` is positive, but row-output paths are inherently
   heavier than compact count/flag paths. We should add device-resident
   compaction/paging and grouped reductions before expecting count-like ratios.

4. **Exact polygon/set reductions**

   Goal1957 proved the bad handoff was the problem and brought polygon from
   catastrophic slowdown to near parity. To turn it into a speedup, RTDL needs a
   reusable identity-preserving reduction contract for shape/set summaries rather
   than a bounded extent reducer.

## Prioritized Work

1. **Partner reduction primitive set**

   Add reusable partner-side primitives for `group_count`, `group_sum`,
   `group_any`, `compact_by_key`, `top_k_by_key`, and `prefix/paging`. This
   directly attacks DB, row materialization, graph, and polygon debts.

2. **Exact identity-preserving outputs**

   Continue the Goal1957 direction: RTDL should pass compact candidate/hit tables
   with stable identity columns and payload slots, never require Python to rebuild
   dense app data before partner code can run.

3. **Graph primitive contract**

   Split graph into reusable partner contracts:
   frontier expansion/counts, visibility-edge aggregation, and triangle-count
   candidate grouping. Do not market the closed-form row as a general graph
   speedup.

4. **Shape/set reduction contract**

   Replace the bounded extent reducer with a more general exact shape/set
   reduction contract. The immediate target is making `polygon_pair_overlap_area_rows`
   faster than v1.8, then lifting `polygon_set_jaccard` from near parity to a
   clear speedup.

5. **Semantic honesty for proxy apps**

   Keep the current fixed-radius threshold rows, but document exactly which app
   semantics they cover. Add future rows for exact Hausdorff, ranked KNN, full
   DBSCAN labeling, and Barnes-Hut force-vector accumulation only when those
   continuations are actually implemented.

## Release Meaning

v2.0 is becoming genuinely useful when the user workload can be expressed as:

```text
RTDL prepared candidate/count/hit table + partner compact reduction/threshold
```

It is not yet a universal acceleration layer for arbitrary Python app logic.
The next engineering target is therefore not “rewrite each app by hand”; it is
to make the partner continuation contracts reusable enough that each app rewrite
is a small expression over shared primitives.

