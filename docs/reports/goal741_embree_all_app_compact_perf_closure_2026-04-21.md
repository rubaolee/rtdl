# Goal 741 - Embree All-App Compact Performance Closure

Date: 2026-04-21

## Verdict

ACCEPT for the current Embree app-performance cleanup step.

The Embree app harness now runs the public app surface in compact/scaled modes where the apps expose them, avoiding accidental measurement of full Python row expansion, cluster expansion, or O(N^2) validation oracles in paths intended to characterize Embree traversal.

## Changes

- `examples/rtdl_dbscan_clustering_app.py` adds `--output-mode core_flags`.
- `examples/rtdl_outlier_detection_app.py` adds `--output-mode density_summary`.
- `examples/rtdl_hausdorff_distance_app.py` avoids the O(N^2) brute-force oracle when `--embree-result-mode directed_summary` is requested on the authored tiled fixture.
- `scripts/goal714_embree_app_thread_perf.py` now uses compact modes for scalable apps where available.

## macOS Evidence

Command:

```bash
PYTHONPATH=src:. python3 scripts/goal714_embree_app_thread_perf.py --apps all --copies 1024 --threads 1,auto --warmups 0 --min-sample-sec 0.2 --max-repeats 2 --timeout 300 --output docs/reports/goal741_embree_all_app_perf_macos_2026-04-21.json
```

Result:

- `valid: true`
- Host: `Rs-MacBook-Air.local`, macOS arm64, 10 logical CPUs, Python 3.14.0
- Scaled app copy count: `1024`
- Parity: every Embree payload matched the CPU/reference semantic payload under the harness canonical comparison.

| App | CPU/reference sec | Embree 1-thread sec | Embree auto sec | Auto vs 1-thread |
|---|---:|---:|---:|---:|
| database_analytics | 0.158 | 0.159 | 0.152 | 1.04x |
| graph_analytics | 0.114 | 0.134 | 0.132 | 1.02x |
| service_coverage_gaps | 1.603 | 0.135 | 0.136 | 0.99x |
| event_hotspot_screening | 4.581 | 0.162 | 0.160 | 1.01x |
| facility_knn_assignment | 4.739 | 0.418 | 0.192 | 2.18x |
| road_hazard_screening | 0.141 | 0.128 | 0.128 | 1.00x |
| segment_polygon_hitcount | 0.107 | 0.114 | 0.114 | 1.00x |
| segment_polygon_anyhit_rows | 0.156 | 0.149 | 0.149 | 1.00x |
| polygon_pair_overlap_area_rows | 0.168 | 0.216 | 0.216 | 1.00x |
| polygon_set_jaccard | 0.106 | 0.115 | 0.161 | 0.71x |
| hausdorff_distance | 0.170 | 0.613 | 0.218 | 2.82x |
| ann_candidate_search | 2.608 | 0.284 | 0.165 | 1.72x |
| outlier_detection | 0.126 | 0.147 | 0.147 | 1.00x |
| dbscan_clustering | 0.122 | 0.148 | 0.146 | 1.01x |
| robot_collision_screening | 2.351 | 1.259 | 1.258 | 1.00x |
| barnes_hut_force | 0.112 | 0.121 | 0.120 | 1.01x |

## Linux Evidence

Clean temp checkout on `lestat-lx1`:

```bash
rm -rf /tmp/rtdl_goal741_embree
git clone --depth 1 https://github.com/rubaolee/rtdl.git /tmp/rtdl_goal741_embree
cd /tmp/rtdl_goal741_embree
PYTHONPATH=src:. python3 scripts/goal714_embree_app_thread_perf.py --host-label lestat-lx1 --apps all --copies 1024 --threads 1,auto --warmups 0 --min-sample-sec 0.2 --max-repeats 2 --timeout 300 --output docs/reports/goal741_embree_all_app_perf_linux_2026-04-21.json
```

Result:

- `valid: true`
- Host: `lestat-lx1`, Linux x86_64, 8 logical CPUs, Python 3.12.3
- Source commit: `dc80cb7`
- Parity: every Embree payload matched the CPU/reference semantic payload under the harness canonical comparison.

| App | CPU/reference sec | Embree 1-thread sec | Embree auto sec | Auto vs 1-thread |
|---|---:|---:|---:|---:|
| database_analytics | 0.260 | 0.285 | 0.284 | 1.00x |
| graph_analytics | 0.200 | 0.231 | 0.232 | 1.00x |
| service_coverage_gaps | 3.141 | 0.274 | 0.273 | 1.00x |
| event_hotspot_screening | 9.089 | 0.350 | 0.352 | 0.99x |
| facility_knn_assignment | 7.978 | 0.874 | 0.400 | 2.18x |
| road_hazard_screening | 0.249 | 0.222 | 0.222 | 1.00x |
| segment_polygon_hitcount | 0.187 | 0.200 | 0.197 | 1.02x |
| segment_polygon_anyhit_rows | 0.319 | 0.294 | 0.296 | 0.99x |
| polygon_pair_overlap_area_rows | 0.318 | 0.414 | 0.413 | 1.00x |
| polygon_set_jaccard | 0.186 | 0.196 | 0.196 | 1.00x |
| hausdorff_distance | 0.190 | 1.146 | 0.456 | 2.51x |
| ann_candidate_search | 4.574 | 0.568 | 0.312 | 1.82x |
| outlier_detection | 0.256 | 0.310 | 0.308 | 1.01x |
| dbscan_clustering | 0.258 | 0.313 | 0.309 | 1.01x |
| robot_collision_screening | 5.037 | 2.656 | 2.690 | 0.99x |
| barnes_hut_force | 0.198 | 0.206 | 0.209 | 0.98x |

## Interpretation

The Embree work is now technically healthier because the app-level harness no longer confuses RTDL/Embree traversal work with Python expansion or validation work.

Clear Embree wins on this Mac:

- service coverage gaps
- event hotspot screening
- facility KNN assignment
- ANN candidate rerank
- robot collision hit-count

Clear multi-thread wins on this Mac:

- facility KNN assignment: `2.18x`
- Hausdorff directed summary: `2.82x`
- ANN candidate rerank: `1.72x`

The Linux run confirms the same pattern with slightly larger absolute times:
facility KNN assignment `2.18x`, Hausdorff directed summary `2.51x`, and ANN
candidate rerank `1.82x` versus Embree 1-thread.

Limited or no auto-thread wins:

- DB, graph, fixed-radius threshold summaries, segment/polygon compact summaries, and Barnes-Hut candidate summary are currently dominated by Python process startup, JSON materialization, small native kernels, or native-assisted CPU refinement.
- `polygon_set_jaccard` is a small non-scaled compatibility fixture in this harness and should not be used as a throughput claim.

## Boundary

This is app-level wall-clock timing, not pure native Embree traversal timing. The numbers include Python CLI startup, JSON parsing, app construction, and output materialization.

The changes do not claim that every app is now a full native Embree implementation. Several apps remain native-assisted or compact-summary-only:

- DBSCAN: native fixed-radius core flags only, not native cluster expansion.
- Outlier: native fixed-radius density threshold only, not a general anomaly engine.
- Polygon overlap/Jaccard: Embree candidate discovery plus CPU exact refinement.
- Barnes-Hut: RTDL candidate generation only; Python still owns force evaluation.

## Verification

Focused tests:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal741_embree_compact_app_perf_harness_test tests.goal738_graph_app_scaled_summary_test tests.goal739_db_app_scaled_summary_test -v
```

Result: `12` tests OK.

Linux focused tests in the clean temp checkout:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal741_embree_compact_app_perf_harness_test tests.goal738_graph_app_scaled_summary_test tests.goal739_db_app_scaled_summary_test -v
```

Result: `12` tests OK.

Additional checks:

```bash
PYTHONPATH=src:. python3 -m py_compile examples/rtdl_dbscan_clustering_app.py examples/rtdl_outlier_detection_app.py examples/rtdl_hausdorff_distance_app.py scripts/goal714_embree_app_thread_perf.py tests/goal741_embree_compact_app_perf_harness_test.py
git diff --check
```

Result: both passed.

## Next Embree Work

- Run the same harness on Linux and Windows once those machines are available for large-scale comparison.
- Add a scalable compact mode for `polygon_set_jaccard` if it remains a public performance target.
- If pure native timing is needed, add per-backend internal timing counters rather than relying on Python CLI wall-clock.
