# RTDL App Implementation Matrix

This document explains how the RTDL app examples are implemented at a technical
level. It compares the released v1.0 app model with the current main/v1.5.x
direction, especially the shift from app-specific native continuations toward
generic reductions, bounded collection, and reduced-copy execution.

This is not a public speedup claim. The performance notes below cite measured
Goal1408 evidence only for the exact reported scopes and do not authorize
whole-app acceleration, broad RTX, or true zero-copy wording.

## Cross-App Execution Model

In v1.0, most app examples were Python programs that packed app data into RTDL
query inputs and then called Embree or OptiX native paths. Where the app needed
compact output, v1.0 commonly used app-specific native continuations: native
code knew enough about a named app mode to turn traversal hits into a summary,
flag, count, or area result without returning every candidate row to Python.

In the current main/v1.5.x line, the engineering direction is to preserve the
same app-level semantics while replacing named-app native logic with generic
primitive contracts where possible. The important target primitives are
`ANY_HIT`, `COUNT_HITS`, `REDUCE_FLOAT(MIN|MAX|SUM)`, and
`REDUCE_INT(COUNT|SUM)`. `COLLECT_K_BOUNDED` is still experimental and should
be treated as a promotion-track feature rather than a stable public claim.

The copy boundary is also becoming more explicit. Python still owns app data
construction and result presentation in the Python+RTDL architecture, so some
host-to-native or host-to-device transfer is unavoidable. The current work
reduces bulk content movement by avoiding row materialization when compact
summaries are sufficient, keeping more reduction work in native code, and
making staging/copy behavior measurable. That is reduced-copy or reduced
materialization, not true zero-copy.

## Comparison Table

| App | v1.0 implementation style | Current main/v1.5.x direction | Copy/reduction change | Goal1408 measured status |
| --- | --- | --- | --- | --- |
| Database analytics | Python DB fixtures plus app-specific compact DB summary continuation. | Move summary-producing subpaths toward generic int/float reductions where traversal plus aggregation fits. | Avoid SQL-style row materialization when compact summaries are requested. | Embree slower `0.696x`; OptiX roughly equal `0.980x`. |
| Graph analytics | Python graph fixtures plus graph-native summary continuations for selected subpaths. | Isolate graph work as RTDL traversal plus count/reduction, not a full graph engine. | Omit large discovery/triangle rows in summary modes. | OptiX faster `1.292x`; no cited Embree row in Goal1408 local summary. |
| Service coverage gaps | Fixed-radius household-clinic traversal with app-specific gap summary modes. | Map prepared gap summaries to generic count/threshold reductions. | Return covered/uncovered counts instead of household/clinic/distance rows. | Embree faster `1.594x`; no cited OptiX row. |
| Event hotspot screening | Radius self-join traversal plus app-specific hotspot count/flag summaries. | Express prepared hotspot mode as integer count/threshold reduction. | Return scalar hotspot counts instead of neighbor-pair rows. | Embree faster `1.401x`; no cited OptiX row. |
| Facility KNN assignment | KNN rows plus app-specific coverage-threshold prepared mode. | Keep KNN row modes separate; express coverage decision as fixed-radius reduction. | Avoid ranked KNN rows when only service coverage is requested. | Embree faster `1.451x`; OptiX slower `0.875x`. |
| Road hazard screening | Segment/polygon traversal plus compact hazard summary continuation. | Map hit counts to generic count reductions while Python keeps priority policy. | Avoid full per-road or pair-row payloads in summary modes. | Embree faster `1.163x`; OptiX faster `1.068x`. |
| Segment/polygon hitcount | Direct segment/polygon join with native hit-count continuation. | Express as generic `COUNT_HITS`. | Return counts without pair witnesses when pair IDs are not requested. | Embree slower `0.865x`; OptiX roughly equal `0.981x`. |
| Segment/polygon any-hit rows | App-specific bounded pair-row and compact segment output paths. | Segment flags/counts fit any-hit/count reductions; pair rows wait on bounded collection promotion. | Compact modes omit polygon IDs and pair rows. | Excluded because `COLLECT_K_BOUNDED` was deferred. |
| Polygon-pair overlap area rows | RT-assisted positive candidate discovery plus native exact-area continuation. | Move aggregate count/area summaries toward generic int/float reductions where possible. | Summary mode returns aggregate overlap count/area instead of per-pair rows. | Embree roughly equal `1.031x`; OptiX roughly equal `1.016x`. |
| Polygon-set Jaccard | Bounded overlap candidate discovery plus set-area/Jaccard continuation. | Wait on bounded collection promotion before stable generic row-producing claims. | Compact summaries depend on safe bounded candidate collection. | Excluded because `COLLECT_K_BOUNDED` was deferred. |
| Hausdorff distance | KNN/radius traversal plus Python or native directed-summary reduction. | Threshold decisions map to fixed-radius any-hit/count; exact directed summary remains reduction-heavy. | Directed summaries avoid full KNN rows; threshold decisions avoid witness rows. | Embree faster `1.087x`; OptiX roughly equal `0.969x`. |
| ANN candidate search | Fixed-radius/KNN candidate traversal; Python owns ranking and app policy. | Coverage decision maps to any-hit or threshold reduction. | Avoid candidate rows when only coverage is requested. | Embree slower `0.735x`; OptiX roughly equal `0.998x`. |
| Outlier detection | Radius-neighbor traversal plus Python thresholding or density summaries. | Density/outlier counts map to generic integer reductions. | Scalar modes avoid per-point labels and neighbor rows. | Embree faster `1.175x`; no cited OptiX row. |
| DBSCAN clustering | Radius-neighbor traversal; Python owns cluster expansion and labels. | Core counts/flags move toward count/threshold reductions. | Core-count mode avoids full neighbor rows. | Embree slower `0.777x`; no cited OptiX row. |
| Robot collision screening | Ray/triangle any-hit traversal plus app-specific pose/count continuations. | Pose flags and hit counts fit `ANY_HIT`/`COUNT_HITS`; witness rows remain separate. | Prepared modes avoid per-ray witness row materialization. | Embree slower `0.901x`; OptiX roughly equal `1.028x`. |
| Barnes-Hut force app | Fixed-radius candidate generation plus native candidate summaries. | Node-coverage decisions map to any-hit/count; opening rule and force reduction stay in Python unless separately implemented. | Candidate summaries avoid large candidate-row output. | Embree slower `0.914x`; OptiX roughly equal `1.022x`. |

## App Notes

### Database Analytics

- Example: `examples/rtdl_database_analytics_app.py`.
- App shape: deterministic order/customer/region fixtures become regional
  dashboard summaries and sales-risk aggregate summaries.
- v1.0 implementation: Python prepares compact database fixtures and dispatches
  RTDL-backed summary modes. Native continuation can return compact DB summary
  data rather than materialized SQL-style rows.
- Current implementation direction: retain Python as the DB fixture and policy
  layer while moving summary-producing work toward generic integer/float
  reductions where the query can be expressed as traversal plus aggregation.
- Copy/reduction behavior: the important win is avoiding row-list payloads when
  the app only needs counts or aggregate summaries. This is not a DBMS, SQL
  engine, or end-to-end database acceleration claim.
- API surface: user-facing execution remains the example CLI with summary modes;
  backend choice and prepared/native modes are explicit.
- Performance evidence: Goal1408 reports Embree current slower than v1.0
  (0.696x) and OptiX roughly equal (0.980x) for the exact 512-copy comparison.
- Pros: clear compact-summary boundary; good example of RTDL as an accelerator
  for a selected data-processing subpath.
- Cons: Python and fixture construction dominate easily; broad database claims
  would be misleading.

### Graph Analytics

- Example: `examples/rtdl_graph_analytics_app.py`.
- App shape: graph fixtures become BFS discovery rows and triangle-count
  summaries through visibility/ray-style formulations.
- v1.0 implementation: Python builds graph fixtures and invokes graph-native
  summary continuations for selected graph subpaths.
- Current implementation direction: maintain the public graph app while
  isolating the accelerated part as RTDL traversal plus count/reduction, not a
  general graph database or full graph analytics engine.
- Copy/reduction behavior: summary modes omit large discovery or triangle row
  payloads where compact counts are enough.
- API surface: graph examples expose summary output and backend selection; the
  graph-system logic stays outside the backend.
- Performance evidence: Goal1408 reports OptiX current faster than v1.0
  (1.292x) for the exact 512-copy graph summary comparison. No Embree Goal1408
  row is available in the cited local report.
- Pros: useful demonstration that graph subpaths can be formulated as RT-style
  traversal.
- Cons: full BFS policy, graph storage, and graph query planning are outside
  RTDL.

### Service Coverage Gaps

- Example: `examples/rtdl_service_coverage_gaps.py`.
- App shape: households and clinics become uncovered-household rows or compact
  covered/uncovered counts.
- v1.0 implementation: fixed-radius neighbor traversal finds household-clinic
  coverage relationships; app-specific summary modes can avoid full row output.
- Current implementation direction: map prepared gap summaries to generic
  count/threshold reductions where possible.
- Copy/reduction behavior: compact summaries avoid emitting household IDs,
  clinic IDs, distances, and load rows when only coverage counts are requested.
- API surface: row output, Embree gap summary, and OptiX prepared gap summary
  modes are explicit.
- Performance evidence: Goal1408 reports Embree current faster than v1.0
  (1.594x) for the exact 512-copy comparison. No OptiX Goal1408 row is present
  in the cited Linux OptiX summary.
- Pros: clean example of replacing many neighbor rows with a scalar summary.
- Cons: clinic siting, routing, and service optimization remain app/Python work.

### Event Hotspot Screening

- Example: `examples/rtdl_event_hotspot_screening.py`.
- App shape: events become hotspot event IDs, neighbor-count rows, or compact
  hotspot counts.
- v1.0 implementation: radius self-join traversal produces neighborhood counts;
  summary modes reduce the output to hotspot decisions or counts.
- Current implementation direction: express the prepared hotspot path as
  traversal plus generic integer count/threshold reductions.
- Copy/reduction behavior: compact modes avoid returning neighbor-pair rows and
  distances when a scalar hotspot count is enough.
- API surface: row, count summary, and prepared count summary modes remain
  user-visible.
- Performance evidence: Goal1408 reports Embree current faster than v1.0
  (1.401x) for the exact 512-copy comparison. No OptiX Goal1408 row is present
  in the cited Linux OptiX summary.
- Pros: very clear reduction workload.
- Cons: domain-specific hotspot interpretation and reporting remain outside the
  backend.

### Facility KNN Assignment

- Example: `examples/rtdl_facility_knn_assignment.py`.
- App shape: customers and depots become nearest-depot assignments, depot-load
  summaries, or service-radius coverage decisions.
- v1.0 implementation: KNN rows and prepared threshold modes are implemented as
  RTDL proximity queries plus app-specific output handling.
- Current implementation direction: preserve assignment modes while treating
  coverage-threshold mode as a generic fixed-radius count/any-hit style
  reduction.
- Copy/reduction behavior: the compact threshold path avoids ranked KNN rows and
  uncovered-customer witness rows when a scalar service decision is enough.
- API surface: assignment output and coverage-threshold prepared mode remain
  separate because they have different semantics.
- Performance evidence: Goal1408 reports Embree current faster than v1.0
  (1.451x) and OptiX current slower than v1.0 (0.875x) for the exact 512-copy
  comparisons.
- Pros: good example of one app exposing both row-producing KNN and compact
  decision modes.
- Cons: ranked KNN, fallback choices, and allocation policies are not the same
  as the compact threshold decision.

### Road Hazard Screening

- Example: `examples/rtdl_road_hazard_screening.py`.
- App shape: road segments and hazard polygons become per-road hit counts,
  priority segment IDs, or compact hazard summaries.
- v1.0 implementation: segment/polygon traversal plus native compact summary
  paths.
- Current implementation direction: map segment/polygon hit counts to generic
  count reductions while keeping priority/reporting policy in Python.
- Copy/reduction behavior: summary modes avoid returning every per-road or
  segment/polygon row when only priority counts are needed.
- API surface: summary and priority output modes are explicit.
- Performance evidence: Goal1408 reports Embree current faster than v1.0
  (1.163x) and OptiX current faster than v1.0 (1.068x) for exact 512-copy
  comparisons.
- Pros: natural fit for hit-count reduction.
- Cons: GIS routing, road-network semantics, and hazard business rules remain
  outside RTDL.

### Segment/Polygon Hitcount

- Example: `examples/rtdl_segment_polygon_hitcount.py`.
- App shape: segments and polygons become per-segment intersection counts.
- v1.0 implementation: direct segment/polygon join with native hit-count
  continuation.
- Current implementation direction: express the app as generic `COUNT_HITS`
  over the segment/polygon traversal path.
- Copy/reduction behavior: count summaries avoid pair-row materialization when
  pair identities are not requested.
- API surface: hit-count mode is distinct from pair-row/any-hit-row modes.
- Performance evidence: Goal1408 reports Embree current slower than v1.0
  (0.865x) and OptiX roughly equal (0.981x) for exact 512-copy comparisons.
- Pros: one of the cleanest generic reduction candidates.
- Cons: if users need pair witnesses, this path is not enough.

### Segment/Polygon Any-Hit Rows

- Example: `examples/rtdl_segment_polygon_anyhit_rows.py`.
- App shape: segments and polygons become intersecting pairs, segment hit
  counts, or segment flags.
- v1.0 implementation: bounded pair-row style output and compact segment modes
  were app-specific native paths.
- Current implementation direction: pair-row output depends on bounded
  collection promotion, while segment flags/counts fit generic any-hit/count
  reductions.
- Copy/reduction behavior: segment-count and segment-flag outputs reduce
  payload size by omitting polygon IDs and pair rows.
- API surface: row-producing modes and compact per-segment modes must remain
  semantically separate.
- Performance evidence: excluded from Goal1408 v1.5 comparison because
  `COLLECT_K_BOUNDED` was deferred to the v1.5.1 promotion track.
- Pros: useful boundary case for explaining when reduction is enough and when
  bounded collection is required.
- Cons: stable generic pair collection is not yet a public promoted primitive.

### Polygon-Pair Overlap Area Rows

- Example: `examples/rtdl_polygon_pair_overlap_area_rows.py`.
- App shape: polygon pairs become overlap-area rows or compact overlap-area
  summaries.
- v1.0 implementation: RT-assisted positive candidate discovery feeds native
  exact-area continuation for selected overlap summaries.
- Current implementation direction: keep candidate discovery and exact-area
  continuation while moving total-area/count summaries toward generic float/int
  reductions where possible.
- Copy/reduction behavior: summary mode avoids full per-pair area rows and only
  returns aggregate overlap count and area totals.
- API surface: row output and summary output remain distinct.
- Performance evidence: Goal1408 reports Embree roughly equal to v1.0 (1.031x)
  and OptiX roughly equal (1.016x) for exact 512-copy comparisons.
- Pros: demonstrates RTDL as a candidate/refinement accelerator rather than a
  monolithic overlay engine.
- Cons: broad polygon overlay and all GIS topology operations remain outside the
  claim boundary.

### Polygon-Set Jaccard

- Example: `examples/rtdl_polygon_set_jaccard.py`.
- App shape: polygon sets become Jaccard-similarity rows.
- v1.0 implementation: bounded overlap candidate discovery plus native
  set-area/Jaccard continuation for selected app modes.
- Current implementation direction: waits on bounded collection promotion before
  making stable generic claims for the row-producing path.
- Copy/reduction behavior: compact summaries are possible only when bounded
  candidate collection is safe and complete.
- API surface: this app should be described conservatively until
  `COLLECT_K_BOUNDED` exits experimental status.
- Performance evidence: excluded from Goal1408 v1.5 comparison because
  `COLLECT_K_BOUNDED` was deferred to the v1.5.1 promotion track.
- Pros: important stress case for bounded collection.
- Cons: not yet a stable public generic primitive story.

### Hausdorff Distance

- Example: `examples/rtdl_hausdorff_distance_app.py`.
- App shape: two point sets become nearest-neighbor rows, directed Hausdorff
  summaries, or Hausdorff-within-radius decisions.
- v1.0 implementation: KNN/radius traversal feeds Python max-distance reduction
  or native directed-summary continuations.
- Current implementation direction: threshold decision modes map naturally to
  fixed-radius any-hit/count reductions, while exact directed distance remains a
  reduction-heavy app mode.
- Copy/reduction behavior: directed summaries avoid returning full KNN rows.
  Threshold decisions can avoid witness rows entirely.
- API surface: exact directed summary and threshold decision modes must remain
  separate because they answer different questions.
- Performance evidence: Goal1408 reports Embree current faster than v1.0
  (1.087x) and OptiX roughly equal (0.969x) for exact 512-copy comparisons.
- Pros: good illustration of min/max reduction semantics.
- Cons: exact witness reporting and full nearest-neighbor rows are outside the
  compact decision path.

### ANN Candidate Search

- Example: `examples/rtdl_ann_candidate_app.py`.
- App shape: query/data points become candidate rows or candidate-coverage
  decisions.
- v1.0 implementation: fixed-radius/KNN-style traversal produces candidates,
  then Python owns ranking and app policy.
- Current implementation direction: coverage decision maps to generic any-hit or
  threshold reductions; full ANN remains outside RTDL.
- Copy/reduction behavior: compact candidate-coverage output avoids full
  candidate rows when only a coverage decision is requested.
- API surface: candidate rows and coverage decisions are separate modes.
- Performance evidence: Goal1408 reports Embree current slower than v1.0
  (0.735x) and OptiX roughly equal (0.998x) for exact 512-copy comparisons.
- Pros: useful app-generic proximity pattern.
- Cons: approximate indexing, reranking, and recall/quality policy are outside
  RTDL.

### Outlier Detection

- Example: `examples/rtdl_outlier_detection_app.py`.
- App shape: points become neighbor rows, density counts, outlier labels, or a
  scalar outlier count.
- v1.0 implementation: radius-neighbor traversal plus Python thresholding or
  native density summaries.
- Current implementation direction: density counts and scalar outlier counts map
  to generic integer reductions and threshold-count continuations.
- Copy/reduction behavior: scalar count modes avoid per-point labels and
  neighbor rows.
- API surface: density summary, label output, and scalar count output are
  different semantic levels.
- Performance evidence: Goal1408 reports Embree current faster than v1.0
  (1.175x). No OptiX Goal1408 row is present in the cited Linux OptiX summary.
- Pros: strong fit for count/threshold reduction.
- Cons: final labeling and downstream analytics can still dominate.

### DBSCAN Clustering

- Example: `examples/rtdl_dbscan_clustering_app.py`.
- App shape: points become neighbor rows, core counts, core flags, or cluster
  labels.
- v1.0 implementation: radius-neighbor traversal provides core-neighborhood
  information; Python owns expansion and cluster labeling.
- Current implementation direction: core counts and core flags move toward
  generic count/threshold reductions; full cluster expansion stays outside the
  backend.
- Copy/reduction behavior: scalar core-count output avoids full neighbor rows;
  core flags still require per-point output.
- API surface: core-count, core-flag, and full clustering modes must remain
  distinct.
- Performance evidence: Goal1408 reports Embree current slower than v1.0
  (0.777x). No OptiX Goal1408 row is present in the cited Linux OptiX summary.
- Pros: clean demonstration of RTDL accelerating the neighborhood subpath.
- Cons: it is not a full DBSCAN engine acceleration claim.

### Robot Collision Screening

- Example: `examples/rtdl_robot_collision_screening_app.py`.
- App shape: robot link rays and obstacle triangles become hit edges, hit
  counts, or pose collision flags.
- v1.0 implementation: ray/triangle any-hit traversal with app-specific compact
  output and pose-flag native continuations.
- Current implementation direction: pose flags and hit counts are strong
  `ANY_HIT`/`COUNT_HITS` candidates; witness row paths remain separate.
- Copy/reduction behavior: prepared count and pose-flag modes avoid per-ray
  witness row materialization.
- API surface: `hit_count`, `pose_flags`, and witness-row modes answer different
  app needs and should not be merged in documentation.
- Performance evidence: Goal1408 reports Embree current slower than v1.0
  (0.901x) and OptiX roughly equal (1.028x) for exact 512-copy comparisons.
- Pros: simple ray/triangle story; easy to explain what RTDL owns.
- Cons: kinematics, pose generation, planning, and witness visualization remain
  outside RTDL.

### Barnes-Hut Force App

- Example: `examples/rtdl_barnes_hut_force_app.py`.
- App shape: bodies and tree nodes become candidate rows, native candidate
  summaries, node-coverage decisions, or approximate force summaries.
- v1.0 implementation: fixed-radius candidate generation plus app-specific
  native candidate summaries.
- Current implementation direction: node-coverage decisions map to generic
  any-hit/count reductions; force-vector reduction and opening-rule policy stay
  in Python unless separately implemented.
- Copy/reduction behavior: candidate summaries avoid large row output, but the
  full force calculation can still require app-side work.
- API surface: candidate summary, force summary, and node-coverage prepared
  modes are intentionally separate.
- Performance evidence: Goal1408 reports Embree current slower than v1.0
  (0.914x) and OptiX roughly equal (1.022x) for exact 512-copy comparisons.
- Pros: demonstrates RTDL as a candidate-generation engine for a physics-style
  workload.
- Cons: not an end-to-end N-body or force-solver acceleration claim.

## Engineering Lessons

- Apps that naturally reduce to `ANY_HIT` or `COUNT_HITS` are the easiest to
  make app-generic.
- Apps that require exact witnesses, pair rows, or top-K candidate lists need
  bounded collection and must fail closed when buffers are insufficient.
- Reduced-copy work helps most when a row-producing v1.0 path can become a
  compact native summary.
- Python+RTDL cannot make host/device copies disappear when Python owns the
  input data. It can only make the copy boundary explicit and avoid avoidable
  materialization.
- Performance must be reported per exact app mode, backend, machine, scale, and
  command. Whole-app or broad RTX claims require separate reviewed evidence.
