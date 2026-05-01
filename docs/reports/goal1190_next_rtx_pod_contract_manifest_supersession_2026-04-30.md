# Goal1190 Next RTX Pod Contract Manifest Supersession

Date: 2026-04-30

This supersession changes planning status only. It does not authorize public RTX speedup wording, release, tagging, or cloud execution by itself.

## Summary

- valid: `True`
- supersedes: Goal1189 blocked baseline-harness classification for graph and polygon rows
- rows: `6`
- local dry-run required rows: `6`
- pod ready now: `False`

## Local Next Step

Run small local command-shape dry-runs for all baseline commands, then build a pod executor only after the JSON schemas and comparable phase fields are verified.

## Pod Recommendation

Do not use a paid pod yet. The manifest is now command-complete, but local dry-runs and schema checks must pass before cloud execution.

## Rows

| App | Status | Contract | Phase to compare | Scale | OptiX command | Baseline command | Boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `database_analytics` | `local_dry_run_required` | prepared compact-summary DB sales-risk traversal/filter/grouping summary only | warm/query compact-summary timing | `{"copies": 30000, "iterations": 10}` | `python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario sales_risk --copies 30000 --iterations 10 --output-mode compact_summary --strict --output-json docs/reports/goal1190_next_rtx_pod_contract_batch/database_compact_summary_optix.json` | `python3 scripts/goal756_db_prepared_session_perf.py --backend embree --scenario sales_risk --copies 30000 --iterations 10 --output-mode compact_summary --strict --output-json docs/reports/goal1190_next_rtx_pod_contract_batch/database_compact_summary_embree.json` | no whole-app speedup claim, SQL, DBMS, row-materializing, or full dashboard claim |
| `graph_analytics` | `local_dry_run_required` | visibility_edges prepared any-hit summary only | Embree graph_phase_totals_sec.query_visibility_pair_rows_sec versus OptiX prepared visibility count/query phase | `{"copies": 30000}` | `python3 scripts/goal889_graph_visibility_optix_gate.py --copies 30000 --output-mode summary --validation-mode analytic_summary --chunk-copies 0 --strict --output-json docs/reports/goal1190_next_rtx_pod_contract_batch/graph_visibility_edges_optix.json` | `python3 examples/rtdl_graph_analytics_app.py --backend embree --scenario visibility_edges --copies 30000 --output-mode summary > docs/reports/goal1190_next_rtx_pod_contract_batch/graph_visibility_edges_embree.json` | no whole-app speedup claim, BFS orchestration, triangle set-intersection, shortest-path, distributed graph, or graph database claim |
| `road_hazard_screening` | `local_dry_run_required` | prepared native road-hazard compact hit-count summary only | prepared segment/polygon hit-count query phase versus Embree summary traversal phase | `{"copies": 20000, "iterations": 5}` | `python3 scripts/goal933_prepared_segment_polygon_optix_profiler.py --scenario road_hazard_prepared_summary --copies 20000 --iterations 5 --mode run --output-json docs/reports/goal1190_next_rtx_pod_contract_batch/road_hazard_native_summary_optix.json` | `python3 examples/rtdl_road_hazard_screening.py --backend embree --copies 20000 --output-mode summary > docs/reports/goal1190_next_rtx_pod_contract_batch/road_hazard_native_summary_embree.json` | no whole-app speedup claim, full GIS, routing, default app, or broad road-hazard claim |
| `polygon_pair_overlap_area_rows` | `local_dry_run_required` | native-assisted LSI/PIP candidate discovery only | run_phases.rt_candidate_discovery_sec; exact area continuation excluded | `{"chunk_copies": 100, "copies": 20000}` | `python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app pair_overlap --mode optix --copies 20000 --output-mode summary --validation-mode analytic_summary --chunk-copies 100 --output-json docs/reports/goal1190_next_rtx_pod_contract_batch/polygon_pair_candidate_discovery_optix.json` | `python3 examples/rtdl_polygon_pair_overlap_area_rows.py --backend embree --copies 20000 --output-mode summary > docs/reports/goal1190_next_rtx_pod_contract_batch/polygon_pair_candidate_discovery_embree.json` | no whole-app speedup claim, exact area, overlay matrix, or monolithic polygon-area claim |
| `polygon_set_jaccard` | `local_dry_run_required` | safe-chunk native-assisted LSI/PIP candidate discovery only | run_phases.rt_candidate_discovery_sec; exact set-area/Jaccard continuation excluded | `{"chunk_copies": 512, "copies": 8192}` | `python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode optix --copies 8192 --output-mode summary --validation-mode analytic_summary --chunk-copies 512 --output-json docs/reports/goal1190_next_rtx_pod_contract_batch/polygon_jaccard_safe_chunk_optix.json` | `python3 examples/rtdl_polygon_set_jaccard.py --backend embree --copies 8192 --output-mode summary > docs/reports/goal1190_next_rtx_pod_contract_batch/polygon_jaccard_safe_chunk_embree.json` | no whole-app speedup claim, exact Jaccard, exact set-area, or whole polygon-set app claim |
| `hausdorff_distance` | `local_dry_run_required` | prepared Hausdorff <= radius decision only | prepared threshold query phase versus Embree directed_summary traversal/reduction | `{"copies": 200000, "iterations": 10, "radius": 0.4, "watch_item": "may still be below timing floor; local dry-run must adjust if needed"}` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario hausdorff_threshold --mode optix --copies 200000 --iterations 10 --radius 0.4 --output-json docs/reports/goal1190_next_rtx_pod_contract_batch/hausdorff_threshold_prepared_optix.json` | `python3 examples/rtdl_hausdorff_distance_app.py --backend embree --copies 200000 --embree-result-mode directed_summary --hausdorff-threshold 0.4 > docs/reports/goal1190_next_rtx_pod_contract_batch/hausdorff_threshold_prepared_embree.json` | no whole-app speedup claim, exact Hausdorff distance, nearest-neighbor ranking, or KNN-row claim |

## Boundary

This supersession changes planning status only. It does not authorize public RTX speedup wording, release, tagging, or cloud execution by itself.

