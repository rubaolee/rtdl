# Goal 707: App RT-Core Red Line And DB/Graph/Spatial Audit

Date: 2026-04-21
Status: accepted after consensus review and blocker fix

## Purpose

This report records the corrected app standard after the discussion about the
paper-derived RTDL demos.

RTDL does not need to reproduce a full paper implementation for every app.
The purpose of an RTDL app is to show that the RTDL language/runtime owns the
ray-tracing or spatial-query acceleration core, while Python may own
orchestration, exact validation, clustering expansion, plotting, reporting, and
application policy.
In short: the RTDL language/runtime owns the ray-tracing or spatial-query acceleration core.

The red line is stricter than "the app has a `--backend optix` flag":

- an app may claim RTDL acceleration only for the part that actually routes
  through an RTDL backend traversal, BVH, point query, ray query, or native
  spatial-query primitive;
- an app may claim NVIDIA RT-core acceleration only when the measured OptiX path
  uses OptiX traversal such as `optixTrace` over an OptiX acceleration structure
  on RTX-class hardware;
- CUDA kernels inside the OptiX backend library are GPU compute, not RT-core
  traversal;
- Embree BVH and point-query execution is real RT-style CPU traversal, not GPU
  RT-core execution;
- Python post-processing is allowed, but it must not be described as native
  backend acceleration.

## Consensus Request

Ask reviewers to check two things:

1. Is the red line above technically correct and clear enough for public docs?
2. Is the status audit below honest for the current DB, graph, and spatial apps?

## Consensus Result

- Codex: ACCEPT after fixing the app-engine support label contradiction found
  by Claude.
- Claude: initial BLOCK because four host-indexed OptiX app paths were labeled
  `direct_cli_native`; the finding was valid and the labels were changed to
  `direct_cli_compatibility_fallback`. Claude re-review returned ACCEPT.
- Gemini Flash: ACCEPT on the original red-line audit and ACCEPT after
  re-reviewing the Claude blocker fix.

Consensus files:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal707_claude_review_2026-04-21.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal707_codex_response_to_claude_block_2026-04-21.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal707_gemini_flash_review_2026-04-21.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal707_gemini_flash_rereview_2026-04-21.md`

## Current App Status

### DB Apps

Public app:

- `/Users/rl2025/rtdl_python_only/examples/rtdl_database_analytics_app.py`

Current answer:

- Yes, the DB app routes bounded DB kernels through RTDL native backends when
  the app uses Embree, OptiX, or Vulkan.
- The OptiX DB path has real native DB BVH candidate discovery, but current
  app-level performance is still classified as `python_interface_dominated`.
- The app must not claim full DBMS behavior, SQL behavior, transaction support,
  query-planner behavior, or a broad speedup.
- The safe claim is bounded RTDL DB-kernel execution with native/backend
  candidate discovery and CPU/Python-owned orchestration/materialization.

Important boundary:

- DB can be a valid RTDL app today.
- DB is not yet a clean NVIDIA RT-core app-performance flagship because packing,
  candidate copy-back, exact filtering/grouping, and dict-row materialization
  can dominate the app-level timing.

### Graph Apps

Public app:

- `/Users/rl2025/rtdl_python_only/examples/rtdl_graph_analytics_app.py`

Current answer:

- Embree graph BFS and triangle-count paths use real Embree CPU BVH/point-query
  execution over graph edge points.
- OptiX and Vulkan graph paths are currently host-indexed correctness paths.
- Therefore the public graph app does not currently support a NVIDIA RT-core
  acceleration claim.

Important boundary:

- Graph is a valid RTDL language/runtime app today.
- Graph is not yet a valid OptiX RT-core performance app today.
- The next graph performance goal must implement or promote native
  graph-to-ray/BVH traversal on OptiX before renting RTX time for graph claims.

### Spatial Apps

Public spatial/proximity apps:

- `/Users/rl2025/rtdl_python_only/examples/rtdl_service_coverage_gaps.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_event_hotspot_screening.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_facility_knn_assignment.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_road_hazard_screening.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_segment_polygon_hitcount.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_segment_polygon_anyhit_rows.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_polygon_pair_overlap_area_rows.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_polygon_set_jaccard.py`

Current answer:

- Service coverage, event hotspot, and facility assignment expose Embree
  spatial-query paths. These are real Embree CPU BVH/point-query executions,
  not NVIDIA RT-core executions.
- Road hazard and segment/polygon apps expose CPU, Embree, OptiX, and Vulkan
  entry points, but the public OptiX app performance matrix still classifies
  the default segment/polygon OptiX app path as `host_indexed_fallback` until a
  native path is explicitly promoted and gated.
- Polygon-pair overlap rows and polygon-set Jaccard are currently CPU-reference
  public scripts, so they make no RT-core claim.

Important boundary:

- Several spatial apps are valid RTDL apps today because their RTDL core is a
  bounded spatial join or proximity query.
- Only apps whose current measured path uses real OptiX traversal should be
  included in NVIDIA RTX RT-core performance claims.

### Paper-Derived Spatial/Physics Apps

Public apps:

- `/Users/rl2025/rtdl_python_only/examples/rtdl_hausdorff_distance_app.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_ann_candidate_app.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_outlier_detection_app.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_dbscan_clustering_app.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_robot_collision_screening_app.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_barnes_hut_force_app.py`

Current answer:

- Robot collision is the current cleanest OptiX traversal candidate because it
  uses ray/triangle any-hit traversal.
- Outlier detection and DBSCAN have optional OptiX fixed-radius summary modes
  that use native OptiX traversal for bounded density/core-flag summaries, but
  default row paths remain `cuda_through_optix`.
- Hausdorff, ANN, and Barnes-Hut are valid RTDL-plus-Python demos today, but
  their current OptiX paths are CUDA-through-OptiX or app/Python dominated.
  Goal706 documents how they can become RT-core targets; it does not claim
  they already are RT-core accelerated.

## Evidence Pointers

- `/Users/rl2025/rtdl_python_only/docs/app_engine_support_matrix.md`
- `/Users/rl2025/rtdl_python_only/docs/application_catalog.md`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/app_support_matrix.py`
- `/Users/rl2025/rtdl_python_only/src/native/embree/rtdl_embree_api.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_workloads.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/vulkan/rtdl_vulkan_core.cpp`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_outlier_detection_app.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_dbscan_clustering_app.py`

## Decision

Current DB, graph, and spatial apps should remain in the app catalog, but public
performance language must distinguish:

- RTDL app support;
- native/backend spatial-query support;
- GPU compute through an RTDL backend;
- NVIDIA RT-core traversal on RTX-class hardware.

No DB, graph, or broad spatial app should be added to an RTX RT-core
performance benchmark until its measured path passes the readiness gate in
`/Users/rl2025/rtdl_python_only/docs/app_engine_support_matrix.md`.
