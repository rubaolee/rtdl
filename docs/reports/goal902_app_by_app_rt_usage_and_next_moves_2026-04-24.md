# Goal902 App-by-App RT Usage and Next Moves

Date: 2026-04-24

## Purpose

This report summarizes every current public RTDL app from the perspective of
the v0.9.8/v1.0 RT-core effort:

- what the app is for
- what core operations it performs
- how RT is used today
- how RT should be used but is not fully used yet
- the next move plan

The current local closure gates are:

- Goal824 pre-cloud readiness gate: valid
- Goal901 pre-cloud app closure gate: valid

Goal901 reports:

```text
public apps: 18
NVIDIA-target apps: 16
non-NVIDIA apps: 2
active cloud entries: 5
deferred cloud entries: 12
full-batch entries: 17
unique commands: 16
missing cloud coverage: none
unsupported analyzer apps: none
```

Boundary: This is not cloud evidence and not a performance claim. For NVIDIA
RT-core app claims, the next material evidence requires a real RTX run using
the single-session cloud runbook and post-cloud artifact review.
In short, the remaining NVIDIA app-performance evidence requires real RTX artifacts.

## Summary Table

| App | Purpose | Current RT use | Missing / not-yet RT use | Next move |
| --- | --- | --- | --- | --- |
| `database_analytics` | DB-style filtered/grouped analytics | Native OptiX/Embree/Vulkan DB BVH candidate discovery and exact filtering/grouping; compact OptiX summary path is the bounded RT-core candidate | Full row/materialized DB output is still Python/interface dominated; not a DBMS or SQL-engine acceleration claim | Run active cloud DB compact-summary entries, inspect native query vs materialization/postprocess phases, compare to CPU/Embree/PostgreSQL where available |
| `graph_analytics` | Graph visibility and graph analytics demos | Bounded `visibility_edges` scenario maps candidate edges to ray/triangle any-hit traversal; Embree BFS and triangle-count now use ray traversal over graph-edge primitives; OptiX BFS/triangle-count now have explicit native graph-ray mode behind a gate | Shortest path, graph database, distributed graph analytics, and whole-app graph-system acceleration are not RT-core claims | Run the combined deferred Goal889/905 graph RTX gate for visibility any-hit plus explicit OptiX native BFS/triangle-count graph-ray mode before any promotion |
| `apple_rt_demo` | Apple Metal/MPS RT demo | Apple-specific closest-hit / visibility style RT paths | Not a NVIDIA RT-core target; DB/graph-style Apple acceleration is not part of the NVIDIA cloud packet | Keep in Apple engine track; do not include in NVIDIA OptiX cloud batch |
| `service_coverage_gaps` | Coverage-gap detection for facilities vs demand points | Prepared OptiX fixed-radius threshold traversal in compact `gap_summary_prepared` path | Full rows / nearest-clinic style outputs are not the RT-core claim path | Run deferred Goal811 service coverage RTX artifact; compare prepared traversal/query/postprocess phases against CPU/Embree/SciPy baselines |
| `event_hotspot_screening` | Hotspot density screening over event points | Prepared OptiX fixed-radius count traversal in compact `count_summary_prepared` path | Full neighbor rows and whole-app hotspot workflows are not the RT-core claim path | Run deferred Goal811 event hotspot RTX artifact; review native query vs Python summary cost |
| `facility_knn_assignment` | Assign / screen facilities and demand coverage | Prepared OptiX fixed-radius threshold traversal for service-coverage decisions | Ranked KNN assignment, nearest-depot ranking, and fallback assignment remain outside RT-core claim | Run deferred Goal887 facility coverage-threshold artifact; postpone native ranking until after decision-path evidence |
| `road_hazard_screening` | Segment/polygon hazard screening for roads | Native OptiX segment/polygon summary gate exists as deferred path | Default public OptiX behavior remains conservative; full GIS/routing workflow is not an RT-core claim | Run deferred Goal888 native road-hazard gate; require strict parity before changing default classification |
| `segment_polygon_hitcount` | Count segment/polygon intersections | Explicit native OptiX mode exists behind gate; Embree/Vulkan/CPU public paths also exist | Default OptiX path remains host-indexed/fallback until native mode passes strict RTX validation | Run deferred Goal807 native-vs-host-indexed RTX gate; compare native, host-indexed, CPU, and PostGIS when available |
| `segment_polygon_anyhit_rows` | Emit bounded segment/polygon hit rows | Explicit bounded native OptiX pair-row emitter exists | Unbounded pair-row output, overflow behavior, and default promotion are not yet claim-safe | Run deferred Goal873 strict RTX gate; require row digest parity, zero overflow, and output-capacity review |
| `polygon_pair_overlap_area_rows` | Polygon pair overlap area rows | OptiX/Embree native-assisted LSI/PIP candidate discovery, then CPU exact area refinement | Exact polygon area refinement is not native RT; full app speedup cannot be claimed from candidate discovery alone | Run deferred Goal877 pair-overlap phase gate; keep claim to candidate discovery unless native exact refinement is later designed |
| `polygon_set_jaccard` | Polygon-set Jaccard similarity | OptiX/Embree native-assisted LSI/PIP candidate discovery, then CPU exact Jaccard refinement | Exact set-area/Jaccard refinement is CPU/Python-owned | Run deferred Goal877 Jaccard phase gate; review candidate traversal vs CPU exact refinement split |
| `hausdorff_distance` | Directed Hausdorff / threshold decision workload | Prepared OptiX fixed-radius threshold traversal for `Hausdorff <= radius` decision | Exact Hausdorff distance and KNN-style ranking are not the RT-core claim path | Run deferred Goal887 Hausdorff threshold artifact; consider native exact/ranking only after decision path is validated |
| `ann_candidate_search` | ANN candidate coverage / filtering | Prepared OptiX fixed-radius threshold traversal for candidate-coverage decisions | Full ANN index, recall optimizer, HNSW/IVF/PQ/FAISS-like ranking are outside current RTDL RT-core claim | Run deferred Goal887 ANN coverage artifact; keep ranking/post-filtering Python-owned for now |
| `outlier_detection` | Density/outlier summary | Prepared OptiX scalar fixed-radius threshold count; active cloud entry | Default row-returning fixed-radius neighbor path is not the claim path | Run active cloud scalar threshold-count entry; compare native prepared query and scalar copyback to CPU/Embree/SciPy baselines |
| `dbscan_clustering` | DBSCAN core-point identification and clustering demo | Prepared OptiX scalar core-threshold summary; active cloud entry | Python cluster expansion is outside the native RT-core claim; full DBSCAN acceleration is not claimed | Run active cloud scalar core-count/core-flag entry; keep clustering expansion separated from native timing |
| `robot_collision_screening` | Discrete robot collision pose screening | Prepared OptiX ray/triangle any-hit traversal with packed rays, prepared pose indices, and scalar pose-count output; active cloud entry | Full robot planning, continuous collision detection, kinematics, and witness-row output are outside scalar pose-count claim | Run active cloud robot pose-count entry; treat as flagship native RT-core path and inspect preparation vs query phases |
| `barnes_hut_force_app` | Barnes-Hut / N-body candidate coverage demo | Prepared OptiX fixed-radius node-coverage decision path | Opening-rule evaluation, force-vector reduction, and full N-body solver are not native RT-core accelerated | Run deferred Goal887 Barnes-Hut node-coverage artifact; native reductions/opening rules are later work |
| `hiprt_ray_triangle_hitcount` | HIPRT ray/triangle hit-count demo | HIPRT-specific ray/triangle hit-count path | Not a NVIDIA OptiX/RTX target; current HIPRT evidence is SDK/Orochi validation, not AMD GPU validation | Keep in HIPRT backend track; exclude from NVIDIA cloud packet |

## Detailed App Notes

### `database_analytics`

Purpose: demonstrates RTDL as a thin Python-facing wrapper over native
candidate discovery and grouped analytics for DB-like workloads.

Core operations:

- predicate filtering
- grouped count / grouped sum
- compact summary output
- optional PostgreSQL-style baseline comparison

Current RT use: OptiX, Embree, and Vulkan paths use native BVH-style candidate
discovery and exact filtering/grouping. The bounded NVIDIA claim path is
`--backend optix --output-mode compact_summary`, because it avoids full row
materialization when the app only needs summaries.

Not-yet RT use: full DBMS behavior is not a goal. SQL planning, transactions,
joins, indexes, storage layout, and broad DB speedup claims are out of scope.
Within RTDL, the remaining limitation is interface/materialization overhead:
Python packing, ctypes transfer, candidate bitset copyback, grouped-row decode,
and summary postprocess can dominate unless the compact summary path is used.

Next move:

- run the two active DB cloud entries
- inspect `db_query_total_sec`, prepare time, warm-query median, materialization,
  and Python summary phases from Goal762
- compare only same-semantics compact summaries against CPU/Embree/PostgreSQL
  baselines
- do not make broad DB claims unless native query time is isolated and useful

### `graph_analytics`

Purpose: provides graph analytics examples and a bounded graph-to-RT lowering.

Core operations:

- graph visibility-edge filtering
- BFS / graph traversal examples
- triangle-count style graph analytics

Current RT use: the bounded `visibility_edges` mode maps graph edge candidates
to ray/triangle any-hit visibility tests. In addition, the Embree BFS and
triangle-count paths now use ray traversal over graph-edge primitives for
candidate generation. OptiX BFS and triangle-count also expose an explicit
native graph-ray mode behind `RTDL_OPTIX_GRAPH_MODE=native` /
`--optix-graph-mode native`.

Not-yet RT use: OptiX/NVIDIA BFS, triangle counting, shortest paths, and
general graph analytics are not currently RT-core claims. OptiX BFS and
triangle-count native graph-ray mode still needs a real RTX artifact and
external review before promotion.

Next move:

- run deferred Goal889 on real RTX hardware
- accept only the bounded graph sub-paths that pass strict parity and phase
  evidence: visibility any-hit plus explicit native BFS/triangle graph-ray
  candidate generation
- keep the default host-indexed path until native graph-ray passes on RTX

### `apple_rt_demo`

Purpose: demonstrates Apple-specific RT/Metal/MPS style backend behavior for
macOS users.

Core operations:

- ray/triangle closest hit
- visibility/count-style operations
- Apple hardware-gated correctness/performance checks

Current RT use: Apple-specific native-assisted RT paths are exposed through the
Apple demo app.

Not-yet RT use: this app is not a NVIDIA RT-core target. Apple DB/graph support
in lower-level features is not automatically Apple hardware ray-tracing
acceleration.

Next move:

- keep this app in the Apple engine track
- exclude it from NVIDIA OptiX cloud batches
- only make Apple-specific claims from Apple hardware artifacts

### `service_coverage_gaps`

Purpose: identifies demand points or regions not adequately covered by service
facilities.

Core operations:

- fixed-radius coverage tests
- threshold summaries
- optional SciPy/reference baselines

Current RT use: `gap_summary_prepared` uses prepared OptiX fixed-radius
threshold traversal and compact summary output. Embree also provides CPU RT-style
acceleration for comparable radius queries.

Not-yet RT use: row output and nearest-facility ranking are not the current
RT-core claim path. Whole-app service planning is outside the claim.

Next move:

- run deferred Goal811 service coverage artifact on RTX
- compare prepared traversal against CPU/Embree/SciPy same-semantics baselines
- keep claims bounded to compact gap-summary traversal

### `event_hotspot_screening`

Purpose: screens event datasets for local density/hotspot summaries.

Core operations:

- fixed-radius self-neighborhood counts
- hotspot threshold summaries
- CPU/Embree/SciPy comparison

Current RT use: `count_summary_prepared` uses prepared OptiX fixed-radius count
traversal for compact hotspot summaries.

Not-yet RT use: full neighbor-row output and broader anomaly-detection pipelines
are not claim paths.

Next move:

- run deferred Goal811 event hotspot artifact
- review native query time separately from input generation and Python summary
- claim only the prepared count-summary sub-path if evidence supports it

### `facility_knn_assignment`

Purpose: supports facility/demand assignment demos and coverage-style KNN
workflows.

Core operations:

- nearest/fixed-radius facility candidate discovery
- coverage-threshold decisions
- optional fallback ranking or assignment

Current RT use: `coverage_threshold_prepared` uses prepared OptiX fixed-radius
threshold traversal for service-coverage decisions.

Not-yet RT use: true ranked KNN assignment and fallback assignment are not
native RT-core paths today.

Next move:

- run deferred Goal887 facility coverage artifact
- keep the claim to coverage-threshold decisions
- postpone native ranking/reduction design until after threshold evidence is
  reviewed

### `road_hazard_screening`

Purpose: screens road segments against hazard polygons.

Core operations:

- segment/polygon intersection
- compact hit-count or summary output
- optional GIS/PostGIS-style comparison

Current RT use: a native OptiX segment/polygon summary gate exists as a
deferred readiness path. Embree/Vulkan/CPU paths also exist at app level.

Not-yet RT use: default OptiX behavior remains conservative. Full GIS/routing
and hazard-management workflows are not the RT-core claim.

Next move:

- run deferred Goal888 native road-hazard gate
- require strict parity against CPU reference
- only promote native OptiX behavior after real RTX artifact review

### `segment_polygon_hitcount`

Purpose: counts segment/polygon hits for spatial join-style workloads.

Core operations:

- segment/polygon candidate traversal
- hit-count reduction
- optional PostGIS comparison

Current RT use: explicit native OptiX hit-count mode exists, but it remains
behind a deferred gate. Embree and Vulkan paths are exposed.

Not-yet RT use: the default OptiX path is still classified as fallback until
native mode passes strict RTX validation.

Next move:

- run deferred Goal807 native-vs-host-indexed gate
- compare CPU, host-indexed OptiX, native OptiX, and PostGIS where available
- only then decide default-mode promotion

### `segment_polygon_anyhit_rows`

Purpose: emits bounded segment/polygon hit pairs.

Core operations:

- segment/polygon any-hit traversal
- bounded pair-row emission
- row digest and overflow checks

Current RT use: explicit `--backend optix --output-mode rows --optix-mode native`
calls the bounded native OptiX pair-row emitter.

Not-yet RT use: unbounded row emission and default pair-row promotion are not
safe claims yet. Overflow and output-capacity behavior must be reviewed on real
RTX hardware.

Next move:

- run deferred Goal873 strict gate
- require row-digest parity and zero overflow
- decide later whether native mode becomes default or remains explicit

### `polygon_pair_overlap_area_rows`

Purpose: computes polygon-pair overlap area rows for spatial analysis.

Core operations:

- LSI/PIP positive candidate discovery
- grid-cell / exact overlap refinement
- area row output

Current RT use: OptiX and Embree provide native-assisted LSI/PIP candidate
discovery; CPU/Python performs exact area refinement.

Not-yet RT use: exact polygon area computation is not a native RT-core kernel.
The current RT claim can only be candidate discovery, not full overlap-area
acceleration.

Next move:

- run deferred Goal877 pair-overlap phase profiler
- inspect candidate-discovery vs exact-refinement split
- keep full-area speedup unclaimed unless native exact refinement is later
  designed

### `polygon_set_jaccard`

Purpose: computes set-level polygon Jaccard similarity.

Core operations:

- LSI/PIP positive candidate discovery
- exact set-area refinement
- Jaccard ratio calculation

Current RT use: OptiX/Embree native-assisted candidate discovery is used before
CPU exact set-area/Jaccard refinement.

Not-yet RT use: exact Jaccard / set-area reduction is not native RT-core
accelerated.

Next move:

- run deferred Goal877 Jaccard profiler
- separate candidate traversal, copyback, and exact CPU refinement
- keep claims bounded to native-assisted candidate discovery

### `hausdorff_distance`

Purpose: supports Hausdorff-style distance decisions and nearest-neighbor
geometry demos.

Core operations:

- directed distance threshold decision
- fixed-radius candidate coverage
- exact-distance / KNN-style reference paths

Current RT use: `directed_threshold_prepared` uses prepared OptiX fixed-radius
threshold traversal to answer bounded `Hausdorff <= radius` decisions.

Not-yet RT use: exact Hausdorff distance and ranked nearest-neighbor output are
not current RT-core claim paths.

Next move:

- run deferred Goal887 Hausdorff threshold artifact
- compare decision semantics only
- consider exact-distance native ranking later if needed

### `ann_candidate_search`

Purpose: demonstrates approximate/candidate nearest-neighbor screening.

Core operations:

- candidate coverage test
- nearest-neighbor/ranking postprocess in non-claim paths
- optional SciPy/reference comparison

Current RT use: `candidate_threshold_prepared` uses prepared OptiX fixed-radius
threshold traversal for candidate-coverage decisions.

Not-yet RT use: full ANN indexing, ranking, recall optimization, and
FAISS/HNSW-like behavior are outside current RTDL RT-core claims.

Next move:

- run deferred Goal887 ANN candidate artifact
- keep RTDL claim to candidate coverage
- use Python/libraries for ranking unless a native ranking feature becomes a
  deliberate future goal

### `outlier_detection`

Purpose: detects low-density points or outlier-like regions.

Core operations:

- fixed-radius neighbor counting
- threshold-count summary
- optional row-returning neighbor inspection

Current RT use: active prepared OptiX scalar threshold-count path uses RT-core
style traversal and compact scalar output.

Not-yet RT use: default row-returning neighbor output is not the RT-core claim.
Whole anomaly-detection systems are outside scope.

Next move:

- run active cloud prepared scalar threshold-count entry
- compare same-semantics scalar summaries against CPU/Embree/SciPy baselines
- keep row mode separate from claim path

### `dbscan_clustering`

Purpose: demonstrates DBSCAN core-point detection and clustering workflow.

Core operations:

- fixed-radius core-neighbor thresholding
- core-flag/core-count summary
- Python-owned cluster expansion

Current RT use: active prepared OptiX scalar core-threshold summary uses
RT-core style traversal for core detection.

Not-yet RT use: Python cluster expansion is not native RT-core accelerated.
Full DBSCAN clustering speedup is not claimed.

Next move:

- run active cloud prepared core-summary entry
- keep native core detection and Python expansion timings separate
- consider native graph/union expansion only as a later distinct design

### `robot_collision_screening`

Purpose: screens robot poses or edges against obstacle geometry for collision.

Core operations:

- ray/triangle any-hit
- pose flag or scalar pose-count output
- optional CPU oracle validation

Current RT use: flagship OptiX RT-core path. It uses packed rays, prepared pose
indices, prepared ray/triangle any-hit traversal, and scalar pose-count output.

Not-yet RT use: full robot planning, continuous collision detection, kinematics,
and detailed witness-row output are outside the current scalar claim.

Next move:

- run active cloud robot pose-count artifact
- inspect scene prepare, ray prepare, pose-index prepare, and warm query phases
- use this as the first high-priority NVIDIA RT-core performance path

### `barnes_hut_force_app`

Purpose: explores Barnes-Hut-like spatial candidate coverage for N-body style
workloads.

Core operations:

- node/body coverage decision
- candidate filtering
- CPU/Python opening-rule and force reduction

Current RT use: `node_coverage_prepared` uses prepared OptiX fixed-radius
threshold traversal for node-coverage decisions.

Not-yet RT use: Barnes-Hut opening-rule evaluation, force-vector reduction, and
full N-body solving are not RT-core accelerated.

Next move:

- run deferred Goal887 Barnes-Hut node-coverage artifact
- review whether traversal helps candidate coverage at scale
- treat native reductions/opening-rule support as future language/runtime work

### `hiprt_ray_triangle_hitcount`

Purpose: validates HIPRT ray/triangle hit-count support.

Core operations:

- ray/triangle hit-count
- HIPRT SDK/Orochi backend path validation

Current RT use: HIPRT-specific native path is exposed by the app.

Not-yet RT use: this is not a NVIDIA OptiX/RTX app. Current HIPRT evidence is
not AMD GPU validation unless explicitly run on AMD hardware.

Next move:

- keep HIPRT validation separate from NVIDIA RT-core app maturity
- exclude from NVIDIA cloud packet
- revisit AMD GPU evidence only when hardware is available

## Cross-App Next Move Plan

1. Keep local state stable; do not add more cloud one-off scripts unless a new
   local gap is found.
2. Use the single-session cloud runbook when RTX hardware is available.
3. Run one full `Goal769 --include-deferred` batch.
4. Copy back the artifact bundle and individual reports if needed.
5. Run Goal762 post-cloud analysis.
6. Review each app using its allowed claim scope and baseline-review contract.
7. Promote only paths with correctness parity, phase separation, and useful
   native traversal evidence.

## Current Stop Condition

Based on Goal901, local app coverage is complete for pre-cloud purposes. Further
meaningful progress on NVIDIA RT-core app performance requires real RTX
artifacts, unless a new local correctness/doc inconsistency is discovered.
