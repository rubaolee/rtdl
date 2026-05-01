# Goal1135 Changed-Path RTX Pod Plan

Date: 2026-04-29

This plan collects changed-path RTX artifacts only. It does not authorize public RTX speedup wording, release, or broad whole-app acceleration claims.

## Policy

Run these entries in one pod session after building/installing the current source. Do not start/stop cloud per app. If one entry OOMs, lower only that entry's scale and continue the remaining entries.

## Entries

| Label | Apps | Reason | Command |
|---|---|---|---|
| `database_analytics_compact_summary` | `database_analytics` | Goal1128 changed compact-summary row-materialization behavior. | `python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario all --copies 20000 --iterations 5 --output-mode compact_summary --strict --output-json docs/reports/goal1135_changed_path_rtx_pod/database_analytics_compact_summary.json` |
| `graph_visibility_edges_gate` | `graph_analytics` | Goal1129 added graph phase splits; retest bounded graph RT sub-paths. | `python3 scripts/goal889_graph_visibility_optix_gate.py --copies 20000 --output-mode summary --validation-mode analytic_summary --chunk-copies 0 --strict --output-json docs/reports/goal1135_changed_path_rtx_pod/graph_visibility_edges_gate.json` |
| `road_hazard_native_summary_count` | `road_hazard_screening` | Goal1130 changed native summary to use prepared threshold count. | `python3 scripts/goal888_road_hazard_native_optix_gate.py --copies 20000 --output-mode summary --strict --output-json docs/reports/goal1135_changed_path_rtx_pod/road_hazard_native_summary_count.json` |
| `polygon_pair_overlap_phase_gate` | `polygon_pair_overlap_area_rows` | Goal1131 exposed candidate-discovery vs exact-continuation phase split. | `python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app pair_overlap --mode optix --copies 20000 --output-mode summary --validation-mode analytic_summary --chunk-copies 20 --output-json docs/reports/goal1135_changed_path_rtx_pod/polygon_pair_overlap_phase_gate.json` |
| `polygon_set_jaccard_phase_gate` | `polygon_set_jaccard` | Goal1131 added compact Jaccard summary and phase split. | `python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode optix --copies 20000 --output-mode summary --validation-mode analytic_summary --chunk-copies 20 --output-json docs/reports/goal1135_changed_path_rtx_pod/polygon_set_jaccard_phase_gate.json` |
| `hausdorff_threshold_phase_gate` | `hausdorff_distance` | Goals1132-1134 clarified app/profiler phase contracts; collect capability-phase evidence only. | `python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario hausdorff_threshold --mode optix --copies 20000 --iterations 5 --radius 0.4 --output-json docs/reports/goal1135_changed_path_rtx_pod/hausdorff_threshold_phase_gate.json` |

Valid: `true`

