# Goal1932 - All-App v2 Pod Batch Runner

Status: runner-ready-pod-needed

Date: 2026-05-13

Goal1932 packages the remaining v2.0 all-app comparison work into a single RTX-pod runner with visible progress. It does not authorize release readiness or whole-app speedup claims.

## What It Runs

The runner writes to `docs/reports/goal1932_all_app_v2_pod_batch` by default
and prints `[goal1932]` progress banners before and after every long step. Each
step is wrapped in GNU `timeout --preserve-status` through
`STEP_TIMEOUT_SECONDS`, defaulting to `2700` seconds. Set it to `0` only for a
manual debugging run where another watchdog is already active.

Implemented or harness-ready v2 rows:

- Goal1925 fixed-radius six-app family: `facility_knn_assignment`, `hausdorff_distance`, `ann_candidate_search`, `outlier_detection`, `dbscan_clustering`, `barnes_hut_force_app`.
- Goal1928 robot collision pose flags.
- Goal1856 segment/polygon any-hit row reruns at `512` and `2048`.

Evidence-only control rows:

- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`
- `database_analytics`
- `graph_analytics`

Those control rows are included so the final report has evidence instead of empty cells, but they are not v2 partner speedup rows.

## Pod Command

```bash
OUT_DIR=docs/reports/goal1932_all_app_v2_pod_batch \
PARTNERS=cupy,torch \
PYTHONPATH=src:. \
bash scripts/goal1932_all_app_v2_pod_batch_runner.sh
```

Optional scale knobs:

```bash
FIXED_QUERY_COUNT=524288 FIXED_SEARCH_COUNT=524288 FIXED_REPEAT=1 \
SEGMENT_ITERATIONS=7 ROBOT_REPEAT=7 \
POLYGON_COPIES=8192 DB_COPIES=100000 GRAPH_COPIES=100000 \
STEP_TIMEOUT_SECONDS=2700
```

Use the fixed-radius override when the goal is seconds-scale evidence rather
than quick smoke coverage. The default runner remains a compact all-app packet;
the large knobs are the preferred pod form for performance interpretation.

## Expected Outputs

- `goal1925_fixed_radius_family_v2_partner_perf_pod.json`
- `goal1928_robot_collision_v2_partner_perf_pod.json`
- `goal1856_segment_polygon_v2_partner_perf_pod_current_512.json`
- `goal1856_segment_polygon_v2_partner_perf_pod_current_2048.json`
- `control_polygon_pair_overlap_area_rows_optix.json`
- `control_polygon_set_jaccard_optix.json`
- `control_database_analytics_optix.json`
- `control_graph_analytics_embree.json`
- `goal1930_all_app_v2_matrix.json`
- `goal1931_current_all_app_v18_v2_perf_analysis.json`
- `progress.log`

## Claim Boundary

This runner is a measurement packet, not a release action. Final v2.0 still needs the resulting artifacts to be validated, folded into the all-app analysis, reviewed by external AI consensus, and approved by explicit release action.
