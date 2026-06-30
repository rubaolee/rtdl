# Goal2026 All-App v1.8 vs v2.0 Pod Comparison

Date: 2026-05-14

Status: current-evidence comparison with fresh pod reruns; not release authorization

## Pod

- Host: `69.30.85.251:22085`
- GPU: `NVIDIA RTX A5000, 570.211.01`
- Source label: `936aff2f1b1d83ee0187c0ef5610db91dd80fd40`
- Checkout on pod: `/root/rtdl_goal2024_936aff2f`

## Result Table

| App | Evidence basis | v1.8 s | v2.0 s | v2/v1.8 | Classification | Fresh pod status |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `database_analytics` | fresh-goal2026-pod-rerun | 6.71738 | 1.57723 | 0.234798 | `positive` | fresh-pod-pass |
| `graph_analytics` | fresh-goal2026-pod-rerun | 16.9713 | 0.000148972 | 8.7779e-06 | `positive-bounded` | fresh-pod-pass |
| `service_coverage_gaps` | latest-accepted-matrix | 0.038096 | 0.000227943 | 0.00598338 | `positive` | not-rerun-in-goal2026 |
| `event_hotspot_screening` | latest-accepted-matrix | 0.0941404 | 0.00018806 | 0.00199766 | `positive` | not-rerun-in-goal2026 |
| `facility_knn_assignment` | latest-accepted-matrix | 0.101372 | 0.00462753 | 0.0456488 | `positive-bounded-exact` | not-rerun-in-goal2026 |
| `road_hazard_screening` | latest-accepted-matrix | 0.00969145 | 0.00393231 | 0.40575 | `positive` | fresh-pod-pass-older-harness |
| `segment_polygon_hitcount` | latest-accepted-matrix | 0.00254414 | 0.000878341 | 0.345241 | `positive` | not-rerun-in-goal2026 |
| `segment_polygon_anyhit_rows` | latest-accepted-matrix | 7.12187 | 1.58276 | 0.222239 | `positive` | fresh-pod-pass-but-small-capacity-slower |
| `polygon_pair_overlap_area_rows` | fresh-goal2026-pod-rerun | 1.18803 | 0.275383 | 0.231799 | `positive-bounded` | fresh-pod-pass |
| `polygon_set_jaccard` | fresh-goal2026-pod-rerun | 0.849128 | 0.192796 | 0.227052 | `positive-bounded` | fresh-pod-pass |
| `hausdorff_distance` | latest-accepted-matrix | 0.325964 | 0.00268638 | 0.00824135 | `positive-bounded-exact` | not-rerun-in-goal2026 |
| `ann_candidate_search` | latest-accepted-matrix | 0.128558 | 0.00472756 | 0.0367739 | `positive-bounded-exact` | not-rerun-in-goal2026 |
| `outlier_detection` | latest-accepted-matrix | 1.35797 | 0.000438552 | 0.000322946 | `positive` | not-rerun-in-goal2026 |
| `dbscan_clustering` | latest-accepted-matrix | 0.00899306 | 0.00259814 | 0.288905 | `positive-bounded-exact` | not-rerun-in-goal2026 |
| `robot_collision_screening` | latest-accepted-matrix | 0.524696 | 0.00983545 | 0.018745 | `positive-subsecond` | fresh-pod-pass-smaller-than-current-matrix |
| `barnes_hut_force_app` | latest-accepted-matrix | 0.103554 | 0.00205643 | 0.0198587 | `positive-bounded-exact` | not-rerun-in-goal2026 |

## Fresh Pod Rerun Summary

- Fresh pass rows: road hazard, segment small row, robot small-scale row, database control, graph control, polygon overlap/Jaccard control.
- Rows marked `latest-accepted-matrix` are backed by latest accepted artifacts already tracked in the current matrix, not by an absence of evidence.
- Fresh blocked row: fixed-radius family failed before timing because the pod rejected generated OptiX PTX for the current CUDA/NVRTC/driver path.
- Fresh diagnostic failure: a naive large segment rerun with `output_capacity=count` overflowed, so the accepted large Goal1940 artifact remains the correct current evidence for that row.
- For road hazard, the fresh runner used the older prepared-reuse harness and measured `0.551x`; the current matrix still prefers the newer Goal2009 cached-triangle-lookup artifact at `0.406x`.

## Interpretation

Every app row in the current release matrix has positive or bounded-positive evidence against the v1.8 Python+RTDL baseline. The fresh pod rerun confirms the two most recent weak-spot closures, graph and polygon control rows, plus database, road hazard, robot, and a small segment row. It does not regenerate the fixed-radius family on this pod because of a PTX/toolchain blocker, and it does not supersede the accepted large segment artifact.

This is not a v2.0 release authorization. It is an all-app performance position: v2.0 is credible enough for final release preparation, while final release still needs the final packet, final gate, and required consensus.

## Boundaries

- Do not claim broad RT-core speedup for every row.
- Do not claim whole-app speedup beyond the measured row contracts.
- Do not claim package-install support from this source-tree pod run.
- Bounded rows remain bounded: graph compressed metric pattern, polygon axis-aligned extent controls, DBSCAN host-bucket index, exact partner-reference rows, and robot subsecond baseline.
