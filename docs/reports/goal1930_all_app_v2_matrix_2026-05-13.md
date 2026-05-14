# Goal1930 - All-App v2 Matrix and v1.8 Comparison Packet

Status: all-app-rows-classified-final-pod-batch-needed

Date: 2026-05-13

Goal1930 converts the v2.0 all-app discussion into a concrete row matrix. It does not claim v2.0 release readiness. The point is to make every app either implemented, harness-ready, rerun-needed, or explicitly marked as an evidence-only control/fallback row before the final RTX pod batch.

## Summary

- row count: `16`
- comparison status counts: `{"needs-current-pod-rerun": 1, "needs-pod-timing": 7, "pod-evidence-collected": 4, "pod-evidence-collected-bounded": 4}`
- release authorized: `False`
- whole-app speedup claim authorized: `False`

## App Rows

| App | Family | v2 state | Comparison status | Claim class |
| --- | --- | --- | --- | --- |
| `database_analytics` | `E-columnar-database-analytics` | `bounded-partner-row` | `pod-evidence-collected-bounded` | `bounded-implemented` |
| `graph_analytics` | `F-graph-split-rows` | `bounded-closed-form-row` | `pod-evidence-collected-bounded` | `bounded-closed-form` |
| `service_coverage_gaps` | `A-fixed-radius-threshold` | `implemented-and-pod-timed` | `pod-evidence-collected` | `implemented` |
| `event_hotspot_screening` | `A-fixed-radius-threshold` | `implemented-and-pod-timed` | `pod-evidence-collected` | `implemented` |
| `facility_knn_assignment` | `A-fixed-radius-threshold` | `harness-ready-pod-needed` | `needs-pod-timing` | `implemented-needs-hardware` |
| `road_hazard_screening` | `C-segment-polygon-count-derived-flags` | `implemented-and-pod-timed` | `pod-evidence-collected` | `implemented` |
| `segment_polygon_hitcount` | `C-segment-polygon-count-derived-flags` | `implemented-and-pod-timed` | `pod-evidence-collected` | `implemented` |
| `segment_polygon_anyhit_rows` | `B-ray-triangle-anyhit-rows` | `implemented-rerun-needed` | `needs-current-pod-rerun` | `implemented-needs-current-hardware` |
| `polygon_pair_overlap_area_rows` | `D-polygon-exact-metric-continuation` | `bounded-partner-row` | `pod-evidence-collected-bounded` | `bounded-implemented` |
| `polygon_set_jaccard` | `D-polygon-exact-metric-continuation` | `bounded-partner-row` | `pod-evidence-collected-bounded` | `bounded-implemented` |
| `hausdorff_distance` | `A-fixed-radius-threshold` | `harness-ready-pod-needed` | `needs-pod-timing` | `implemented-needs-hardware` |
| `ann_candidate_search` | `A-fixed-radius-threshold` | `harness-ready-pod-needed` | `needs-pod-timing` | `implemented-needs-hardware` |
| `outlier_detection` | `A-fixed-radius-threshold` | `harness-ready-pod-needed` | `needs-pod-timing` | `implemented-needs-hardware` |
| `dbscan_clustering` | `A-fixed-radius-threshold` | `harness-ready-pod-needed` | `needs-pod-timing` | `implemented-needs-hardware` |
| `robot_collision_screening` | `B-ray-triangle-anyhit-flags` | `harness-ready-pod-needed` | `needs-pod-timing` | `implemented-needs-hardware` |
| `barnes_hut_force_app` | `A-fixed-radius-threshold` | `harness-ready-pod-needed` | `needs-pod-timing` | `implemented-needs-hardware` |

## Control Rows

The following rows are deliberately evidence-only controls for now, not v2 partner speedup rows:


## Final Pod Batch Commands

Run the harness-ready rows on RTX hardware with progress output:

```bash
PYTHONPATH=src:. python3 scripts/goal1925_fixed_radius_family_v2_partner_perf.py \
  --apps facility_knn_assignment,hausdorff_distance,ann_candidate_search,outlier_detection,dbscan_clustering,barnes_hut_force_app \
  --partners cupy,torch --repeat 5 \
  --output docs/reports/goal1925_fixed_radius_family_v2_partner_perf_pod.json

PYTHONPATH=src:. python3 scripts/goal1928_robot_collision_v2_partner_perf.py \
  --pose-count 4096 --obstacle-count 256 --partners cupy,torch --repeat 5 \
  --output docs/reports/goal1928_robot_collision_v2_partner_perf_pod.json

PYTHONPATH=src:. python3 scripts/goal1856_segment_polygon_v2_partner_perf.py \
  --count 2048 --iterations 5 --partners cupy,torch \
  --output docs/reports/goal1856_segment_polygon_v2_partner_perf_pod_current_2048.json
```

## Analysis Rule

The final report must compare v1.8 and v2.0 row by row, but it must not collapse implemented rows and control rows into one marketing claim. Positive rows explain amortized prepared reuse and partner-owned outputs; negative or neutral rows explain setup overhead, host materialization, or exact app continuation dominating the RT subpath.
