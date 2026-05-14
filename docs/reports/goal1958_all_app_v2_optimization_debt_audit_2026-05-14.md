# Goal1958 All-App v2 Optimization Debt Audit

Date: 2026-05-14

Status: implementation audit, final release still blocked

## Executive Result

After Goal1957, every one of the 16 tracked apps has a v2 row decision and at
least a bounded v2 path. That does not mean every app is equally optimized, nor
that v2.0 can claim broad whole-app acceleration.

Current classification from the refreshed Goal1931 analysis:

- `positive`: 11 apps
- `positive-subsecond`: 1 app
- `positive-bounded`: 3 apps
- `positive-bounded-exact`: 1 app

The important change is that there are no longer blank “control” rows in the
all-app matrix. The remaining question is quality of the v2 path.

## Current App Table

| App | Current v2 state | Evidence | Main remaining optimization debt |
| --- | --- | --- | --- |
| `database_analytics` | positive bounded RawKernel row | v2/v1.8 `0.205x` | Generalize app-local DB RawKernel into reusable partner grouped scan/reduction primitives. |
| `graph_analytics` | positive bounded metric-table row | v2/v1.8 `0.000003x` | Goal1972 removed the closed-form RawKernel shortcut; still not a broad graph traversal acceleration claim. |
| `service_coverage_gaps` | positive | v2/v1.8 `0.006x` | Mostly healthy; keep prepared scene/output reuse and avoid row materialization. |
| `event_hotspot_screening` | positive | v2/v1.8 `0.002x` | Mostly healthy; same fixed-radius threshold shape. |
| `facility_knn_assignment` | positive threshold proxy | v2/v1.8 `0.000309x` | Not ranked KNN assignment; needs ranked/top-k partner output if the public app wants true assignment semantics. |
| `road_hazard_screening` | positive | v2/v1.8 `0.247x` | Smaller row counts are overhead-sensitive; improve batching/reuse before marketing broad speedups. |
| `segment_polygon_hitcount` | positive | v2/v1.8 `0.345x` | Healthy compact count row; avoid host witness materialization. |
| `segment_polygon_anyhit_rows` | positive row output | v2/v1.8 `0.222x` | Row materialization remains heavier than compact counts; needs device-resident row paging/compaction for larger arbitrary outputs. |
| `polygon_pair_overlap_area_rows` | positive bounded extent row | v2/v1.8 `0.292x` | Goal1969 fixed the candidate-table bottleneck with CuPy extent columns; still bounded to the authored axis-aligned control app. |
| `polygon_set_jaccard` | positive bounded extent row | v2/v1.8 `0.281x` | Goal1969 makes this a clear speedup for the authored extent case; arbitrary polygon/set overlay remains a future broader contract. |
| `hausdorff_distance` | positive bounded exact partner row | v2/CPU exact `0.00824x` | Goal1975 replaces the threshold proxy with exact min-distance then max-distance partner reductions; bounded because it is partner-reference evidence, not an RT-core speedup claim. |
| `ann_candidate_search` | positive threshold proxy | v2/v1.8 `0.000263x` | Not an ANN index; needs candidate-generation/index contract if public app promises ANN behavior. |
| `outlier_detection` | positive | v2/v1.8 `0.000323x` | Healthy count-threshold shape; avoid returning full neighbor rows. |
| `dbscan_clustering` | positive threshold proxy | v2/v1.8 `0.000326x` | Core-point detection is accelerated; full transitive cluster labeling is still app/graph logic. |
| `robot_collision_screening` | positive-subsecond | v2/v1.8 `0.0187x` | Strong ratio but v1.8 is subsecond; keep exact pose-flag parity and scale evidence. |
| `barnes_hut_force_app` | positive threshold proxy | v2/v1.8 `0.000304x` | Node coverage is accelerated; force-vector accumulation is still app logic. |

## What Is Still Unoptimized

The remaining debt is not one bug. It is four patterns:

1. **Metric-table graph continuation is fixed, but still bounded**

   `graph_analytics` no longer uses the closed-form RawKernel shortcut after
   Goal1972. It now uses generic partner metric-table reductions, but it is
   still not a general graph runtime.

2. **Threshold proxies for richer app semantics are shrinking**

   Goal1975 removes `hausdorff_distance` from this bucket by adding exact
   directed Hausdorff partner reductions. `facility_knn_assignment`,
   `ann_candidate_search`, `dbscan_clustering`, and `barnes_hut_force_app`
   still have strong v2 rows because they map to fixed-radius count/threshold
   outputs. The real richer semantics still need additional partner contracts:
   ranked top-k, ANN indexing, cluster expansion, and vector accumulation.

3. **Row materialization**

   `segment_polygon_anyhit_rows` is positive, but row-output paths are inherently
   heavier than compact count/flag paths. We should add device-resident
   compaction/paging and grouped reductions before expecting count-like ratios.

4. **Exact polygon/set reductions**

   Goal1957 proved the bad handoff was the problem and brought polygon from
   catastrophic slowdown into a clear speedup for the authored axis-aligned
   extent rows. To generalize beyond that case, RTDL still needs a reusable
   identity-preserving reduction contract for arbitrary shape/set summaries
   rather than only a bounded extent reducer.

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
   candidate grouping. Do not market the metric-table row as a general graph
   traversal speedup.

4. **Shape/set reduction contract**

   Replace the bounded extent reducer with a more general exact shape/set
   reduction contract. Goal1969 has made the authored extent-control rows faster
   than v1.8; the next target is broadening beyond axis-aligned extent summaries.

5. **Semantic honesty for proxy apps**

   Keep the current fixed-radius threshold rows, but document exactly which app
   semantics they cover. Goal1975 adds the exact Hausdorff row; future rows for
   ranked KNN, full DBSCAN labeling, and Barnes-Hut force-vector accumulation
   should appear only when those continuations are actually implemented.

## Release Meaning

v2.0 is becoming genuinely useful when the user workload can be expressed as:

```text
RTDL prepared candidate/count/hit table + partner compact reduction/threshold
```

It is not yet a universal acceleration layer for arbitrary Python app logic.
The next engineering target is therefore not “rewrite each app by hand”; it is
to make the partner continuation contracts reusable enough that each app rewrite
is a small expression over shared primitives.
