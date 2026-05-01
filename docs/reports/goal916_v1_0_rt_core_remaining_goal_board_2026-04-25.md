# Goal916 v1.0 RT-Core Remaining Goal Board

Date: 2026-04-25

## Purpose

This report answers the current question: what remains before the v1.0 target
that every public RTDL app has a real NVIDIA RT-core-backed path, with honest
scope boundaries and no per-app pod restarts.

## Current Count

- Public apps tracked in the RT-core migration matrix: `16`.
- Current `rt_core_ready`: `3`.
- Current `rt_core_partial_ready`: `13`.
- Apps with cloud artifacts already present locally from the 2026-04-25 pod
  session but not yet promoted by review: `3`.

## App Board

| App | Current RT-core status | RT-backed part already present | Remaining work before v1.0-ready claim path |
| --- | --- | --- | --- |
| `database_analytics` | `rt_core_partial_ready` | OptiX DB BVH candidate discovery plus native C++ exact filtering/grouping for prepared compact summaries. | Interface tuning and phase proof that Python/materialization is not dominant; no SQL/DBMS claim. |
| `graph_analytics` | `rt_core_partial_ready` | `visibility_edges` uses `rt.visibility_pair_rows(...)`; BFS/triangle have explicit native graph-ray candidate-generation modes. | Run Goal914 on RTX for fixed graph artifact; keep BFS bookkeeping and triangle set-intersection outside the RT claim. |
| `service_coverage_gaps` | `rt_core_partial_ready` | Prepared OptiX fixed-radius threshold traversal for compact gap summaries. | Review existing `goal811_service_coverage_rtx.json` against baselines before promotion. |
| `event_hotspot_screening` | `rt_core_partial_ready` | Prepared OptiX fixed-radius count traversal for compact hotspot summaries. | Review existing `goal811_event_hotspot_rtx.json` against baselines before promotion. |
| `facility_knn_assignment` | `rt_core_partial_ready` | Prepared OptiX service-coverage threshold decision path. | Package same-semantics profiler/baselines; no ranked nearest-depot or KNN-assignment claim. |
| `road_hazard_screening` | `rt_core_partial_ready` | Explicit native OptiX segment/polygon summary gate. | Review existing `goal888_road_hazard_native_optix_gate_rtx.json`; default public path remains gated until accepted. |
| `segment_polygon_hitcount` | `rt_core_partial_ready` | Explicit native OptiX hit-count gate exists. | Run Goal807 strict RTX artifact with same-semantics CPU/PostGIS baselines where available. |
| `segment_polygon_anyhit_rows` | `rt_core_partial_ready` | Native bounded pair-row emitter exists behind explicit mode. | Run Goal873 strict RTX artifact; require row digest parity and zero overflow. |
| `polygon_pair_overlap_area_rows` | `rt_core_partial_ready` | OptiX native-assisted LSI/PIP candidate discovery; exact area refinement remains CPU/Python. | Review pair-overlap 20k artifact and keep claim limited to candidate discovery. |
| `polygon_set_jaccard` | `rt_core_partial_ready` | OptiX native-assisted LSI/PIP candidate discovery. | Goal913 found 20k parity failure; run Goal914 Jaccard diagnostic chunk sizes before any promotion. |
| `hausdorff_distance` | `rt_core_partial_ready` | Prepared OptiX fixed-radius threshold decision for `Hausdorff <= radius`. | Run same-semantics threshold-decision profiler on RTX; no exact Hausdorff-distance claim. |
| `ann_candidate_search` | `rt_core_partial_ready` | Prepared OptiX fixed-radius candidate-coverage decision. | Run same-semantics threshold-decision profiler on RTX; no ANN index/ranking claim. |
| `outlier_detection` | `rt_core_ready` | Prepared OptiX fixed-radius scalar threshold-count summary. | Keep in batched RTX validation; do not present row-output neighbor mode as the claim path. |
| `dbscan_clustering` | `rt_core_ready` | Prepared OptiX fixed-radius scalar core-flag/core-threshold summary. | Keep cluster expansion separate from native timing; no full DBSCAN clustering claim. |
| `robot_collision_screening` | `rt_core_ready` | Prepared ray/triangle any-hit scalar pose-count path with packed input and prepared pose-index buffers. | Keep as flagship RTX path; continue phase-clean profiler validation. |
| `barnes_hut_force_app` | `rt_core_partial_ready` | Prepared OptiX node-coverage decision path. | Run node-coverage profiler on RTX; no force-vector or opening-rule acceleration claim. |

## Existing Cloud Artifacts To Intake Before Next Pod

These local artifacts should be reviewed before starting another pod:

- `docs/reports/cloud_2026_04_25/goal811_service_coverage_rtx.json`
  records `copies=20000`, `optix_prepare=6.518379669636488s`,
  `optix_query=0.6260500205680728s`, `python_postprocess=0.03535711392760277s`.
- `docs/reports/cloud_2026_04_25/goal811_event_hotspot_rtx.json`
  records `copies=20000`, `optix_prepare=6.69359050039202s`,
  `optix_query=1.1063673989847302s`, `python_postprocess=0.11933588702231646s`.
- `docs/reports/cloud_2026_04_25/goal888_road_hazard_native_optix_gate_rtx.json`
  records `copies=20000`, `status=pass`, `strict_pass=true`, and no strict
  failures.

These are useful artifacts, but this report does not promote them. They need a
bounded intake review against same-semantics baselines and a two-AI consensus
record before the public matrix changes.

## Next Local Work Before Another Pod

1. Review and summarize the three existing cloud artifacts above.
2. Decide whether service coverage, event hotspot, and road hazard can be
   promoted from `needs_real_rtx_artifact` to claim-review status.
3. Package the next pod batch so it runs all remaining missing RTX artifacts in
   one session: Goal914 graph/Jaccard, Goal807, Goal873, Goal887 decision
   apps, and any retained active regression paths.
4. Do not start a cloud pod until the batch is explicit, ordered, and
   OOM-bounded.

## Boundary

The v1.0 target is not "every full application is entirely accelerated by RT
cores." The target is: every public app has a clearly named RTDL path where the
RT-relevant core operation uses NVIDIA RT-core traversal, with Python used for
orchestration, validation, or domain-specific postprocessing when appropriate.
