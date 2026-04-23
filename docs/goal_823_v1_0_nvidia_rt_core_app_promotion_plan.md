# Goal 823: v1.0 NVIDIA RT-Core App Promotion Plan

## Objective

Promote RTDL public apps toward honest NVIDIA RT-core acceleration claims while
avoiding repeated paid cloud pod start/stop cycles.

The target is not "every app has an OptiX flag." The target is:

- the app's dominant RTDL operation uses OptiX traversal over an acceleration
  structure on RTX-class hardware;
- correctness is checked against the existing CPU/Embree/oracle path;
- phase timing separates data preparation, acceleration-structure build/reuse,
  traversal, copy-back/materialization, and Python postprocess;
- public docs state the exact claim scope and non-claim.

## Cloud-Cost Rule

Do not ask the user to restart or stop a cloud pod per app.

All local gates, scripts, manifests, and docs must be ready before the next paid
RTX session. The cloud session should run one consolidated batch, collect all
artifacts, and then shut down.

## Promotion Tiers

### Tier 1: Finish Near-Ready RT-Core Apps

These apps already have a real or credible prepared OptiX traversal path.

| App | Current path | Required local action before cloud |
| --- | --- | --- |
| `robot_collision_screening` | prepared OptiX ray/triangle any-hit pose/count summary | keep as flagship; verify packed input, scalar/flag outputs, and phase profiler |
| `outlier_detection` | prepared OptiX fixed-radius threshold summary | keep summary path only; verify row mode is not included as claim path |
| `dbscan_clustering` | prepared OptiX fixed-radius core-flag summary | split core-flag RTDL acceleration from Python cluster expansion |
| `database_analytics` | compact prepared DB session summaries | split interface/materialization from traversal; claim compact summaries only |

### Tier 2: Phase Evidence Before Promotion

These apps have plausible prepared traversal paths but should stay deferred
until phase-clean evidence exists.

| App | Current path | Required action |
| --- | --- | --- |
| `service_coverage_gaps` | prepared OptiX gap summary | run Goal811 phase profiler locally/dry-run and later on RTX |
| `event_hotspot_screening` | prepared OptiX count summary | run Goal811 phase profiler locally/dry-run and later on RTX |

### Tier 3: Native OptiX Redesign Needed

These apps currently have Embree RT-style evidence but the OptiX app path is
host-indexed or CUDA-through-OptiX, not an RT-core claim path.

| App | Current blocker | First implementable direction |
| --- | --- | --- |
| `segment_polygon_hitcount` | native OptiX mode exists but is strict-validation gated | finish Goal807 strict native-vs-host-indexed correctness/perf gate |
| `segment_polygon_anyhit_rows` | compact count path is easier than pair-row output | promote compact flags/counts first; native pair-row output later |
| `road_hazard_screening` | depends on segment/polygon core | promote only after segment/polygon strict gate passes |
| `graph_analytics` | host-indexed CSR fallback | design real graph-to-RT traversal or keep out of RTX claims |
| `hausdorff_distance` | CUDA-through-OptiX KNN compute | design traversal-friendly Hausdorff summary/candidate method |
| `ann_candidate_search` | CUDA-through-OptiX KNN/ranking | design RT candidate culling plus explicit ranking/refinement |
| `barnes_hut_force_app` | Python tree/opening/force reduction dominates | use RT traversal only for candidate node selection and split force timing |

### Tier 4: App Surface Needed First

These apps have Embree/native-assisted paths but no OptiX/NVIDIA app surface.

| App | Required action |
| --- | --- |
| `facility_knn_assignment` | design real RT-assisted nearest/ranking path; do not substitute fixed-radius threshold |
| `polygon_pair_overlap_area_rows` | add OptiX candidate-discovery surface before any claim |
| `polygon_set_jaccard` | add OptiX candidate-discovery surface before any claim |

## Goal Sequence

1. Goal823: write and test this promotion plan.
2. Goal824: add a local pre-cloud readiness gate that validates the active
   cloud manifest, deferred entries, exclusions, public docs, and dry-run
   command plan.
3. Goal825: tighten Tier-1 phase profiler contracts and ensure outputs are
   directly comparable across runs.
4. Goal826: add Tier-2 service/hotspot phase-profiler contracts while keeping
   those apps deferred until real RTX phase runs and review.
5. Goal827: fail closed on incomplete post-cloud artifacts by requiring
   `cloud_claim_contract` and all required phase keys before evidence can be
   reviewed.
6. Goal828: add deferred/filter controls to the one-shot pod runner so active
   and selected deferred entries can run in one paid session.
7. Goal829: publish the single-session cloud runbook with local preflight,
   one batched command, artifact copy-back, shutdown rule, and claim boundary.
8. Goal830+: return to segment/polygon strict packaging and the design reports
   for graph, Hausdorff/ANN, Barnes-Hut, facility KNN, and polygon
   overlap/Jaccard before implementation.

## Exit Criteria

- No active RTX manifest entry uses `cuda_through_optix`, `host_indexed_fallback`,
  or `not_optix_exposed`.
- Deferred entries have explicit activation gates.
- Excluded apps are explicit and documented.
- One local command can prove "ready to start one cloud pod and run the batch."
- The runbook `docs/rtx_cloud_single_session_runbook.md` is followed for paid
  pod sessions; no per-app restart/stop loop is used.
- No release or speedup claim is made before cloud evidence and review.
