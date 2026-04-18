# RTDL v0.8.0 Support Matrix

Date: 2026-04-18
Status: released as `v0.8.0`

## Workload/App Surface

v0.8 app-building examples:

| App | Public example | Primary RTDL primitive |
| --- | --- | --- |
| Hausdorff distance | `examples/rtdl_hausdorff_distance_app.py` | `knn_rows(k=1)` |
| ANN candidate search | `examples/rtdl_ann_candidate_app.py` | `knn_rows(k=1)` |
| Outlier detection | `examples/rtdl_outlier_detection_app.py` | `fixed_radius_neighbors` |
| DBSCAN clustering | `examples/rtdl_dbscan_clustering_app.py` | `fixed_radius_neighbors` |
| Robot collision screening | `examples/rtdl_robot_collision_screening_app.py` | `ray_triangle_hit_count` |
| Barnes-Hut force approximation | `examples/rtdl_barnes_hut_force_app.py` | `fixed_radius_neighbors` |

## Backend Matrix

| App | CPU Python reference | CPU/oracle | Embree | OptiX | Vulkan | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Hausdorff distance | yes | yes | yes | yes | yes | Goal507 Linux performance evidence |
| ANN candidate search | yes | yes | yes | yes | yes | Goal524 Linux characterization; optional SciPy comparison path exists but was skipped in Goal524 because SciPy was absent |
| Outlier detection | yes | yes | yes | yes | yes | Goal524 Linux characterization; not a production anomaly-detection framework |
| DBSCAN clustering | yes | yes | yes | yes | yes | Goal524 Linux characterization; not a production clustering engine |
| Robot collision screening | yes | yes | yes | yes | no | Vulkan is intentionally not exposed until the Goal509 per-edge hit-count mismatch is fixed |
| Barnes-Hut force approximation | yes | yes | yes | yes | yes | Goal509 separates RTDL candidate-generation timing from Python force reduction |

## Platform Matrix

| Platform | Status | Evidence |
| --- | --- | --- |
| Linux | primary validation platform | Goal523 and Goal529 public command harnesses pass `88/88`; Goal529 full test discovery passes `232` tests; Embree/OptiX/Vulkan probes pass |
| macOS | bounded local platform | Goal528 full test discovery passes `232` tests; public command harness passes available commands with expected OptiX/Vulkan skips |
| Windows | historical bounded support, not the primary v0.8 release gate | v0.7/v0.6 evidence remains preserved; v0.8 post-doc-refresh validation is Linux/macOS-centered |

## Current Validation Gates

Goal528 macOS post-doc-refresh audit:

- `232` tests, `OK`
- public command harness: `62` passed, `0` failed, `26` skipped

Goal529 Linux post-doc-refresh validation:

- `232` tests, `OK`
- public command harness: `88` passed, `0` failed, `0` skipped
- Embree `(4, 3, 0)`, OptiX `(9, 0, 0)`, Vulkan `(0, 1, 0)`
- PostgreSQL available on the host, though PostgreSQL is not part of the v0.8
  app support matrix

## Boundary Notes

- v0.8.0 is an app-building release, not a DB release.
- PostgreSQL remains part of earlier DB/graph validation history, not a v0.8
  app backend flag.
- ANN candidate search is candidate-subset reranking, not a full ANN index.
- Outlier detection and DBSCAN are app demos over neighbor rows, not production
  ML/clustering frameworks.
- Robot collision screening is bounded discrete screening, not full robotics or
  continuous swept-volume collision detection.
- Barnes-Hut is candidate-generation plus Python force reduction, not a full
  N-body solver.
- Stage-1 proximity performance evidence is within-RTDL-backend
  characterization, not external-baseline speedup evidence.
