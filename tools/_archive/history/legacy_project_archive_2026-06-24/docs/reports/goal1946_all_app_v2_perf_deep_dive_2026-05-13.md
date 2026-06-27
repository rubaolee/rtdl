# Goal1946 - All-App v1.8 vs v2.0 Performance Deep Dive

Status: codex-analysis-refreshed-after-goal1957-1997-awaiting-external-review

Date: 2026-05-13

## Scope

Goal1946 expands the current Goal1931 all-app rollup into a reader-facing
performance analysis. It answers a narrower question than "is v2.0 released?":

For the 16 active public app rows, what does the current v1.8 versus v2.0
evidence actually say, and why do some rows speed up dramatically while others
remain bounded rather than broad release claims?

This report is based on already collected artifacts:

- `docs/reports/goal1931_current_all_app_v18_v2_perf_analysis_2026-05-13.json`
- `docs/reports/goal1903_fixed_radius_batch_pod.json`
- `docs/reports/goal1937_fixed_radius_repeat3_pod/fixed_radius_524288_repeat3.json`
- `docs/reports/goal1940_robot_segment_scaleup_pod/segment_1048576_segment_anyhit_rows_1048576.json`
- `docs/reports/goal1940_robot_segment_scaleup_pod/robot_8388608x16384_robot_collision_8388608x16384.json`
- `docs/reports/goal1958_all_app_v2_optimization_debt_audit_2026-05-14.md`
- `docs/reports/goal1993_aabb_pair_overlap_summary_2026-05-14.md`
- `docs/reports/goal1994_aabb_pair_payload_columns_2026-05-14.md`
- `docs/reports/goal1996_partner_column_page_contract_2026-05-14.md`
- `docs/reports/goal1997_ray_primitive_witness_pair_paging_2026-05-14.md`

It does not authorize v2.0 release, package-install support, whole-app speedup,
broad RT-core speedup, or arbitrary PyTorch/CuPy acceleration.

## Executive Summary

Current all-app classification after the later Goal1957-1997 cleanup:

| Class | Count | Meaning |
| --- | ---: | --- |
| `positive` | 7 | v2.0 partner path is faster on the same measured row contract. |
| `positive-subsecond` | 1 | v2.0 is much faster, but the v1.8 baseline is still under one second. |
| `positive-bounded` | 3 | The row has measured positive v2 evidence, but the semantics are intentionally narrow. |
| `positive-bounded-exact` | 5 | Exact partner-reference rows are implemented, but they are not broad RT-core speedup claims. |

All 16 rows now have a measured or bounded v2 path. Aggregate speedup summaries
remain descriptive only; they must not be turned into a public "RTDL is N times
faster" claim because the rows are heterogeneous, several are bounded
partner-reference contracts, and v2.0 release authorization still requires final
review consensus.

The core lesson is sharper:

- v2.0 wins dramatically when the app can be expressed as generic RTDL native
  primitive work plus a small partner tensor continuation over partner-owned
  device columns.
- v2.0 still helps on any-hit rows when the output stays compact and the app
  avoids host row materialization.
- v2.0 should not overclaim when the remaining application continuation is a
  bounded database, graph, polygon-area, or set-union contract rather than a
  general-purpose engine feature.

## Full Row Table

`Speedup` is `v1.8 prepared seconds / v2 prepared partner seconds`. A larger
number is better for v2.0. `Ratio` is the inverse, matching Goal1931.

| App row | Class | Partner | Size | v1.8 prepared s | v2 partner s | Ratio | Speedup | Interpretation |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `database_analytics` | `positive` | CuPy | 100,000 | 5.002953 | 1.023833 | 0.204646 | 4.9x | Goal1989 gives a reusable fused columnar partner path at parity with the old app-local RawKernel; bounded by database semantics and final review. |
| `graph_analytics` | `positive-bounded` | CuPy | 1,000 | 18.060916 | 0.000054 | 0.000003 | 334,999x | Goal1991 uses generic metric-table payload/batch reductions; this is not a broad graph traversal claim. |
| `service_coverage_gaps` | `positive` | CuPy | 16,384 | 0.038096 | 0.000228 | 0.005983 | 167.1x | Fixed-radius count-threshold row; partner-owned threshold columns avoid dense pair materialization. |
| `event_hotspot_screening` | `positive` | CuPy | 16,384 | 0.094140 | 0.000188 | 0.001998 | 500.6x | Same fixed-radius pattern, with larger v1.8 native work and tiny partner continuation. |
| `facility_knn_assignment` | `positive-bounded-exact` | CuPy | 524,288 | 1.553787 | 0.000480 | 0.000309 | 3238.1x | Goal1978 adds an exact K=3 ranked nearest-depot partner-reference row; the older fixed-radius threshold row remains useful but is no longer the semantic representative. |
| `road_hazard_screening` | `positive` | CuPy | 2,048 | 0.004491 | 0.001108 | 0.246651 | 4.1x | Positive but small; prepared reuse and compact outputs matter, while tiny rows expose fixed overhead. |
| `segment_polygon_hitcount` | `positive` | Torch | 2,048 | 0.002544 | 0.000878 | 0.345241 | 2.9x | Positive compact count row; not the exact polygon area/Jaccard continuation. |
| `segment_polygon_anyhit_rows` | `positive` | Torch | 1,048,576 | 7.121871 | 1.582755 | 0.222239 | 4.5x | Seconds-scale same-contract any-hit row with strict row-count parity. |
| `polygon_pair_overlap_area_rows` | `positive-bounded` | CuPy | 2,048 | 0.279780 | 0.081689 | 0.291976 | 3.4x | Goals1993-1994 replace the app-local extent RawKernel with generic AABB pair-payload and overlap-summary partner adapters; still bounded to AABB extent semantics. |
| `polygon_set_jaccard` | `positive-bounded` | CuPy | 2,048 | 0.233212 | 0.065533 | 0.281000 | 3.6x | Same generic AABB pair summary path; not arbitrary polygon topology or GIS overlay. |
| `hausdorff_distance` | `positive-bounded-exact` | Torch | 524,288 | 1.326599 | 0.000368 | 0.000277 | 3608.3x | Goal1975 adds exact min-distance then max-distance partner reductions; bounded because this is partner-reference evidence, not a universal Hausdorff implementation claim. |
| `ann_candidate_search` | `positive-bounded-exact` | Torch | 524,288 | 1.328173 | 0.000350 | 0.000263 | 3799.2x | Goal1983 adds exact candidate-subset rerank plus exact full-search quality comparison; bounded because this is not an ANN index/recall-latency optimizer. |
| `outlier_detection` | `positive` | CuPy | 524,288 | 1.357974 | 0.000439 | 0.000323 | 3096.5x | Native fixed-radius counts plus partner scalar reduction. |
| `dbscan_clustering` | `positive-bounded-exact` | Torch | 524,288 | 1.337720 | 0.000436 | 0.000326 | 3069.0x | Goal1985 uses a generic spatial-bucket candidate graph with exact dense validation; still host-index bounded rather than true zero-copy sparse clustering. |
| `robot_collision_screening` | `positive-subsecond` | CuPy | 8,388,608 poses | 0.524696 | 0.009835 | 0.018745 | 53.3x | Exact pose-flag parity and true device-column handoff, but v1.8 is still subsecond. |
| `barnes_hut_force_app` | `positive-bounded-exact` | CuPy | 524,288 | 1.373772 | 0.000418 | 0.000304 | 3289.5x | Goal1979 adds exact pairwise force-vector partner output; bounded because this is not hierarchical Barnes-Hut tree opening or an RT-core speedup claim. |

## Family Analysis

### Fixed-Radius And Exact Partner-Reference Family

Rows:

- `service_coverage_gaps`
- `event_hotspot_screening`
- `outlier_detection`

Exact bounded rows that used to be represented by threshold proxies:

- `facility_knn_assignment`
- `hausdorff_distance`
- `ann_candidate_search`
- `dbscan_clustering`
- `barnes_hut_force_app`

This is the strongest current v2.0 family. The winning shape is:

1. RTDL/OptiX does generic fixed-radius hit/count work.
2. v2.0 writes the compact decision columns into partner-owned device memory.
3. Torch or CuPy performs a small threshold, scalar, or summary continuation.
4. The app avoids dense all-pairs materialization.

At 524,288 queries by 524,288 search points, v1.8 prepared OptiX rows are
seconds-scale, while v2 prepared partner continuations are sub-millisecond for
the measured fixed-radius outputs. The speedup is real for those contracts, but
the row table now distinguishes them from the later exact bounded rows:
Goal1975 for directed Hausdorff, Goal1978 for ranked facility KNN, Goal1979 for
force vectors, Goal1983 for ANN quality comparison, and Goal1985 for the
spatial-bucket DBSCAN path. Those exact rows are valuable v2 evidence, but they
remain bounded partner-reference contracts rather than broad RT-core speedup
claims.

### Segment / Polygon Compact Output Family

Rows:

- `road_hazard_screening`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`

This family is positive but less spectacular. The small 2,048-row hitcount and
road-hazard rows show `2.9x` to `4.1x` speedups, because fixed overheads are
large relative to the app work. The 1,048,576-row any-hit artifact is more
important for release interpretation: it is seconds-scale on v1.8 (`7.12s`) and
faster on v2.0 (`1.58s`), with strict row-count parity.

The lesson is that v2.0 pays off here when the result is a compact flag/count
column. It should not be presented as evidence that exact polygon overlay,
area, or Jaccard computations are accelerated end to end.

### Robot Collision Family

Row:

- `robot_collision_screening`

This is the strongest true device-handoff story in the current packet. The
robot adapter uses caller-supplied partner device ray columns and produces
partner GPU pose flags from native generic any-hit ray flags. The artifact
records direct device-pointer observation and exact pose-flag parity through
8,388,608 poses.

The ratio is strong (`53.3x`), but the v1.8 prepared baseline is still only
`0.525s`. Therefore this row supports "large exact-parity scaling signal" and
"selected true zero-copy/direct-pointer contract" wording, not a seconds-scale
whole-app claim.

### Bounded Families

Rows:

- `database_analytics`
- `graph_analytics`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

These rows are not failures of v2.0; they are places where the current
application continuation is useful but narrow. They are v2 rows, but not broad
release-proof claims for arbitrary database, graph, or polygon programs.

`database_analytics` now has a fused generic columnar partner path, but the
semantics are still a bounded columnar predicate/reduction workload rather than
arbitrary SQL acceleration.

`graph_analytics` now uses generic metric-table payload/reduction adapters, but
it remains too broad as a general graph-runtime claim. Visibility edges can be
RT-shaped, while BFS and triangle counting are graph algorithms.

`polygon_pair_overlap_area_rows` and `polygon_set_jaccard` now use reusable AABB
pair-payload and overlap-summary partner adapters. That is legitimate v2
evidence for the authored AABB extent rows, not evidence for arbitrary polygon
clipping or exact GIS topology.

## What A Learner Should Take Away

v2.0 is not "write arbitrary Python and it becomes GPU-fast." The productive
mental model is:

```text
RTDL generic primitive -> partner-owned device columns -> Torch/CuPy tensor continuation
```

The more an app can fit that shape, the better v2.0 looks. The more an app
requires app-specific exact continuation logic that remains outside Torch/CuPy
or returns to the host, the more it becomes bounded evidence rather than a broad
speedup claim.

## Release Claim Boundary

Allowed technical summary, pending final consensus:

```text
Current v2.0 evidence shows strong speedups for selected OptiX RTDL primitive
contracts that hand compact outputs to Torch or CuPy device tensors. The
strongest broad rows remain fixed-radius threshold workloads; segment any-hit
and robot collision also show positive measured results. Database, graph, AABB
polygon metrics, and the later exact partner-reference rows for Hausdorff,
facility KNN, ANN quality, DBSCAN, and force vectors have useful bounded
contracts, but they must stay narrowly worded until final review consensus.
```

Still blocked:

- v2.0 release authorization;
- broad RT-core speedup claims;
- whole-app acceleration claims;
- arbitrary PyTorch/CuPy acceleration claims;
- package-install claims;
- using bounded rows as broad speedup evidence.

## Next Work

Before a final v2.0 release packet, this report needs external review. The
review should check that the row classifications are fair after Goals1957-1997,
that the fixed-radius speedups are not overgeneralized, that exact bounded rows
stay out of broad marketing claims, and that the source-tree-only package policy
remains a separate consensus question.
