# Goal848: v1.0 RT-Core Goal Series

Date: 2026-04-23

## Summary

- Public apps: `18`
- RT-core ready now: `16`
- RT-core partial-ready now: `0`
- Need redesign or new surface: `0`
- Out of NVIDIA RT scope: `2`

Priority buckets are execution buckets, not pure status buckets. An app can already be rt_core_ready and still appear in must_finish_first when it is a flagship path with required optimization or claim-packaging work; robot_collision_screening is the current example.

## Priority Buckets

### already_ready_keep_and_optimize

- `graph_analytics`
- `facility_knn_assignment`
- `road_hazard_screening`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`
- `hausdorff_distance`
- `ann_candidate_search`
- `outlier_detection`
- `dbscan_clustering`
- `barnes_hut_force_app`

### must_finish_first

- `database_analytics`
- `service_coverage_gaps`
- `event_hotspot_screening`
- `robot_collision_screening`

### second_wave


### major_redesign_wave


### out_of_scope_for_nvidia_rt

- `apple_rt_demo`
- `hiprt_ray_triangle_hitcount`

## Goal Series

### Goal848: Lock the v1.0 all-in-RT app migration plan

Use the canonical app maturity matrix to define promotion order, acceptance rules, and claim boundaries.

Acceptance:

- Every public app is assigned to a v1.0 bucket.
- Each bucket has an explicit engineering purpose and claim boundary.
- The plan is machine-readable and reviewable.

Consensus: `3-AI for planning significance`

### Goal849: Promote spatial prepared-summary apps to promotion-ready candidates

Package local evidence for service coverage and event hotspot prepared OptiX summary paths using existing profiler and CLI guards.

Acceptance:

- Dry-run phase packet exists for both apps.
- Prepared OptiX summary modes remain guarded by --require-rt-core.
- Cloud inclusion criteria are explicit and bounded.

Consensus: `2-AI before completion`

### Goal850: Reduce DB app host/interface overhead on the OptiX path

Push compact prepared DB outputs and native phase accounting until Python is orchestration only.

Acceptance:

- Prepared DB compact-summary path has phase-clean counters.
- Internal review package shows the dominant app path is no longer materialization-driven.
- Claim remains bounded to prepared DB summary paths.

Consensus: `2-AI before completion`

### Goal851: Promote segment/polygon compact native OptiX paths

Run strict native-vs-host-indexed gating for hit-count and compact outputs before any row-output claim.

Acceptance:

- Explicit native mode passes strict correctness gate.
- Compact summary/count outputs are separated from pair-row output.
- No row-output claim is made without a native row emitter.

Consensus: `2-AI before completion`

### Goal852: Validate graph analytics native RT-core sub-paths

Run the combined graph gate for visibility any-hit plus explicit native BFS/triangle graph-ray candidate generation on RTX hardware.

Acceptance:

- Strict RTX artifact proves row-digest parity for visibility, native BFS, and native triangle-count sub-paths.
- Host-indexed fallback remains the default until the native graph-ray path passes review.
- Shortest-path, graph database, distributed graph analytics, and whole-app graph-system claims remain excluded.

Consensus: `3-AI because it changes strategic scope`

### Goal853: Redesign CUDA-through-OptiX apps into true traversal apps or demote them permanently

Hausdorff, ANN candidate search, and Barnes-Hut require true RT traversal formulations or permanent non-RT-core classification.

Acceptance:

- Each app has a true traversal design or a permanent non-RT-core decision.
- Public docs stop conflating CUDA-through-OptiX with RT-core use.

Consensus: `3-AI because it changes flagship app scope`

### Goal854: Expose or explicitly retire missing OptiX app surfaces

Facility KNN, polygon overlap, and polygon Jaccard need either real OptiX surfaces or explicit retirement from NVIDIA RT-core targets.

Acceptance:

- Each app has a surface decision with rationale.
- Any new OptiX surface has a local correctness gate.

Consensus: `2-AI before completion`

### Goal855: Run one consolidated RTX cloud validation batch after local closure

Use the single-session cloud procedure only after local work is ready.

Acceptance:

- All active-candidate apps have local readiness packets.
- The cloud run is one batched session with preserved artifacts.
- Interpretation stays bounded to exact measured sub-paths.

Consensus: `2-AI before completion`

## Boundary

This plan defines the v1.0 NVIDIA RT-core migration order. It is a planning artifact, not a release authorization and not a public speedup claim.
