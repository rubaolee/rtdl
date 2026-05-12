# Goal1746 v1.0 Embree Baseline Adapter Manifest

## Verdict

`v1_0_embree_baseline_adapter_ready`

These rows use real v1.0 Embree example/app command surfaces from the Goal1030 local baseline manifest. They are adapter candidates, not public speedup claims. Timing comparability must be assessed per row after artifacts are generated.

## Rows

| App | Artifact | Command |
| --- | --- | --- |
| `service_coverage_gaps` | `docs/reports/goal1746_v1_0_service_coverage_gaps_embree.json` | `C:\Python311\python.exe examples/rtdl_service_coverage_gaps.py --backend embree --copies 20000 --embree-summary-mode gap_summary` |
| `event_hotspot_screening` | `docs/reports/goal1746_v1_0_event_hotspot_screening_embree.json` | `C:\Python311\python.exe examples/rtdl_event_hotspot_screening.py --backend embree --copies 20000 --embree-summary-mode count_summary` |
| `facility_knn_assignment` | `docs/reports/goal1746_v1_0_facility_knn_assignment_embree.json` | `C:\Python311\python.exe examples/rtdl_facility_knn_assignment.py --backend embree --copies 20000 --output-mode summary` |
| `road_hazard_screening` | `docs/reports/goal1746_v1_0_road_hazard_screening_embree.json` | `C:\Python311\python.exe examples/rtdl_road_hazard_screening.py --backend embree --copies 20000 --output-mode summary` |
| `segment_polygon_hitcount` | `docs/reports/goal1746_v1_0_segment_polygon_hitcount_embree.json` | `C:\Python311\python.exe examples/rtdl_segment_polygon_hitcount.py --backend embree --copies 256` |
| `segment_polygon_anyhit_rows` | `docs/reports/goal1746_v1_0_segment_polygon_anyhit_rows_embree.json` | `C:\Python311\python.exe examples/rtdl_segment_polygon_anyhit_rows.py --backend embree --copies 256 --output-mode rows --output-capacity 4096` |
| `graph_visibility_edges` | `docs/reports/goal1746_v1_0_graph_visibility_edges_embree.json` | `C:\Python311\python.exe examples/rtdl_graph_analytics_app.py --backend embree --scenario visibility_edges --copies 20000 --output-mode summary` |
| `graph_bfs` | `docs/reports/goal1746_v1_0_graph_bfs_embree.json` | `C:\Python311\python.exe examples/rtdl_graph_analytics_app.py --backend embree --scenario bfs --copies 20000 --output-mode summary` |
| `graph_triangle_count` | `docs/reports/goal1746_v1_0_graph_triangle_count_embree.json` | `C:\Python311\python.exe examples/rtdl_graph_analytics_app.py --backend embree --scenario triangle_count --copies 20000 --output-mode summary` |
| `hausdorff_distance` | `docs/reports/goal1746_v1_0_hausdorff_distance_embree.json` | `C:\Python311\python.exe examples/rtdl_hausdorff_distance_app.py --backend embree --copies 20000 --embree-result-mode directed_summary` |
| `ann_candidate_search` | `docs/reports/goal1746_v1_0_ann_candidate_search_embree.json` | `C:\Python311\python.exe examples/rtdl_ann_candidate_app.py --backend embree --copies 20000 --output-mode rerank_summary` |
| `barnes_hut_force_app` | `docs/reports/goal1746_v1_0_barnes_hut_force_app_embree.json` | `C:\Python311\python.exe examples/rtdl_barnes_hut_force_app.py --backend embree --body-count 200000 --output-mode candidate_summary` |
| `polygon_pair_overlap_area_rows` | `docs/reports/goal1746_v1_0_polygon_pair_overlap_area_rows_embree.json` | `C:\Python311\python.exe examples/rtdl_polygon_pair_overlap_area_rows.py --backend embree --copies 20000 --output-mode summary` |
| `polygon_set_jaccard` | `docs/reports/goal1746_v1_0_polygon_set_jaccard_embree.json` | `C:\Python311\python.exe examples/rtdl_polygon_set_jaccard.py --backend embree --copies 20000` |

## Execution

Run from current main and point `--baseline-workdir` at a clean v1.0 checkout with Embree built:

```bash
PYTHONPATH=src:. python3 scripts/goal1746_v1_0_embree_baseline_adapter.py --baseline-workdir /path/to/v1_0_checkout --run
```

The runner captures stdout JSON from each v1.0 app command and writes it into the current checkout's `docs/reports/` directory.

## Boundary

This manifest and runner recover real v1.0 Embree baseline artifacts where v1.0 exposed app-level Embree CLIs. It does not fabricate missing phase-profiler rows and does not authorize public speedup wording.
