# Goal1196 Public Wording Decision Packet

Date: 2026-04-30

Goal1196 is a public-wording decision packet after Goal1195 evidence-readiness. It proposes narrow public wording only for rows with same-contract OptiX advantage, keeps slower OptiX rows blocked from positive speedup wording, and does not edit public docs or authorize release by itself.

## Summary

- source intake: `docs/reports/goal1194_goal1192_public_wording_evidence_batch_final_intake_2026-04-30.json`
- source consensus: `docs/reports/goal1195_two_ai_consensus_2026-04-30.md`
- minimum positive public ratio used by packet: `1.2`
- proposed reviewed apps: `road_hazard_screening, hausdorff_distance`
- proposed blocked apps: `database_analytics, graph_analytics, polygon_pair_overlap_area_rows, polygon_set_jaccard`
- public speedup claims authorized by this packet: `0`

## Decisions

| App | Path | Decision | Embree sec | OptiX sec | Ratio |
| --- | --- | --- | ---: | ---: | ---: |
| `database_analytics` | `prepared_db_compact_summary` | `keep_public_wording_blocked_no_positive_speedup` | `0.119347` | `0.150720` | `0.79x` |
| `graph_analytics` | `visibility_edges_prepared_anyhit` | `keep_public_wording_blocked_no_positive_speedup` | `1.000280` | `2.000505` | `0.50x` |
| `road_hazard_screening` | `prepared_native_road_hazard_summary` | `propose_public_wording_reviewed` | `0.415621` | `0.103539` | `4.01x` |
| `polygon_pair_overlap_area_rows` | `native_assisted_lsi_pip_candidate_discovery` | `keep_public_wording_blocked_no_positive_speedup` | `2.896597` | `3.452362` | `0.84x` |
| `polygon_set_jaccard` | `native_assisted_lsi_pip_candidate_discovery` | `keep_public_wording_blocked_no_positive_speedup` | `0.889453` | `1.620841` | `0.55x` |
| `hausdorff_distance` | `prepared_directed_threshold_decision` | `propose_public_wording_reviewed` | `1.680214` | `0.122389` | `13.73x` |

## Candidate Public Wording

### database_analytics / prepared_db_compact_summary

No positive public RTX speedup wording is authorized for database_analytics from Goal1195 evidence.

Boundary: Prepared compact-summary traversal/filter/grouping is evidence-ready, but the measured OptiX phase is slower than Embree; no SQL-engine, DBMS, full-row, dashboard, or whole-app speedup claim is allowed.

### graph_analytics / visibility_edges_prepared_anyhit

No positive public RTX speedup wording is authorized for graph_analytics from Goal1195 evidence.

Boundary: Bounded visibility/graph-ray RT traversal is evidence-ready, but the measured OptiX phase is slower than Embree; no BFS, triangle-count, graph-system, shortest-path, distributed-analytics, or whole-app speedup claim is allowed.

### road_hazard_screening / prepared_native_road_hazard_summary

RTDL's prepared native road-hazard summary RTX sub-path measured 0.103539 s and 4.01x versus the reviewed same-contract Embree sub-path.

Boundary: Only the prepared native segment/polygon road-hazard summary traversal and threshold-count continuation are covered; default app behavior, full GIS/routing, row materialization, Python setup, and whole-app speedup remain outside this wording.

### polygon_pair_overlap_area_rows / native_assisted_lsi_pip_candidate_discovery

No positive public RTX speedup wording is authorized for polygon_pair_overlap_area_rows from Goal1195 evidence.

Boundary: Native-assisted LSI/PIP candidate discovery is evidence-ready, but the measured OptiX phase is slower than Embree; exact polygon-area refinement, row materialization, broad spatial-join performance, and whole-app speedup are outside any wording.

### polygon_set_jaccard / native_assisted_lsi_pip_candidate_discovery

No positive public RTX speedup wording is authorized for polygon_set_jaccard from Goal1195 evidence.

Boundary: Native-assisted LSI/PIP candidate discovery is evidence-ready after recovery, but the first pod run failed parity, chunk-sensitive or nondeterministic behavior was observed during the recovery trail, and the final measured OptiX phase is slower than Embree; exact set-area/Jaccard refinement, row materialization, and whole-app speedup are outside any wording. Any future positive-wording consideration requires stability testing across chunk configurations.

### hausdorff_distance / prepared_directed_threshold_decision

RTDL's prepared Hausdorff threshold-decision RTX sub-path measured 0.122389 s and 13.73x versus the reviewed same-contract Embree directed-summary sub-path.

Boundary: Only the prepared fixed-radius Hausdorff <= threshold decision sub-path is covered; exact Hausdorff distance, KNN-row output, nearest-neighbor ranking, violating-ID witnesses in scalar mode, Python setup, and whole-app speedup remain outside this wording.

## Reviewer Questions

1. Is it correct to promote only road_hazard_screening and hausdorff_distance to bounded reviewed wording?
2. Is it correct to keep database_analytics, graph_analytics, polygon_pair_overlap_area_rows, and polygon_set_jaccard blocked from positive public speedup wording because OptiX is slower than Embree in the accepted evidence?
3. Is the Jaccard caution boundary strong enough given the first-run parity failure before recovery?
4. Are all boundaries narrow enough to avoid whole-app, default-mode, Python postprocess, DBMS, GIS, graph-system, or exact-distance claims?

