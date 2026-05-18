# Goal2085 v2 Perf Table After Streaming Witness Update

Date: 2026-05-15

## Purpose

Goal2079 filled the all-app Embree and OptiX/RT v1.8-vs-v2.0 tables, but the OptiX/RT `segment_polygon_anyhit_rows` row still used the old full Python witness-row contract and was slower. Goal2081/Goal2083 added and measured a streaming exact witness-column contract. Goal2084 Gemini review accepted the pod evidence with boundary.

This report keeps the Embree table unchanged and refreshes the OptiX/RT table by replacing only `segment_polygon_anyhit_rows` with the reviewed streaming witness-column evidence.

## Key Delta

`segment_polygon_anyhit_rows` changes from the old full-row contract (`1.562x` in Goal2079) to the streaming exact witness-column contract (`0.001x` at count 16384 in Goal2083). The old full-row path remains documented; the new table row is a different, better v2 output contract.

## Embree Table

| app | scale | v1.8 sec | v2.0 sec | v2/v1.8 | note |
| --- | --- | ---: | ---: | ---: | --- |
| `database_analytics` | copies=4000 | 0.624328 | 0.623253 | 0.998x | filled by re-implementing/running the v1.8 Python+RTDL Embree path in the current tree; no distinct v2 CPU partner DB adapter claim |
| `graph_analytics` | scenario=all copies=2000 | 0.448031 | 0.448262 | 1.001x | filled by measuring the complete graph app instead of leaving split graph rows or blank cells; reusable v2 graph partner primitive remains future work |
| `service_coverage_gaps` | copies=2000 | 0.383810 | 0.385865 | 1.005x | threshold/proxy semantics only; not exact ranked KNN, full DBSCAN, or force-vector accumulation |
| `event_hotspot_screening` | copies=2000 | 0.462037 | 0.460492 | 0.997x | threshold/proxy semantics only; not exact ranked KNN, full DBSCAN, or force-vector accumulation |
| `facility_knn_assignment` | copies=2000 | 1.038575 | 1.039533 | 1.001x | threshold/proxy semantics only; not exact ranked KNN, full DBSCAN, or force-vector accumulation |
| `road_hazard_screening` | copies=2000 | 0.358194 | 0.358267 | 1.000x | same Embree evidence cell; v2 GPU partner speedup is an OptiX/CuPy result, not an Embree CPU claim |
| `segment_polygon_hitcount` | copies=1024 | 0.393747 | 0.394920 | 1.003x | same Embree evidence cell; compact count is the desired v2 shape but this local row is CPU Embree |
| `segment_polygon_anyhit_rows` | copies=1024 capacity=16384 | 0.417826 | 0.419203 | 1.003x | full row materialization remains the weak output shape; no compact-count substitution in this row |
| `polygon_pair_overlap_area_rows` | copies=5000 | 2.422751 | 1.029965 | 0.425x | filled as evidence for the bounded/streaming candidate-summary direction; not arbitrary polygon overlay |
| `polygon_set_jaccard` | copies=1000 | 1.844188 | 0.383534 | 0.208x | filled as evidence for the bounded/streaming candidate-summary direction; not arbitrary polygon overlay |
| `hausdorff_distance` | copies=2000 | 1.271810 | 1.306289 | 1.027x | exact directed summary, not a GPU partner threshold proxy in this Embree table |
| `ann_candidate_search` | copies=2000 | 0.752987 | 0.746997 | 0.992x | candidate coverage/rerank summary only; not a general ANN index claim |
| `outlier_detection` | copies=2000 | 0.377554 | 0.373912 | 0.990x | threshold/proxy semantics only; not exact ranked KNN, full DBSCAN, or force-vector accumulation |
| `dbscan_clustering` | copies=2000 | 0.378293 | 0.377832 | 0.999x | core-count only; full cluster expansion remains app/partner graph work |
| `robot_collision_screening` | poses=2000 obstacles=512 | 35.723054 | 35.676529 | 0.999x | pose flags/count only; no whole-planner acceleration claim |
| `barnes_hut_force_app` | body-count=50000 | 1.022868 | 1.020987 | 0.998x | node coverage only; force-vector reduction remains outside this row |


## OptiX/RT Table

| app | scale | v1.8 sec | v2.0 sec | v2/v1.8 | note |
| --- | --- | ---: | ---: | ---: | --- |
| `database_analytics` | copies=100000 partner=cupy candidate_backend=cupy_extent current RTX A5000 | 8.914665 | 2.062000 | 0.231x | current-commit pod refresh; user-approved Python+CuPy+RTDL vs Python+RTDL app-wall comparison, not absolutely fair |
| `graph_analytics` | copies=512 | 5.206507 | 0.000121 | 0.000x | app-wall Python+RTDL vs Python+CuPy+RTDL; not absolutely fair, but user-approved v2 app comparison |
| `service_coverage_gaps` | size=16384 partner=cupy | 0.038096 | 0.000228 | 0.006x | prepared fixed-radius count/threshold output; compact partner-owned columns |
| `event_hotspot_screening` | size=16384 partner=cupy | 0.094140 | 0.000188 | 0.002x | prepared fixed-radius count/threshold output; compact partner-owned columns |
| `facility_knn_assignment` | query=16384 search=8192 partner=cupy current RTX A5000 | 0.047628 | 0.000307 | 0.006x | current-commit pod refresh; prepared fixed-radius count/threshold output; richer semantics remain bounded where documented |
| `road_hazard_screening` | roads=12288 hazards=18432 partner=cupy | 0.029205 | 0.002496 | 0.085x | prepared reusable witness output plus partner priority flags |
| `segment_polygon_hitcount` | rows=131072 capacity=67108864 partner=cupy | 0.452884 | 0.002772 | 0.006x | compact partner-owned count columns; strongest segment/polygon v2 shape |
| `segment_polygon_anyhit_rows` | count=16384 partner=cupy streaming_exact_witness_page current RTX 3090 | 1.905528 | 0.001421 | 0.001x | Goal2083 reviewed streaming exact witness-column contract; avoids full Python row-table materialization. Old full-row v2 contract remains separately documented as slower/less favorable. |
| `polygon_pair_overlap_area_rows` | copies=4096 partner=cupy candidate_backend=cupy_extent current RTX A5000 | 0.705557 | 0.166247 | 0.236x | current-commit pod refresh using Goal2075 generic tiled AABB candidate-summary source; legacy OptiX candidate path at copies=3072 measured ratio=1.990x and remains slower |
| `polygon_set_jaccard` | copies=4096 partner=cupy candidate_backend=cupy_extent current RTX A5000 | 0.692274 | 0.151142 | 0.218x | current-commit pod refresh using Goal2075 generic tiled AABB candidate-summary source; legacy OptiX candidate path at copies=3072 measured ratio=1.263x and remains slower |
| `hausdorff_distance` | query=16384 search=8192 partner=cupy current RTX A5000 | 0.042356 | 0.000306 | 0.007x | current-commit pod refresh; prepared fixed-radius count/threshold output; richer semantics remain bounded where documented |
| `ann_candidate_search` | query=16384 search=8192 partner=cupy current RTX A5000 | 0.043023 | 0.000303 | 0.007x | current-commit pod refresh; prepared fixed-radius count/threshold output; richer semantics remain bounded where documented |
| `outlier_detection` | query=16384 search=8192 partner=cupy current RTX A5000 | 0.044036 | 0.000331 | 0.008x | current-commit pod refresh; prepared fixed-radius count/threshold output; richer semantics remain bounded where documented |
| `dbscan_clustering` | query=16384 search=8192 partner=cupy current RTX A5000 | 0.047394 | 0.000320 | 0.007x | current-commit pod refresh; prepared fixed-radius count/threshold output; richer semantics remain bounded where documented |
| `robot_collision_screening` | poses=16384 obstacles=1024 partner=cupy current RTX A5000 | 0.001668 | 0.000613 | 0.367x | current-commit pod refresh; prepared generic any-hit flags to partner-owned pose flags |
| `barnes_hut_force_app` | query=16384 search=8192 partner=cupy current RTX A5000 | 0.043253 | 0.000309 | 0.007x | current-commit pod refresh; prepared fixed-radius count/threshold output; richer semantics remain bounded where documented |


## Boundary

This is a performance-table refresh, not a v2.0 release authorization. It distinguishes the new streaming witness-column contract from the old full Python row contract. Final v2.0 release wording still needs the normal final consensus gate.
