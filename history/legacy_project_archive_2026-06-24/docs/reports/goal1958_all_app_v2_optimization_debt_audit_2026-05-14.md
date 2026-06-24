# Goal1958 All-App v2 Optimization Debt Audit

Date: 2026-05-14

Status: implementation audit, final release still blocked

## Executive Result

After Goal1957, every one of the 16 tracked apps has a v2 row decision and at
least a bounded v2 path. That does not mean every app is equally optimized, nor
that v2.0 can claim broad whole-app acceleration.

Current classification from the refreshed Goal1931 analysis:

- `positive`: 7 apps
- `positive-subsecond`: 1 app
- `positive-bounded`: 3 apps
- `positive-bounded-exact`: 5 apps

The important change is that there are no longer blank “control” rows in the
all-app matrix. The remaining question is quality of the v2 path.

## Current App Table

| App | Current v2 state | Evidence | Main remaining optimization debt |
| --- | --- | --- | --- |
| `database_analytics` | positive bounded RawKernel row plus generic columnar path | v2/v1.8 `0.205x`; generic/RawKernel `2.755x` | Goal1987 adds reusable partner columnar predicate/reduction primitives; the next debt is fusing/batching them so the generic path can match the old app-local RawKernel. |
| `graph_analytics` | positive bounded metric-table row | v2/v1.8 `0.000003x` | Goal1972 removed the closed-form RawKernel shortcut; still not a broad graph traversal acceleration claim. |
| `service_coverage_gaps` | positive | v2/v1.8 `0.006x` | Mostly healthy; keep prepared scene/output reuse and avoid row materialization. |
| `event_hotspot_screening` | positive | v2/v1.8 `0.002x` | Mostly healthy; same fixed-radius threshold shape. |
| `facility_knn_assignment` | positive bounded exact top-k row | v2/CPU exact `0.04565x` | Goal1978 replaces the service-coverage proxy with exact K=3 ranked nearest-depot rows; bounded because it is partner-reference evidence, not an RT-core speedup claim. |
| `road_hazard_screening` | positive | v2/v1.8 `0.247x` | Smaller row counts are overhead-sensitive; improve batching/reuse before marketing broad speedups. |
| `segment_polygon_hitcount` | positive | v2/v1.8 `0.345x` | Healthy compact count row; avoid host witness materialization. |
| `segment_polygon_anyhit_rows` | positive row output | v2/v1.8 `0.222x` | Row materialization remains heavier than compact counts; Goals1996-1997 add generic partner column paging and generic witness-pair page adapters. Remaining debt is app adoption plus pod-scale timing. |
| `polygon_pair_overlap_area_rows` | positive bounded AABB extent row | v2/v1.8 `0.292x` | Goal1969 fixed the candidate-table bottleneck; Goals1993-1994 replace the app-local extent RawKernel and handoff with reusable AABB pair-payload and overlap-summary partner adapters. Still bounded to axis-aligned extent semantics. |
| `polygon_set_jaccard` | positive bounded AABB extent row | v2/v1.8 `0.281x` | Goal1969 makes this a clear speedup for the authored extent case; Goals1993-1994 make the continuation generic AABB partner algebra, but arbitrary polygon/set overlay remains a future broader contract. |
| `hausdorff_distance` | positive bounded exact partner row | v2/CPU exact `0.00824x` | Goal1975 replaces the threshold proxy with exact min-distance then max-distance partner reductions; bounded because it is partner-reference evidence, not an RT-core speedup claim. |
| `ann_candidate_search` | positive bounded exact quality row | v2/CPU exact `0.01881x` | Goal1983 replaces the coverage proxy as the semantic representative with exact candidate-subset rerank plus exact full-search quality comparison; bounded because it is not an ANN index or recall/latency optimizer. |
| `outlier_detection` | positive | v2/v1.8 `0.000323x` | Healthy count-threshold shape; avoid returning full neighbor rows. |
| `dbscan_clustering` | positive bounded exact spatial-bucket row | spatial/dense exact `0.256x` | Goal1985 replaces the dense timing row with a generic spatial-bucket candidate graph and separates validation from timing; still host-index bounded, not true zero-copy. |
| `robot_collision_screening` | positive-subsecond | v2/v1.8 `0.0187x` | Strong ratio but v1.8 is subsecond; keep exact pose-flag parity and scale evidence. |
| `barnes_hut_force_app` | positive bounded exact force row | v2/CPU exact `0.01986x` | Goal1979 replaces node coverage as the representative row with exact pairwise force-vector partner output; bounded because this is not hierarchical Barnes-Hut tree opening or RT-core acceleration. |

## What Is Still Unoptimized

The remaining debt is not one bug. It is four patterns:

1. **Metric-table graph continuation is fixed, but still bounded**

   `graph_analytics` no longer uses the closed-form RawKernel shortcut after
   Goal1972. It now uses generic partner metric-table reductions, but it is
   still not a general graph runtime.

2. **Threshold proxies for richer app semantics are shrinking**

   Goal1975 removes `hausdorff_distance` from this bucket by adding exact
   directed Hausdorff partner reductions. Goal1978 removes
   `facility_knn_assignment` from this bucket by adding exact K=3 ranked
   nearest-depot rows. Goal1979 removes `barnes_hut_force_app` from this bucket
   by adding exact force-vector partner output. Goal1981 removes
   `dbscan_clustering` from this bucket by adding exact radius-graph component
   labels. Goal1983 removes `ann_candidate_search` from this bucket by adding
   exact candidate-subset rerank plus exact full-search quality comparison.
   The remaining richer semantics need a true ANN indexing contract and a
   fully partner/device-side sparse DBSCAN index; Goal1985 fixes the dense
   timing path but still uses a host-built bucket index.

3. **Row materialization**

   `segment_polygon_anyhit_rows` is positive, but row-output paths are inherently
   heavier than compact count/flag paths. Goal1965 adds generic compaction,
   Goal1996 adds bounded partner-column paging, and Goal1997 adds generic
   ray/primitive witness-pair paging. We still need app adoption and pod-scale
   timing before expecting count-like ratios.

4. **Exact polygon/set reductions beyond AABB**

   Goal1957 proved the bad handoff was the problem and brought polygon from
   catastrophic slowdown into a clear speedup for the authored axis-aligned
   extent rows. Goals1993-1994 then moved the extent continuation into public
   reusable partner adapters: `aabb_pair_payload_to_partner_columns` and
   `aabb_pair_overlap_summary_2d_partner_columns`. To generalize beyond that
   case, RTDL still needs reusable contracts for arbitrary polygon topology,
   clipping, and set summaries rather than only a bounded AABB extent reducer.

## Prioritized Work

1. **Partner reduction primitive set**

   Add reusable partner-side primitives for `group_count`, `group_sum`,
   `group_any`, `compact_by_key`, `top_k_by_key`, and prefix/paging. This
   directly attacks row materialization, graph, and polygon debts. Goals1996-1997
   cover the first generic paging layer; the next row-output target is using
   those pages in app examples and timing them on pod-scale witness outputs.
   Goal1987 adds the first generic DB columnar reductions; Goal1989 fuses the
   DB summaries into a batched generic path.

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

   Build on the reusable AABB pair-payload and overlap-summary adapters from
   Goals1993-1994 with a more general exact shape/set reduction contract.
   Goal1969 made the authored extent-control rows faster than v1.8; the next
   target is broadening beyond axis-aligned extent summaries without putting
   polygon-specific logic into the native engine.

5. **Semantic honesty for proxy apps**

   Keep the current fixed-radius threshold rows, but document exactly which app
   semantics they cover. Goal1975 adds the exact Hausdorff row and Goal1978
   adds the exact facility KNN top-k row; Goal1979 adds exact Barnes-Hut force
   vectors; Goal1981 adds exact DBSCAN component labels; Goal1983 adds exact
   ANN candidate-subset quality comparison. Future rows for ANN indexing should
   appear only when those continuations are actually implemented.

## Release Meaning

v2.0 is becoming genuinely useful when the user workload can be expressed as:

```text
RTDL prepared candidate/count/hit table + partner compact reduction/threshold
```

It is not yet a universal acceleration layer for arbitrary Python app logic.
The next engineering target is therefore not “rewrite each app by hand”; it is
to make the partner continuation contracts reusable enough that each app rewrite
is a small expression over shared primitives.
