# Goal2342: v2.1 All-App Rethink And Comparison

Date: 2026-05-18

Status: local app audit complete; no ordinary app rewrite required; Goal2343
Gemini review accepted with boundary

## Purpose

This goal rechecks every current learner-facing app against the v2.1 runtime
surface. The user request was to rewrite new versions where possible, compare
against v2.0, and include the two serious research benchmarks without rewriting
them again.

The conclusion is intentionally conservative: v2.1 gives two real wins, but it
does not justify cosmetic rewrites of apps whose output contracts are already
served by v2.0 primitives.

## v2.1 Feature Surface Considered

| v2.1 feature | Best fit | Not a fit for |
| --- | --- | --- |
| Prepared segment first-hit / nearest-boundary probe | RayJoin-style vertical-probe support contracts | count, all-witness, ranking, clustering, force-vector, or dynamic-programming apps |
| Hausdorff scale-aware grouped point traversal default | exact projected-point Hausdorff benchmark usability and large-row defaults | unrelated fixed-radius, DB, graph, polygon overlay, or RayJoin apps |
| Existing compact/partner-owned v2.0 summaries | ordinary apps that only need flags, counts, threshold summaries, or compact reductions | full arbitrary user reductions or shader injection |

The rewrite rule is `no_app_specific_native`: app code may choose a generic
primitive, but the native engine must not gain app-shaped names, kernels, or
special cases.

## Ordinary App Decisions

| App script | Current contract | v2.1 rewrite decision | v2.0 comparison evidence retained |
| --- | --- | --- | --- |
| `examples/v2_0/apps/analytics/rtdl_database_analytics_app.py` | columnar scan/group summary | `no_rewrite_same_contract`; v2.1 first-hit is unrelated | Embree 0.998x, OptiX/CuPy 0.231x in Goal2085 |
| `examples/v2_0/apps/geospatial/rtdl_sales_risk_screening.py` | sales-risk scan, grouped count, grouped sum | `no_rewrite_same_contract`; already uses generic compact DB continuation | covered by the same columnar-summary family as database analytics |
| `examples/v2_0/apps/analytics/rtdl_graph_analytics_app.py` | visibility, BFS, triangle-style graph summaries | `no_rewrite_same_contract`; v2.1 RayJoin first-hit does not create a reusable graph primitive | Embree 1.001x, OptiX/CuPy app-wall 0.000x with closed-form boundary in Goal2085 |
| `examples/v2_0/apps/geospatial/rtdl_service_coverage_gaps.py` | fixed-radius coverage counts | `no_rewrite_same_contract`; prepared count path already matches app need | Embree 1.005x, OptiX/CuPy 0.006x in Goal2085 |
| `examples/v2_0/apps/geospatial/rtdl_event_hotspot_screening.py` | fixed-radius density counts | `no_rewrite_same_contract`; prepared count path already matches app need | Embree 0.997x, OptiX/CuPy 0.002x in Goal2085 |
| `examples/v2_0/apps/geospatial/rtdl_facility_knn_assignment.py` | threshold/radius assignment summary | `no_rewrite_same_contract`; exact ranked KNN remains separate future primitive work | Embree 1.001x, OptiX/CuPy 0.006x in Goal2085 |
| `examples/v2_0/apps/geospatial/rtdl_road_hazard_screening.py` | road/hazard counts and priority summaries | `no_rewrite_same_contract`; first-hit would drop count/priority semantics | Embree 1.000x, OptiX/CuPy 0.085x in Goal2085 |
| `examples/v2_0/apps/ml/rtdl_ann_candidate_app.py` | candidate subset and rerank summary | `no_rewrite_same_contract`; first-hit is not ANN ranking | Embree 0.992x, OptiX/CuPy 0.007x in Goal2085 |
| `examples/v2_0/apps/ml/rtdl_outlier_detection_app.py` | radius-density counts | `no_rewrite_same_contract`; prepared fixed-radius path already matches app need | Embree 0.990x, OptiX/CuPy 0.008x in Goal2085 |
| `examples/v2_0/apps/ml/rtdl_dbscan_clustering_app.py` | core-count/core-flag primitive | `no_rewrite_same_contract`; cluster expansion remains app/partner graph work | Embree 0.999x, OptiX/CuPy 0.007x in Goal2085 |
| `examples/v2_0/apps/robotics/rtdl_robot_collision_screening_app.py` | pose collision flags/counts | `no_rewrite_same_contract`; any-hit flags already match the app contract | Embree 0.999x, OptiX/CuPy 0.367x in Goal2085 |
| `examples/v2_0/apps/simulation/rtdl_barnes_hut_force_app.py` | node/body candidate coverage | `no_rewrite_same_contract`; force-vector reduction remains app/partner work | Embree 0.998x, OptiX/CuPy 0.007x in Goal2085 |
| `examples/v2_0/apps/trajectory/rtdl_continuous_frechet_distance_app.py` | Frechet cell broadphase plus dynamic-programming continuation | `no_rewrite_same_contract`; first-hit is not a free-space DP primitive | learner app kept; no Goal2085 all-app table row |

No v2.1 ordinary-app rewrite was landed because each candidate rewrite would
either be a cosmetic rename or would change the app's semantics. This is a
positive result for the app-agnostic boundary, not a failure to use v2.1.

## Feature Rows Carried Forward

These are not all standalone apps, but they feed several learner apps and were
kept in the comparison evidence:

| Feature row | v2.0 evidence | v2.1 action |
| --- | --- | --- |
| `segment_polygon_anyhit_rows` | OptiX streaming witness row in Goal2085: v1.8 1.905528 s, v2.0 0.001421 s, 0.001x | first-hit does not replace full witness output; keep streaming witness contract |
| `polygon_pair_overlap_area_rows` | OptiX/CuPy Goal2085: v1.8 0.705557 s, v2.0 0.166247 s, 0.236x | no v2.1 change; bounded candidate-summary remains the right v2.x shape |
| `polygon_set_jaccard` | OptiX/CuPy Goal2085: v1.8 0.692274 s, v2.0 0.151142 s, 0.218x | no v2.1 change; bounded candidate-summary remains the right v2.x shape |

## Research Benchmark Comparisons

The two research benchmarks are included as evidence, but this goal did not
rewrite them because their v2.1 work was just completed.

### RayJoin-Style Spatial Join

| Scale | RayJoin query | RTDL v2.0 same-contract query+reduction | RTDL v2.1 first-hit native | RTDL v2.1 query+validation | v2.1 vs v2.0 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 4,096 | 0.236209 ms | 26.394 ms | 0.796 ms | 1.363 ms | 19.37x faster |
| 65,536 | 1.490470 ms | 734.597 ms | 2.654 ms | 10.073 ms | 72.93x faster |

Interpretation: v2.1 closes the major current-v2.0 RayJoin PIP gap with a
generic first-hit primitive. It still does not claim to beat the RayJoin paper's
specialized implementation; at 65,536 queries the native RTDL v2.1 timing is
about 1.78x slower than RayJoin's query timing.

Sources: Goal2335 and Goal2337.

### Hausdorff/X-HD-Style Distance

| Evidence row | Optimized grouped CuPy | RTDL/OptiX exact grouped point traversal | Ratio |
| --- | ---: | ---: | ---: |
| Stanford Dragon vs Happy Buddha, public graphics row | 3.417380 s | 0.535331 s | 6.38x faster |
| X-HD graphics Dragon vs Happy Buddha, 437k group4096 | 5.592102 s | 0.591490 s | 9.45x faster |
| Dense Thai Statuette vs Asian Dragon, 1M group8192 | 17.380398 s | 1.248008 s | 13.93x faster |
| Census/ZCTA public geo row | 3.760128 s | 0.301055 s | 12.49x faster |

Goal2340 made the default user path scale-aware so large benchmark rows select
the group sizes that matched the strongest prior evidence. It did not create a
new public current-main performance claim; fresh pod timing for the current
commit remains `needs-pod-evidence`.

Sources: Goal2141 and Goal2340.

## Design Findings

1. v2.1 should not become a version-label repaint of v2.0 apps.
2. First-hit is a real generic primitive, but its safe scope is narrow: nearest
   crossing / nearest boundary support contracts.
3. Most ordinary apps are already better served by v2.0 compact summaries:
   counts, flags, grouped reductions, fixed-radius summaries, and partner-owned
   arrays.
4. The remaining future work is not "rewrite all apps." It is new generic
   primitive work where app contracts require it:
   exact ranked KNN, reusable graph continuation, exact force-vector reduction,
   full Frechet continuation acceleration, and arbitrary user reductions.

## Validation Plan

Local validation for this goal should include:

```text
py -3 -m unittest tests.goal2342_v2_1_all_app_rethink_and_comparison_test
py -3 -m py_compile examples/v2_0/apps/analytics/rtdl_database_analytics_app.py examples/v2_0/apps/analytics/rtdl_graph_analytics_app.py examples/v2_0/apps/geospatial/rtdl_event_hotspot_screening.py examples/v2_0/apps/geospatial/rtdl_facility_knn_assignment.py examples/v2_0/apps/geospatial/rtdl_road_hazard_screening.py examples/v2_0/apps/geospatial/rtdl_sales_risk_screening.py examples/v2_0/apps/geospatial/rtdl_service_coverage_gaps.py examples/v2_0/apps/ml/rtdl_ann_candidate_app.py examples/v2_0/apps/ml/rtdl_dbscan_clustering_app.py examples/v2_0/apps/ml/rtdl_outlier_detection_app.py examples/v2_0/apps/robotics/rtdl_robot_collision_screening_app.py examples/v2_0/apps/simulation/rtdl_barnes_hut_force_app.py examples/v2_0/apps/trajectory/rtdl_continuous_frechet_distance_app.py
```

## Verdict

Ordinary v2.1 app rewrite sweep: `accept`.

Reason: every ordinary app was rechecked, and none should be rewritten with
v2.1 first-hit or Hausdorff tuning without changing its public contract.

Research benchmark v2.1 comparison: `accept-with-boundary`.

Reason: RayJoin has strong reviewed v2.1 improvement over v2.0; Hausdorff has
strong prior evidence and v2.1 default tuning, but fresh current-main pod timing
is still required before replacing earlier numbers.

Full v2.1 release readiness: `needs-external-review`.

## External Review

Goal2343 Gemini review was received with verdict `accept-with-boundary`. The
review accepted the ordinary-app no-rewrite decisions, verified the RayJoin and
Hausdorff numbers against their source reports, and agreed that broad v2.1
release readiness is not authorized by this report alone.
