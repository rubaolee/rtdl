# Goal1409 v1.5 vs v1.0 Linux Performance Results

Date: 2026-05-06

This report records same-command, same-scale v1.5 candidate vs v1.0 application
performance measurements on the local Linux host `192.168.1.20` (`lx1`). It is
evidence for release engineering and regression triage. It does not, by itself,
authorize public whole-app speedup wording.

## Environment

- Host: `lx1`
- OS: Ubuntu Linux, kernel `6.17.0-20-generic`
- CPU: Intel Core i7-7700HQ, 4 cores / 8 threads
- GPU: NVIDIA GeForce GTX 1070, driver `580.126.09`
- CUDA compiler: `nvcc` release `12.0`
- OptiX SDK headers: `/home/lestat/vendor/optix-dev`
- Clean benchmark clone: `/home/lestat/rtdl_goal1408_perf`
- v1.5 candidate commit: `e76adc4c1bc4d05ede46bf4d6cde1d315769e01f`
- v1.0 release commit: `b9c9620af78a2fab92083d43af312bb6310e452a`
- Scale: `copies=512`, `iterations=3`

OptiX was measured on a GTX 1070. This is NVIDIA OptiX backend evidence, not RTX
RT-core evidence.

## Artifact Index

- Embree raw artifact:
  `docs/reports/goal1408_v1_5_vs_v1_0_perf_linux_embree/`
- OptiX raw artifact:
  `docs/reports/goal1408_v1_5_vs_v1_0_perf_linux_optix/`
- Harness source:
  `scripts/goal1408_v1_5_vs_v1_0_perf_runner.py`
- Harness tests:
  `tests/goal1408_v1_5_vs_v1_0_perf_runner_test.py`

The Linux clone was reset to `origin/main`, the harness tests passed, and OptiX
was built with:

```sh
make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev CUDA_PREFIX=/usr/local/cuda
```

## Embree Results

| App | v1.0 sec | v1.5 sec | v1.0/v1.5 | Status |
| --- | ---: | ---: | ---: | --- |
| `database_analytics` | 0.001488 | 0.001700 | 0.876x | v1.5 slower |
| `service_coverage_gaps` | 0.011171 | 0.011730 | 0.952x | roughly equal |
| `event_hotspot_screening` | 0.018273 | 0.018704 | 0.977x | roughly equal |
| `facility_knn_assignment` | 0.093146 | 0.086695 | 1.074x | v1.5 faster |
| `road_hazard_screening` | 0.007889 | 0.012611 | 0.626x | v1.5 slower |
| `segment_polygon_hitcount` | 0.022352 | 0.022415 | 0.997x | roughly equal |
| `polygon_pair_overlap_area_rows` | 0.088796 | 0.092176 | 0.963x | roughly equal |
| `hausdorff_distance` | 0.093992 | 0.089602 | 1.049x | roughly equal |
| `ann_candidate_search` | 1.095467 | 1.097309 | 0.998x | roughly equal |
| `outlier_detection` | 0.011656 | 0.011946 | 0.976x | roughly equal |
| `dbscan_clustering` | 0.011325 | 0.011802 | 0.960x | roughly equal |
| `robot_collision_screening` | 0.346853 | 0.343838 | 1.009x | roughly equal |
| `barnes_hut_force_app` | 0.086842 | 0.087414 | 0.993x | roughly equal |

Embree interpretation: v1.5 is mostly performance-neutral against v1.0 at this
small Linux scale. One app is modestly faster (`facility_knn_assignment`), two
apps are slower (`database_analytics`, `road_hazard_screening`), and the
remaining measured apps are within the harness rough-equality band.

## OptiX Results

| App | v1.0 sec | v1.5 sec | v1.0/v1.5 | Status |
| --- | ---: | ---: | ---: | --- |
| `database_analytics` | 0.004171 | 0.004254 | 0.980x | roughly equal |
| `graph_analytics` | 0.531221 | 0.411316 | 1.292x | v1.5 faster |
| `facility_knn_assignment` | 0.000097 | 0.000111 | 0.875x | v1.5 slower |
| `road_hazard_screening` | 0.007960 | 0.007451 | 1.068x | v1.5 faster |
| `segment_polygon_hitcount` | 0.033669 | 0.034314 | 0.981x | roughly equal |
| `polygon_pair_overlap_area_rows` | 0.748401 | 0.736527 | 1.016x | roughly equal |
| `hausdorff_distance` | 0.000155 | 0.000160 | 0.969x | roughly equal |
| `ann_candidate_search` | 0.000085 | 0.000086 | 0.998x | roughly equal |
| `robot_collision_screening` | 0.000106 | 0.000103 | 1.028x | roughly equal |
| `barnes_hut_force_app` | 0.000083 | 0.000081 | 1.022x | roughly equal |

OptiX interpretation: v1.5 improves `graph_analytics` and modestly improves
`road_hazard_screening` on this GTX 1070 host. `facility_knn_assignment` is
slower, but both measured medians are below 0.2 ms, so this row is too small to
support a meaningful public performance conclusion. The rest are roughly equal.

## Excluded Apps

These apps are intentionally excluded from v1.5 same-contract comparison:

- `apple_rt_demo`: Apple RT is outside the active v1.5 Embree+OptiX scope.
- `hiprt_ray_triangle_hitcount`: HIPRT is outside the active v1.5 Embree+OptiX
  scope.
- `polygon_set_jaccard`: depends on `COLLECT_K_BOUNDED`, deferred to v1.5.1.
- `segment_polygon_anyhit_rows`: depends on `COLLECT_K_BOUNDED`, deferred to
  v1.5.1.

## Release Interpretation

The v1.5 performance story from this Linux run is not "v1.5 is faster than
v1.0 across all apps." The defensible statement is narrower:

- v1.5 preserves roughly comparable app-level performance for most included
  Embree and OptiX app profiles at the measured small scale.
- v1.5 adds standalone-language/runtime architecture and support-matrix
  clarity without broad app-level regression.
- Positive speedup claims remain app/backend/subpath-specific and require the
  raw evidence plus external review before public wording.
- RTX RT-core wording still requires an RTX-class pod run, not this GTX 1070
  OptiX run.
