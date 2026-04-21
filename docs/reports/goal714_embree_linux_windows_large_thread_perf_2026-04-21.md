# Goal 714: Embree Linux/Windows Large Multithreaded App Performance

Date: 2026-04-21

Status: ACCEPT

## Scope

Goal 714 runs the public Embree app surface on both controlled remote machines:

- Linux: `linux-lx1`, 8 logical CPUs, Python 3.12.3, Embree 4.3.0.
- Windows: `windows-32thread`, 32 logical CPUs, Python 3.11.9.

Both runs used fresh or isolated checkouts at commit `2eacbc9`
(`Warm up Embree app perf samples`).

Artifacts:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal714_embree_app_thread_perf_linux_2026-04-21.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal714_embree_app_thread_perf_windows_2026-04-21.json`

## Methodology

Command shape:

```sh
PYTHONPATH=src:. python3 scripts/goal714_embree_app_thread_perf.py \
  --groups spatial_point,segment_polygon,polygon_overlap,ray,db,graph \
  --copies 1024 \
  --threads ... \
  --warmups 1 \
  --min-sample-sec 2 \
  --max-repeats 10 \
  --timeout 600
```

The harness:

- runs each app once with `cpu_python_reference`;
- runs each app with Embree for every requested thread setting;
- discards one Embree warmup before measured samples;
- hashes backend-normalized JSON payloads to verify CPU-vs-Embree parity;
- records app-level wall-clock timings.

Important boundary: this is whole-app CLI timing. It includes Python startup,
JSON materialization, and app postprocess. It is not pure native Embree
traversal phase timing.

## Correctness Result

Both machines passed:

- Linux: `valid: true`, 16/16 apps valid.
- Windows: `valid: true`, 16/16 apps valid.

Every Embree thread setting produced canonical payloads matching the
CPU-reference output for every app.

## Linux Results

Linux host: 8 logical CPUs.

| App | CPU ref s | Embree 1T s | Embree auto s | Auto speedup vs 1T | Best thread | Best speedup |
|---|---:|---:|---:|---:|---:|---:|
| database_analytics | 0.182 | 0.196 | 0.197 | 0.99x | 1 | 1.00x |
| graph_analytics | 0.183 | 0.196 | 0.195 | 1.00x | auto | 1.00x |
| service_coverage_gaps | 3.158 | 0.271 | 0.273 | 0.99x | 1 | 1.00x |
| event_hotspot_screening | 8.972 | 0.348 | 0.348 | 1.00x | 4 | 1.00x |
| facility_knn_assignment | 8.197 | 1.451 | 0.637 | 2.28x | auto | 2.28x |
| road_hazard_screening | 0.180 | 0.194 | 0.194 | 1.00x | 2 | 1.00x |
| segment_polygon_hitcount | 0.183 | 0.195 | 0.194 | 1.01x | auto | 1.01x |
| segment_polygon_anyhit_rows | 0.182 | 0.196 | 0.196 | 1.00x | 1 | 1.00x |
| polygon_pair_overlap_area_rows | 0.182 | 0.194 | 0.195 | 1.00x | 2 | 1.00x |
| polygon_set_jaccard | 0.183 | 0.194 | 0.195 | 1.00x | 4 | 1.00x |
| hausdorff_distance | 24.937 | 9.094 | 7.710 | 1.18x | auto | 1.18x |
| ann_candidate_search | 9.588 | 5.670 | 5.294 | 1.07x | auto | 1.07x |
| outlier_detection | 23.600 | 8.007 | 8.051 | 0.99x | 1 | 1.00x |
| dbscan_clustering | 30.969 | 15.676 | 15.656 | 1.00x | auto | 1.00x |
| robot_collision_screening | 0.184 | 0.197 | 0.197 | 1.00x | 4 | 1.00x |
| barnes_hut_force | 0.187 | 0.198 | 0.199 | 0.99x | 1 | 1.00x |

## Windows Results

Windows host: 32 logical CPUs.

| App | CPU ref s | Embree 1T s | Embree auto s | Auto speedup vs 1T | Best thread | Best speedup |
|---|---:|---:|---:|---:|---:|---:|
| database_analytics | 0.592 | 0.648 | 0.682 | 0.95x | 1 | 1.00x |
| graph_analytics | 0.619 | 0.588 | 0.615 | 0.96x | 4 | 1.01x |
| service_coverage_gaps | 7.983 | 0.922 | 0.926 | 1.00x | 8 | 1.06x |
| event_hotspot_screening | 22.830 | 1.046 | 0.898 | 1.16x | 16 | 1.20x |
| facility_knn_assignment | 18.326 | 2.184 | 1.228 | 1.78x | auto | 1.78x |
| road_hazard_screening | 0.608 | 0.617 | 0.605 | 1.02x | auto | 1.02x |
| segment_polygon_hitcount | 0.546 | 0.634 | 0.651 | 0.97x | 4 | 1.09x |
| segment_polygon_anyhit_rows | 0.609 | 0.589 | 0.641 | 0.92x | 2 | 1.02x |
| polygon_pair_overlap_area_rows | 0.570 | 0.617 | 0.622 | 0.99x | 2 | 1.08x |
| polygon_set_jaccard | 0.554 | 0.619 | 0.645 | 0.96x | 2 | 1.12x |
| hausdorff_distance | 50.426 | 15.058 | 13.304 | 1.13x | 32 | 1.13x |
| ann_candidate_search | 19.801 | 10.916 | 10.745 | 1.02x | 32 | 1.03x |
| outlier_detection | 57.216 | 20.151 | 19.806 | 1.02x | 16 | 1.02x |
| dbscan_clustering | 76.392 | 39.405 | 38.790 | 1.02x | 2 | 1.02x |
| robot_collision_screening | 0.630 | 0.599 | 0.614 | 0.97x | 1 | 1.00x |
| barnes_hut_force | 0.582 | 0.645 | 0.602 | 1.07x | 16 | 1.11x |

## Interpretation

What is strong:

- Cross-machine correctness is strong: all 16 public Embree app paths match
  CPU-reference outputs on Linux and Windows across every tested thread count.
- Embree is substantially faster than CPU reference for large copy-scaled
  spatial apps, even before considering thread speedup:
  `service_coverage_gaps`, `event_hotspot_screening`,
  `facility_knn_assignment`, `hausdorff_distance`, `ann_candidate_search`,
  `outlier_detection`, and `dbscan_clustering`.
- Multithread speedup is visible where the app shape maps well to the current
  native parallel KNN path:
  `facility_knn_assignment` reaches `2.28x` on Linux auto and `1.78x` on
  Windows auto versus Embree one-thread.
- Hausdorff also benefits modestly: `1.18x` Linux auto and `1.13x` Windows
  auto.

What is not yet strong:

- Fixed-radius apps often beat CPU reference strongly, but do not scale with
  more Embree threads at this app level. This suggests remaining bottlenecks
  are not solved by the current point-query parallel dispatch alone.
- DB, graph, ray, segment/polygon, and polygon-overlap apps are mostly small
  public fixtures or native-assisted paths, so this run should not be used as a
  speedup claim for those app groups.
- Polygon overlap/Jaccard now run through Embree candidate discovery, but the
  exact area/Jaccard refinement remains CPU/Python.

## Next Engineering Actions

1. Add native phase timers for prepared/build, traversal, row materialization,
   and Python postprocess. The current app-level harness identifies symptoms,
   not exact bottleneck phases.
2. Expand native parallel dispatch beyond point KNN/fixed-radius into:
   ray any-hit/count, segment/polygon hit-count and any-hit rows, graph BFS and
   triangle probe, and DB scan/grouped aggregate loops.
3. Add larger scalable fixtures for DB, graph, ray, segment/polygon, and
   polygon-overlap apps so their performance tests are not dominated by CLI
   overhead or tiny public examples.
4. Keep `--warmups 1` or higher in all release-facing perf tests to avoid
   one-time native load/compile/cache artifacts.

## Verdict

Goal 714 establishes cross-machine Embree app correctness and the first honest
large app-level multithreaded performance baseline.

It does not prove broad automatic multicore speedup for all apps yet. The
current performance win is concentrated in large spatial/KNN-style app paths,
with additional parallelization work still required for the other app groups.

Gemini 2.5 Flash Lite review:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal714_gemini_flash_lite_review_2026-04-21.md`
- Verdict: ACCEPT.
