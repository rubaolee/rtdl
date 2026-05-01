# Goal1189 Next RTX Pod Contract Manifest

Date: 2026-04-30

This manifest defines contracts and commands only. It does not authorize public RTX speedup wording, release, tagging, or cloud execution by itself.

## Summary

- valid: `True`
- rows: `6`
- pod-ready after local dry run: `3`
- needs baseline harness: `3`

## Recommendation

Do not run the next public-wording pod batch yet. First add candidate-only baseline harnesses for graph visibility, polygon pair overlap, and polygon Jaccard; then run local dry-runs for all six rows and package one pod batch.

## Rows

| App | Status | Contract | Scale | OptiX command | Baseline command / missing work | Boundary |
| --- | --- | --- | --- | --- | --- | --- |
| `database_analytics` | `pod_ready_after_local_dry_run` | prepared compact-summary DB sales-risk traversal/filter/grouping summary only | `{"copies": 30000, "iterations": 10, "reason": "Goal1184 copies=20000 was 0.09356s, just below 0.1s; 30000 should clear floor with margin"}` | `python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario sales_risk --copies 30000 --iterations 10 --output-mode compact_summary --strict --output-json docs/reports/goal1189_next_rtx_pod_contract_batch/database_compact_summary_optix.json` | `python3 scripts/goal756_db_prepared_session_perf.py --backend embree --scenario sales_risk --copies 30000 --iterations 10 --output-mode compact_summary --strict --output-json docs/reports/goal1189_next_rtx_pod_contract_batch/database_compact_summary_embree.json` | no SQL, DBMS, row-materializing, full dashboard, or whole-app speedup claim |
| `graph_analytics` | `needs_baseline_harness_before_pod` | visibility_edges prepared any-hit summary plus native graph-ray candidate path only | `{"copies": 30000, "reason": "raise work above previous copies=20000 while preserving summary semantics"}` | `python3 scripts/goal889_graph_visibility_optix_gate.py --copies 30000 --output-mode summary --validation-mode analytic_summary --chunk-copies 0 --strict --output-json docs/reports/goal1189_next_rtx_pod_contract_batch/graph_visibility_edges_optix.json` | `add a same-contract CPU/Embree summary baseline artifact for visibility_edges that emits comparable blocked/visible counts and timing without full row materialization` | no whole-app speedup claim, whole graph-system, BFS orchestration, triangle set-intersection, or distributed graph claim |
| `road_hazard_screening` | `pod_ready_after_local_dry_run` | prepared native road-hazard compact hit-count summary only | `{"copies": 20000, "iterations": 5, "reason": "Goal1184 already cleared floor with median 0.108167s"}` | `python3 scripts/goal933_prepared_segment_polygon_optix_profiler.py --scenario road_hazard_prepared_summary --copies 20000 --iterations 5 --mode run --output-json docs/reports/goal1189_next_rtx_pod_contract_batch/road_hazard_native_summary_optix.json` | `python3 examples/rtdl_road_hazard_screening.py --backend embree --copies 20000 --output-mode summary` | no whole-app speedup claim, full GIS, routing, default app, or broad road-hazard speedup claim |
| `polygon_pair_overlap_area_rows` | `needs_candidate_baseline_harness_before_pod` | native-assisted LSI/PIP candidate discovery only | `{"chunk_copies": 100, "copies": 20000, "reason": "Goal1184 candidate-discovery phase was 2.950786s and reviewable if baseline contract is split cleanly"}` | `python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app pair_overlap --mode optix --copies 20000 --output-mode summary --validation-mode analytic_summary --chunk-copies 100 --output-json docs/reports/goal1189_next_rtx_pod_contract_batch/polygon_pair_candidate_discovery_optix.json` | `add a same-contract candidate-discovery-only CPU/Embree baseline; full exact area continuation is not an acceptable baseline for the candidate-only claim` | no whole-app speedup claim, exact area, overlay matrix, or monolithic polygon-area speedup claim |
| `polygon_set_jaccard` | `needs_candidate_baseline_harness_before_pod` | safe-chunk native-assisted LSI/PIP candidate discovery only | `{"chunk_copies": 512, "copies": 8192, "reason": "Goal1184 safe chunk cleared with candidate-discovery phase 1.830098s; chunk 512 is known safe"}` | `python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode optix --copies 8192 --output-mode summary --validation-mode analytic_summary --chunk-copies 512 --output-json docs/reports/goal1189_next_rtx_pod_contract_batch/polygon_jaccard_safe_chunk_optix.json` | `add a same-contract candidate-discovery-only CPU/Embree baseline; exact set-area/Jaccard continuation remains outside the claim` | no exact Jaccard, exact set-area, or whole app speedup claim |
| `hausdorff_distance` | `pod_ready_after_local_dry_run` | prepared Hausdorff <= radius decision only | `{"copies": 200000, "iterations": 10, "radius": 0.4, "reason": "Goal1184 copies=20000 was 0.001296s, far below floor; 10x scale targets reviewable timing while preserving threshold semantics"}` | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario hausdorff_threshold --mode optix --copies 200000 --iterations 10 --radius 0.4 --output-json docs/reports/goal1189_next_rtx_pod_contract_batch/hausdorff_threshold_prepared_optix.json` | `python3 examples/rtdl_hausdorff_distance_app.py --backend embree --copies 200000 --embree-result-mode directed_summary --hausdorff-threshold 0.4` | no exact Hausdorff distance, nearest-neighbor ranking, KNN rows, or whole-app speedup claim |

## Boundary

This manifest defines contracts and commands only. It does not authorize public RTX speedup wording, release, tagging, or cloud execution by itself.

