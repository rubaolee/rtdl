# Goal2654 All Benchmark App Performance Comparison Refresh

Status: internal current-evidence report. This is not public speedup wording,
not a release/tag operation, and not a whole-application performance claim.

## Purpose

This report refreshes the all-benchmark Embree-vs-OptiX comparison after the
RayDB benchmark was rewritten and closed as a paper-shaped RT-core prepared
query benchmark in Goal2653. The older Goal2637 all-benchmark report is kept as
historical evidence; it still contains the old RayDB partner-resident rows and
should not be used as the current RayDB RT-core claim.

The table below is a current-evidence portfolio view. Most rows come from the
Goal2634/Goal2637 matrix; RayDB rows come from Goal2652/Goal2653. Therefore this
is not a single synchronized pod sweep. It is the current accepted per-app
comparison table.

## Source Artifacts

Primary portfolio and historical all-benchmark evidence:

- `docs/application_catalog.md`
- `docs/reports/goal2637_all_benchmark_perf_diffs_2026-05-27.md`
- `docs/reports/goal2643_all_benchmark_apps_detailed_report_2026-05-27.md`

RayDB current evidence:

- `docs/reports/goal2652_raydb_10s_prepared_query_configs_2026-05-27.md`
- `docs/reports/goal2653_raydb_benchmark_closeout_2026-05-27.md`
- `docs/reports/goal2653_raydb_closeout_3ai_consensus_2026-05-27.md`

Important follow-up rows:

- `docs/reports/goal2636_strengthened_rows_pod_fixed/summary.md`
- `docs/reports/goal2636_strengthened_rows_stress_pod_fixed/summary.md`
- `docs/reports/goal2642_barnes_hut_embree_vs_optix_app_perf_2026-05-27.md`

## Executive Summary

Current promoted benchmark portfolio:

- 10 benchmark apps.
- 11 primary comparison rows because RayDB has separate grouped `count` and
  grouped `sum` contracts.
- 11 of 11 primary rows show OptiX faster than Embree at the exact documented
  subpath boundary.
- Current primary-row summary: min 3.29x, median 27.67x, geomean 24.13x, max
  172.14x.
- Strengthened weak-row summary from Goal2636 remains: 13 of 13 OptiX wins,
  min 1.81x, median 23.38x, geomean 16.91x, max 170.63x.
- Stress-row summary from Goal2636 remains: 16 of 16 OptiX wins, min 1.26x,
  median 36.36x, geomean 21.69x, max 465.45x.

Correct narrow conclusion:

```text
For the current accepted internal evidence, every promoted benchmark app has an
Embree-vs-OptiX comparison at its documented exact-subpath boundary, and OptiX
wins every current primary row.
```

Incorrect conclusion:

```text
RTDL universally beats Embree, CUDA, author systems, SQL engines, or DBMSs for
whole applications.
```

That broader claim is not supported.

## Current Primary Comparison Table

| App | Current comparison contract | Embree sec | OptiX sec | OptiX speedup | Evidence | Boundary |
| --- | --- | ---: | ---: | ---: | --- | --- |
| Hausdorff / X-HD-style | Hausdorff threshold decision | 0.102451 | 0.0311073 | 3.29x | Goal2637 / Goal2634 | Threshold decision only; not every exact witness path. |
| Spatial RayJoin-style | Scoped all-backend query summary | 0.0203149 | 0.000529638 | 38.36x | Goal2637 / Goal2634 | Scoped spatial relation summary; not full RayJoin reproduction. |
| RT-DBSCAN-style | Cluster signature | 20.6102 | 1.62144 | 12.71x | Goal2637 / Goal2634 | Generic fixed-radius/component contract; no DBSCAN-native ABI. |
| Robot collision | Prepared collision flags | 0.00853798 | 0.00161413 | 5.29x | Goal2637 / Goal2634 | Static-scene screening only. |
| RayDB-style grouped aggregate | Generated 2M grouped count, steady-state prepared query | 0.0047154 | 0.0001704 | 27.67x | Goal2652 / Goal2653 | Prepared-query phase only; no whole-app, DBMS, authors-code, or public speedup claim. |
| RayDB-style grouped aggregate | Generated 2M grouped sum, steady-state prepared query | 0.0985329 | 0.0009476 | 104.00x | Goal2652 / Goal2653 | Prepared-query phase only; setup, descriptor, scene, payload, and ray prep excluded. |
| Barnes-Hut / RT-BarnesHut-style | Node coverage prepared threshold decision | 0.0388851 | 0.00855045 | 4.55x | Goal2637 / Goal2634 | Node-coverage contract; not full force aggregation. |
| LibRTS-style spatial index | AABB index count-only | 20.7070 | 0.691477 | 29.95x | Goal2637 / Goal2634 | Internal count-only AABB slice; not full mutable LibRTS reproduction. |
| RTNN neighbor search | Prepared 3-D ranked summary | 0.263800 | 0.00153247 | 172.14x | Goal2637 / Goal2634 | Ranked-summary contract only. |
| Triangle counting | RT-Graph-style RT-2A1 summary | 0.0390490 | 0.000364401 | 107.16x | Goal2637 / Goal2634 | Synthetic/backend-query contract; paper-scale datasets still need streaming. |
| Bounded contact witness / contact-manifold | Generic AABB broadphase plus bounded collection | 0.485812 | 0.0184764 | 26.29x | Goal2637 / Goal2634 | Generic AABB discovery plus bounded rows; no collision-native ABI. |

## Primary Table Interpretation

The RayDB change is the main update relative to Goal2637:

- old Goal2637 RayDB rows were partner-resident grouped reductions and were not
  RT-core traversal claims;
- current RayDB rows are paper-shaped RT-core prepared-query rows using the
  generic `generic_ray_triangle_primitive_grouped_i64_reduction_3d` primitive;
- the allowed RayDB claim is internal and narrow: generated 2M fixture,
  prepared-query phase only, Embree host versus OptiX host.

The portfolio remains positive after replacing the old RayDB rows. The maximum
primary-row speedup is now RTNN at 172.14x rather than the historical RayDB
partner-resident 280.15x row. This is a cleaner portfolio because the RayDB row
now matches the project's RT-core purpose.

## Strengthened Rows Still In Force

These Goal2636 rows remain the evidence that the previously weak apps were not
only winning on tiny or fragile workloads.

| App | Strengthened workload | Embree sec | OptiX sec | OptiX speedup | Boundary |
| --- | --- | ---: | ---: | ---: | --- |
| Hausdorff / X-HD-style | Threshold, 4096 copies | 0.100719 | 0.0344760 | 2.92x | Threshold-decision subpath. |
| Hausdorff / X-HD-style | Threshold, 16384 copies | 0.380607 | 0.181478 | 2.10x | Larger threshold scale. |
| Hausdorff / X-HD-style | Threshold, 65536 copies | 1.70826 | 0.946120 | 1.81x | Largest strengthened threshold row; margin narrows. |
| Spatial RayJoin-style | PIP authored tiled x512 | 0.0233497 | 0.000315720 | 73.96x | Nonzero tiled point-in-polygon route. |
| Spatial RayJoin-style | LSI authored tiled x512 | 0.0298779 | 0.000303850 | 98.33x | Nonzero tiled line-segment route. |
| Spatial RayJoin-style | Overlay-seed authored tiled x512 | 0.266497 | 0.0558806 | 4.77x | Overlay dependency route, not full materialization. |
| RTNN neighbor search | Uniform 65536 ranked summary | 0.258464 | 0.0106400 | 24.29x | Uniform distribution. |
| RTNN neighbor search | Clustered 65536 ranked summary | 2.16539 | 0.0926344 | 23.38x | Density-risk clustered distribution. |
| RTNN neighbor search | Shell 65536 ranked summary | 0.934770 | 0.00547840 | 170.63x | Shell distribution. |
| Barnes-Hut / RT-BarnesHut-style | Node coverage, 8192 bodies | 0.0393546 | 0.00862844 | 4.56x | Same-contract node coverage. |
| Barnes-Hut / RT-BarnesHut-style | Node coverage, 32768 bodies | 0.113009 | 0.0374079 | 3.02x | Same-contract node coverage. |
| Triangle counting | RT-Graph 2A1, 5000 K4 cliques | 0.0490641 | 0.000372456 | 131.73x | Generic RT-Graph backend-query row. |
| Triangle counting | RT-Graph 2A1, 20000 K4 cliques | 0.102953 | 0.000755426 | 136.28x | Generic RT path remains positive. |

## Stress Rows Still In Force

The stress rows remain useful for trend direction, especially for margin
analysis. The weakest stress row remains Barnes-Hut node coverage at 131072
bodies with 1.26x, so Barnes-Hut remains the portfolio's main candidate for
future runtime work.

| App | Stress workload | Embree sec | OptiX sec | OptiX speedup | Boundary |
| --- | --- | ---: | ---: | ---: | --- |
| Hausdorff / X-HD-style | Threshold, 16384 copies | 0.369679 | 0.164627 | 2.25x | OptiX win. |
| Hausdorff / X-HD-style | Threshold, 65536 copies | 1.69796 | 1.01777 | 1.67x | OptiX win; margin narrows. |
| Hausdorff / X-HD-style | Threshold, 262144 copies | 7.31725 | 4.63951 | 1.58x | Largest threshold stress row. |
| Spatial RayJoin-style | PIP authored tiled x2048 | 0.0349485 | 0.000510602 | 68.45x | PIP route. |
| Spatial RayJoin-style | LSI authored tiled x2048 | 0.0356758 | 0.000455981 | 78.24x | LSI route. |
| Spatial RayJoin-style | Overlay-seed authored tiled x2048 | 3.78287 | 0.897468 | 4.22x | Overlay dependency route. |
| RTNN neighbor search | Uniform 65536 ranked summary | 0.262757 | 0.00226594 | 115.96x | Uniform distribution. |
| RTNN neighbor search | Clustered 65536 ranked summary | 2.11638 | 0.0933383 | 22.67x | Clustered distribution. |
| RTNN neighbor search | Shell 65536 ranked summary | 0.866792 | 0.00552687 | 156.83x | Shell distribution. |
| RTNN neighbor search | Uniform 262144 ranked summary | 3.15816 | 0.00990457 | 318.86x | Large uniform row. |
| RTNN neighbor search | Clustered 262144 ranked summary | 14.9944 | 1.37452 | 10.91x | Hardest RTNN density row. |
| RTNN neighbor search | Shell 262144 ranked summary | 9.35380 | 0.186924 | 50.04x | Large shell row. |
| Barnes-Hut / RT-BarnesHut-style | Node coverage, 32768 bodies | 0.110231 | 0.0374388 | 2.94x | Node coverage. |
| Barnes-Hut / RT-BarnesHut-style | Node coverage, 131072 bodies | 0.385655 | 0.304904 | 1.26x | Weakest stress row. |
| Triangle counting | RT-Graph 2A1, 20000 K4 cliques | 0.101853 | 0.000703277 | 144.83x | Generic RT path. |
| Triangle counting | RT-Graph 2A1, 80000 K4 cliques | 0.403863 | 0.000867688 | 465.45x | Strongest stress row. |

## Latest App-Specific Follow-Ups

RayDB:

- Current closeout row is Goal2652/Goal2653.
- The old Goal2520/Goal2528 partner-resident grouped-reduction path remains
  historical and is not the current RT-core claim.
- Current accepted internal RayDB prepared-query claim: 27.7x for grouped
  `count`, 104.0x for grouped `sum`.

Barnes-Hut:

- The primary table keeps the stable node-coverage row for portfolio
  comparability.
- Goal2642 adds a more relevant aggregate-frontier lowering. At 8192 bodies,
  total app-lowering timing is Embree 74.9243 s versus OptiX 11.1908 s, a
  6.70x total speedup. Membership-only speedup is 74.68x.
- Boundary: native engine sees generic expanded AABB point membership, not
  Barnes-Hut force math.

Robot collision and contact witness:

- Robot collision has both a standard 5.29x row and a 32768-pose stress row at
  8.84x.
- Contact witness has the standard 26.29x row and a large contact broadphase
  stress row at 16.89x.
- Boundary: no native collision/contact ABI.

## App-by-App Current Verdict

| App | Current perf status | Main caveat |
| --- | --- | --- |
| Hausdorff / X-HD-style | Positive primary, strengthened, and stress threshold rows. | Exact witness has OptiX-only rows without same-contract Embree ratio. |
| Spatial RayJoin-style | Strong PIP/LSI rows and positive overlay-seed rows. | Not full RayJoin or full polygon overlay materialization. |
| RT-DBSCAN-style | Positive current promoted app-contract row. | Same output contract, but Embree/OptiX use optimized backend-specific routes. |
| Robot collision | Positive standard and stress prepared-query rows. | Static screening only. |
| RayDB-style grouped aggregate | Reclosed as RT-core prepared-query benchmark with 27.7x/104.0x internal rows. | Prepared-query phase only; no whole-app or DBMS claim. |
| Barnes-Hut / RT-BarnesHut-style | Positive node-coverage rows; aggregate-frontier follow-up improves the RT-core story at scale. | Full force aggregation remains app/partner continuation. |
| LibRTS-style spatial index | Strong count-only AABB-index row. | Not full mutable LibRTS reproduction. |
| RTNN neighbor search | Strong primary, strengthened, and stress distribution rows. | Ranked-summary contract only. |
| Triangle counting | Strong synthetic RT-Graph 2A1 rows. | Paper-scale graph datasets still need segmented/streamed lowering. |
| Bounded contact witness / contact-manifold | Positive standard and stress broadphase rows. | Exact contact interpretation remains Python/app-owned. |

## Bottom Line

The all-benchmark performance comparison is current again after RayDB's
Goal2653 closeout. The refreshed portfolio is cleaner than Goal2637 because
RayDB is now represented by paper-shaped RT-core prepared-query rows instead of
the old partner-resident grouped-reduction rows.

The next version should use this report as the current internal baseline, while
still treating every number as exact-subpath evidence that requires explicit
artifact citation before any public wording.
