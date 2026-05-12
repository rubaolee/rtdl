# Goal1757 v1.0 to Current Embree / OptiX Reader Performance Table

Date: 2026-05-12

## Verdict

`reader_table_ready_without_public_speedup_claim`

This report rewrites the v1.0 customized-engine versus current
generic-engine performance evidence in reader-facing form. Every cell is
explicitly populated with either a numeric comparison or an evidence basis;
there are no unexplained `n/a`, `pending`, or `artifacts present` cells.

No public speedup claim is authorized. The Embree and OptiX columns use
different measurement bases and should not be compared by absolute seconds.

## How To Read Ratios

Ratio is `v1.0 / current`.

- Above `1.0x`: current generic path is faster for that measured basis.
- Below `1.0x`: current generic path is slower for that measured basis.
- Embree `app-wall`: same app-level CLI wall clock, including process
  startup, input construction, native work, and JSON serialization.
- OptiX/RT `same-contract`: approved same-contract native or subphase timing
  from Goal1750. For graph rows, the combined OptiX `graph_analytics`
  artifact is split into its ordered records: visibility edges, BFS, and
  triangle count.

## Reader Table

| App | Embree v1.0 | Embree current | Embree ratio | Embree basis | OptiX/RT v1.0 | OptiX/RT current | OptiX ratio | OptiX basis |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | --- |
| `database_analytics` | 0.083333 | 0.082423 | 1.011x | same-contract warm query | 0.074627 | 0.074117 | 1.007x | same-contract warm query |
| `service_coverage_gaps` | 0.990 | 1.036 | 0.956x | app-wall | 0.178277 | 0.152120 | 1.172x | optix query |
| `event_hotspot_screening` | 1.804 | 1.777 | 1.015x | app-wall | 0.183431 | 0.182763 | 1.004x | optix query |
| `facility_knn_assignment` | 65.993 | 70.077 | 0.942x | app-wall | 0.000824 | 0.000873 | 0.944x | query median |
| `road_hazard_screening` | 0.832 | 0.847 | 0.982x | app-wall | 0.102807 | 0.103605 | 0.992x | query median |
| `segment_polygon_hitcount` | 0.221 | 0.256 | 0.864x | app-wall | 0.002429 | 0.002430 | 0.999x | query median |
| `segment_polygon_anyhit_rows` | 0.228 | 0.242 | 0.943x | app-wall | 0.004099 | 0.003901 | 1.051x | query median |
| `graph_visibility_edges` | 0.958 | 1.005 | 0.954x | app-wall | 0.959978 | 0.635912 | 1.510x | graph section wall |
| `graph_bfs` | 0.446 | 0.460 | 0.971x | app-wall | 6.232238 | 0.716360 | 8.700x | graph section wall |
| `graph_triangle_count` | 0.693 | 0.696 | 0.995x | app-wall | 0.887620 | 0.971441 | 0.914x | graph section wall |
| `hausdorff_distance` | 105.036 | 107.033 | 0.981x | app-wall | 0.001616 | 0.001702 | 0.949x | query median |
| `ann_candidate_search` | 37.149 | 44.549 | 0.834x | app-wall | 0.000525 | 0.000530 | 0.991x | query median |
| `barnes_hut_force_app` | 3.365 | 3.401 | 0.989x | app-wall | 0.001768 | 0.001770 | 0.999x | query median |
| `polygon_pair_overlap_area_rows` | 5.267 | 20.315 | 0.259x | app-wall | 4.034705 | 2.857352 | 1.412x | candidate discovery |
| `polygon_set_jaccard` | 0.492 | 6.249 | 0.079x | app-wall | 2.371421 | 2.468719 | 0.961x | candidate discovery |
| `outlier_detection` | 1.065 | 1.075 | 0.991x | app-wall | 0.001678 | 0.001673 | 1.004x | warm query |
| `robot_collision_screening` | 717.839 | 715.423 | 1.003x | app-wall | 0.000357 | 0.000353 | 1.011x | prepared warm query |

## Main Reading

Most Embree rows are near parity, but Embree polygon candidate discovery is
the clear performance debt:

- `polygon_pair_overlap_area_rows`: Embree current app-wall is `0.259x`
  of v1.0, while OptiX/RT candidate discovery is `1.412x`.
- `polygon_set_jaccard`: Embree current app-wall is `0.079x` of v1.0,
  while OptiX/RT candidate discovery is `0.961x`.

This does not indicate a polygon correctness failure. The result summaries
match. The slowdown is concentrated in the current generic Embree
candidate-discovery/app-wall path after replacing app-specific polygon
native paths with app-agnostic shape-pair machinery.

OptiX/RT survived the generic-engine migration much better. Its candidate
discovery is near parity for Jaccard and faster for polygon-pair overlap.

## Current Native Engine App-Support Audit

The current source tree separates Python app semantics from native generic
engine primitives for the major v1.8 RTDL families:

- point-in-polygon style work is routed through point/primitive any-hit
  packet symbols;
- Hausdorff-style work is routed through max-distance nearest-candidate
  symbols;
- BFS-style work is routed through frontier/edge traversal and frontier
  discover symbols;
- KNN-style work is routed through k-closest-hit symbols;
- polygon work is routed through generic shape/shape-pair/segment-shape
  symbols;
- DB analytics work is routed through columnar-payload and reduction
  symbols.

Goal1758 follow-up: the older app-named native support outside the
Embree/OptiX pair has now been migrated to generic terms.

| Backend | Goal1757 finding | Goal1758 disposition |
| --- | --- | --- |
| Apple RT | `rtdl_apple_rt_run_lsi` | renamed to `rtdl_apple_rt_run_segment_pair_intersection` |
| HIPRT | `rtdl_hiprt_run_lsi`, `rtdl_hiprt_run_overlay`, `rtdl_hiprt_run_triangle_probe`, `rtdl_hiprt_run_prepared_triangle_probe`, plus HIPRT kernel-name hints | renamed to segment-pair intersection, shape-pair relation flags, and triangle-cycle candidate terminology |
| Oracle | `rtdl_oracle_run_lsi`, `rtdl_oracle_run_overlay`, `rtdl_oracle_run_triangle_probe` | renamed to segment-pair intersection, shape-pair relation flags, and triangle-cycle candidate terminology |
| Vulkan | `rtdl_vulkan_run_lsi`, `rtdl_vulkan_run_overlay`, `rtdl_vulkan_run_triangle_probe` | renamed to segment-pair intersection, shape-pair relation flags, and triangle-cycle candidate terminology |

Post-Goal1758, `src/native/**` no longer shows the old lower-case
`lsi`, `overlay`, or `triangle_probe` native support vocabulary.

## Release Boundary

For a reader:

- v1.0 is the customized-engine baseline.
- current/v1.8-pre is the generic-engine direction.
- Embree/OptiX app families used by the v1.8 RTDL story are structurally
  generic at the native ABI boundary.
- The non-Embree/non-OptiX legacy app-shaped native support symbols
  identified here were migrated by Goal1758.
- The table is engineering evidence, not public performance wording.
