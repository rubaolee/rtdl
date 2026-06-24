# Goal923: Current v1.0 RT-Core Board After Goal922

Date: 2026-04-25

## Purpose

This report refreshes the current v1.0 NVIDIA RT-core app board after Goals918-922. It supersedes the status counts in the earlier Goal916 snapshot; Goal916 remains historical evidence for the pre-promotion state.

## Current Count

- Public apps tracked in the RT-core migration matrix: `18`.
- Current `rt_core_ready`: `6`.
- Current `rt_core_partial_ready`: `10`.
- Current `not_nvidia_rt_core_target`: `2`.

## Ready Apps

These apps or bounded sub-paths are ready for RTX claim review, not automatic public speedup claims:

| App | Ready RT-backed claim path | Boundary |
| --- | --- | --- |
| `service_coverage_gaps` | Prepared OptiX fixed-radius gap-summary traversal. | No nearest-clinic row-output or whole-app service-coverage optimizer claim. |
| `event_hotspot_screening` | Prepared OptiX fixed-radius count-summary traversal. | No neighbor-row or whole-app hotspot analytics claim. |
| `facility_knn_assignment` | Prepared OptiX service-coverage threshold decision. | No ranked nearest-depot KNN assignment claim. |
| `outlier_detection` | Prepared OptiX fixed-radius scalar threshold-count summary. | No neighbor-row or full anomaly-detection-system claim. |
| `dbscan_clustering` | Prepared OptiX core-threshold/core-flag summary. | No full DBSCAN cluster-expansion claim. |
| `robot_collision_screening` | Prepared OptiX ray/triangle any-hit scalar pose-count path. | No full robot planning, kinematics, CCD, or witness-row claim. |

## Partial Apps

| App | RT-backed part already present | Remaining local/cloud work |
| --- | --- | --- |
| `database_analytics` | OptiX DB BVH candidate discovery plus native C++ exact filtering/grouping for prepared compact summaries. | Rerun compact-summary on RTX with Goal921 phase totals; review against CPU/Embree/PostgreSQL same-semantics baselines. |
| `graph_analytics` | `visibility_edges` uses OptiX any-hit; BFS/triangle-count have explicit native graph-ray candidate-generation modes. | Run the combined Goal889/905 graph gate on RTX and review visibility, native BFS, and native triangle-count digests. |
| `road_hazard_screening` | Explicit native OptiX segment/polygon summary gate. | Review or rerun Goal888 strict RTX artifact; default public path remains gated. |
| `segment_polygon_hitcount` | Explicit native OptiX hit-count gate exists. | Run Goal807 strict RTX artifact with same-semantics CPU/PostGIS baselines where available. |
| `segment_polygon_anyhit_rows` | Native bounded pair-row emitter exists behind explicit mode. | Run Goal873 strict RTX artifact; require row-digest parity and zero overflow. |
| `polygon_pair_overlap_area_rows` | OptiX native-assisted LSI/PIP candidate discovery. | Review phase artifact for candidate discovery only; exact area refinement remains CPU/Python. |
| `polygon_set_jaccard` | OptiX native-assisted LSI/PIP candidate discovery. | Resolve the Goal913 20k Jaccard parity failure through targeted diagnostics before promotion. |
| `hausdorff_distance` | Prepared OptiX fixed-radius threshold decision for `Hausdorff <= radius`. | Run same-semantics threshold-decision profiler on RTX; no exact-distance claim. |
| `ann_candidate_search` | Prepared OptiX fixed-radius candidate-coverage decision. | Run same-semantics candidate-threshold profiler on RTX; no ANN index/ranking claim. |
| `barnes_hut_force_app` | Prepared OptiX node-coverage decision path. | Run node-coverage profiler on RTX; no force-vector or opening-rule claim. |

## Out Of NVIDIA Scope

| App | Reason |
| --- | --- |
| `apple_rt_demo` | Apple Metal/MPS RT evidence, not an NVIDIA OptiX/RTX app. |
| `hiprt_ray_triangle_hitcount` | HIPRT-specific validation, not an NVIDIA OptiX app. |

## Next Batch Policy

Do not start a paid cloud pod for one app. The next pod should run a consolidated, OOM-bounded batch for the remaining `needs_real_rtx_artifact` items and the DB Goal921 rerun.

Local work should continue until every command, artifact path, validation mode, and review boundary is explicit.

## Boundary

The v1.0 target is not that every full application is entirely accelerated by RT cores. The target is that every public app has a clearly named RTDL path where the RT-relevant core operation uses NVIDIA RT-core traversal, with Python used for orchestration, validation, or domain-specific postprocessing when appropriate.
