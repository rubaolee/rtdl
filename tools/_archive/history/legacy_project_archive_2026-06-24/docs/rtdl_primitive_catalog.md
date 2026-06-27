# RTDL Primitive Catalog And Promotion Rules

Date: 2026-06-03

Status: generated internal architecture catalog. This document organizes
the current RTDL primitive surface; it does not authorize public release
wording, public speedup claims, external ABI stability, authors-code
parity, or paper reproduction claims.

> Generated from `src/rtdsl/primitive_hierarchy.py` by
> `scripts/generate_rtdl_primitive_catalog.py`. Do not hand-edit this
> file; change the Python hierarchy or renderer and regenerate it.

## What Primitive Means

An RTDL primitive is an app-independent runtime operation that RTDL agrees
to own, schedule, optimize, and test across supported execution paths.

A primitive must have:

- app-independent semantics;
- typed inputs and outputs;
- explicit result layout;
- backend or partner lowering rules;
- deterministic, tolerance, capacity, and overflow behavior;
- correctness tests and evidence boundaries;
- claim wording that blocks app/product overreach.

If removing operation `X` would force multiple apps to reimplement the
same low-level behavior, `X` is a primitive candidate. If removing `X`
only breaks one domain's interpretation, `X` is app code.

| Operation | Classification | Reason |
| --- | --- | --- |
| `ANY_HIT` | Primitive | Many apps need existence over rays, segments, or primitives. |
| `COUNT_HITS` | Primitive | Many apps need count summary without materializing hit rows. |
| `group_sum_i64` | Shared grouped-reduction operation | Reusable grouped aggregation across columnar and app-adapter paths. |
| DBSCAN cluster expansion | App code | It is DBSCAN domain semantics. |
| Robot pose/link sampling | App code | It is robotics domain lowering. |
| Barnes-Hut inverse-square force law | App or partner code | It is workload math, even if given a generic-looking name. |

## Hierarchical Primitive Organization

The top-level organization is a dependency hierarchy. Lower layers provide
runtime substrate for higher layers. Stability, maturity, backend coverage,
and implementation owner are metadata on each node; they are not the hierarchy.

The source-of-truth code for this hierarchy is
`src/rtdsl/primitive_hierarchy.py` and is exported as:

```python
rtdsl.primitive_hierarchy()
rtdsl.primitive_layer_map()
rtdsl.validate_primitive_hierarchy()
```

For the current discovery workflow, the same node data also carries a metadata overlay
for user-intent search. The hierarchy remains the governance/dependency
source of truth; the discovery API is only an index over those nodes:

```python
rtdsl.primitive_index()
rtdsl.find_primitive(intent="count", shape="fixed_radius", dim="3d")
rtdsl.describe_primitive("traversal.fixed_radius_count_threshold")
rtdsl.lint_new_primitive(candidate_node)
```

Discovery facets use the controlled families `intent:*`, `shape:*`,
`dim:*`, `output:*`, `exactness:*`, and `keying:*`. New promoted
primitives that overlap an existing primitive's key facets must record
`considered_alternatives` and `distinct_from`; otherwise the duplicate
gate fails closed. This keeps the catalog searchable without turning RTDL
into an app-shaped library.

Approved layer order:

```text
1. Execution / Residency
2. Traversal
3. Row Emission
4. Bounded Materialization
5. Reduction
6. Continuation
7. Candidate / Experimental
```

Dependency rule:

```text
Execution / Residency
-> Traversal
-> Row Emission
-> Bounded Materialization or Reduction
-> Continuation
-> App semantics
```

App semantics are deliberately outside the hierarchy. If a proposed
native node needs DBSCAN, robot, contact, collision, RayDB, RayJoin,
RTNN, Barnes-Hut force-law, SQL, or graph-domain meaning, it is
app/partner code unless it is redesigned as an app-independent behavior.

## Generated Validation Snapshot

- Generator version: `rtdl.primitive_catalog.generated.v1`
- Hierarchy validation valid: `True`
- Node count: `58`
- Unknown capability tags: `-`
- Missing dependencies: `-`
- Backward dependencies: `-`
- Strict discovery metadata validation valid: `True`
- Strict discovery metadata missing: `-`
- Semantic search preview validation valid: `True`
- Semantic search preview executes: `False`
- Semantic search preview uses embeddings: `False`
- Semantic search preview auto partner selection: `False`
- Composition recipe validation valid: `True`
- Composition recipe count: `6`
- Advisory planner validation status: `accept`
- Advisory planner executes: `False`
- Advisory planner auto partner selection: `False`
- Promotion metadata enforced by default: `False`

## Current Hierarchy

```text
Execution / Residency Layer (layer.execution_residency)
  Prepared RT State (execution.prepared_rt_state)
  Buffer Descriptors (execution.buffer_descriptors)
  Partner-Resident Handoff (execution.partner_resident_handoff)
  Capacity / Overflow Contract (execution.capacity_overflow_contract)
  Spatial Order Points 2D (execution.spatial_order_points_2d)
  Spatial Order Segments 2D (execution.spatial_order_segments_2d)
  Segment Columns 2D (execution.segment_columns_2d)
Traversal Layer (layer.traversal)
  ANY_HIT (traversal.any_hit)
  CLOSEST_HIT / First-Hit-Like Paths (traversal.closest_hit)
  COUNT_HITS (traversal.count_hits)
  AABB_INDEX_QUERY_2D Predicates (traversal.aabb_index_query_2d)
    point_contains (traversal.aabb_point_contains)
    range_contains (traversal.aabb_range_contains)
    range_intersects (traversal.aabb_range_intersects)
  FIXED_RADIUS_COUNT_THRESHOLD (traversal.fixed_radius_count_threshold)
Row Emission Layer (layer.row_emission)
  Generic Candidate / Witness Rows (rows.generic_candidate_rows)
  RAY_TRIANGLE_HIT_STREAM_3D (rows.ray_triangle_hit_stream_3d)
  AABB range_intersection_rows (rows.aabb_range_intersection_rows)
  EXPANDED_AABB_POINT_MEMBERSHIP_2D (rows.expanded_aabb_point_membership_rows)
  POINT_CLOSED_SHAPE_BOUNDARY_EVENT_COLUMNS_2D (rows.point_closed_shape_boundary_event_columns)
  SEGMENT_PAIR_INTERSECTION_ROWS_2D (rows.segment_pair_intersection_rows_2d)
  Segment / Polygon Rows (rows.segment_polygon_rows)
  Fixed-Radius Neighbor Rows (rows.fixed_radius_neighbor_rows)
  AGGREGATE_FRONTIER_COLLECT_2D (rows.aggregate_frontier_collect)
  Graph / Triangle Witness Rows (rows.graph_triangle_witness_rows)
Bounded Materialization Layer (layer.bounded_materialization)
  COLLECT_K_BOUNDED (materialization.collect_k_bounded)
  Prepared Output Buffers (materialization.prepared_output_buffers)
  Row Schema Validation (materialization.row_schema_validation)
Reduction Layer (layer.reduction)
  Scalar Reductions (reduction.scalar)
    COUNT_HITS (reduction.count_hits)
    Canonical Graph-Cycle Count (reduction.graph_cycle_count)
    REDUCE_INT(COUNT|SUM) (reduction.reduce_int)
    REDUCE_FLOAT(MIN|MAX|SUM) (reduction.reduce_float)
  Grouped / Keyed Reductions (reduction.grouped)
    group_any (reduction.group_any)
    group_count (reduction.group_count)
    group_sum_i64 / group_sum_f64 (reduction.group_sum)
    group_min / group_max (reduction.group_min_max)
    group_sum_count / group_stats (reduction.group_stats)
    RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D (reduction.ray_triangle_primitive_grouped_i64)
  Columnar Compact Summary (reduction.columnar_compact_summary)
Continuation Layer (layer.continuation)
  Fixed-Radius Graph Continuation (continuation.fixed_radius_graph)
  Predicate-Aware Boundary Union (continuation.predicate_aware_boundary_union)
  Explicit Partner Continuation (continuation.partner_resident)
  Segmented / Chunked Row Continuation (continuation.segmented_chunked_rows)
  Candidate-Quality / Ranked Summary Continuation (continuation.ranked_summary)
Candidate / Experimental Layer (layer.candidate_experimental)
  Aggregate-Frontier Traversal (candidate.aggregate_frontier_traversal)
  Streamed / Segmented Graph Lowering (candidate.streamed_graph_lowering)
  Device-Resident Grouped Candidate Merge / Finalize (candidate.device_grouped_candidate_merge)
  Closed-Shape Topology-Aware Membership Count 2D (candidate.closed_shape_topology_membership_count_2d)
  Future Zero-Copy Row Streams (candidate.zero_copy_row_streams)
```

## Status Metadata

| Status | Meaning |
| --- | --- |
| `stable_primitive` | RTDL owns the app-independent behavior under stated backend and evidence boundaries. |
| `stable_behavior` | Stable governing behavior or contract, not necessarily a standalone external primitive. |
| `stable_compatibility_path` | Supported compatibility behavior with explicit naming and claim boundaries. |
| `internal_substrate` | Shared implementation contract used by RTDL paths, but not yet an externally stable primitive. |
| `internal_generic_path` | Generic internal path used by backend adapters or front doors. |
| `candidate_behavior` | Reusable pressure exists, but the primitive contract is not accepted yet. |
| `app_or_partner_code` | Domain semantics, custom math, or partner-specific implementation outside engine ownership. |

## Layer Details

The sections below are generated from every hierarchy node. Users should
first identify the behavior they need, then check status, backend
coverage, capability tags, and claim boundaries.

### Execution / Residency Layer

Owns prepared runtime state, buffer descriptors, residency, and capacity contracts.

| Node | Status | Summary | Outputs | Depends on | Capabilities | Backends / partners | Boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `execution.prepared_rt_state` | `stable_behavior` | Reusable prepared Embree/OptiX scenes, indexes, and query-side state. | `prepared_handle`, `lifetime_metadata` | - | `intent:exists`, `shape:generic`, `output:columns`, `exactness:bounded`, `keying:none` | backends: `cpu_python_reference`, `cpu`, `embree`, `optix` | - |
| `execution.buffer_descriptors` | `internal_substrate` | Typed host/device buffers and result-buffer descriptors. | `typed_buffer_descriptor`, `result_buffer_descriptor` | - | - | - | - |
| `execution.partner_resident_handoff` | `internal_substrate` | Describes user/partner-owned device columns handed to RTDL without changing app ownership. | `partner_column_descriptor`, `device_pointer_handoff` | - | - | - | - |
| `execution.capacity_overflow_contract` | `stable_behavior` | Shared capacity accounting and fail-closed overflow behavior for exact outputs. | `capacity`, `overflowed`, `complete_candidate_coverage` | - | `intent:collect_rows`, `shape:generic`, `output:rows`, `exactness:bounded`, `keying:none` | backends: `cpu_python_reference`, `cpu`, `embree`, `optix` | - |
| `execution.spatial_order_points_2d` | `stable_behavior` | Deterministically reorder caller-owned 2-D point records for traversal locality before packing. | `ordered_records`, `stable_id_order` | - | `intent:order`, `shape:point_set`, `dim:2d`, `output:columns`, `exactness:exact`, `keying:none` | backends: `cpu_python_reference` | This is a generic preparation hint. It preserves caller IDs and does not add app-specific membership, join, or predicate semantics. |
| `execution.spatial_order_segments_2d` | `stable_behavior` | Deterministically reorder caller-owned 2-D segment records by centroid locality before packing. | `ordered_records`, `stable_id_order` | - | `intent:order`, `shape:segment_set`, `dim:2d`, `output:columns`, `exactness:exact`, `keying:none` | backends: `cpu_python_reference` | This is a generic preparation hint. It preserves caller segment IDs and does not add app-specific intersection, join, overlay, or predicate semantics. |
| `execution.segment_columns_2d` | `stable_behavior` | Normalize caller-owned 2-D segment records into reusable column batches before packing. | `segment_id_column`, `endpoint_columns`, `column_batch` | - | `intent:prepare`, `shape:segment_set`, `dim:2d`, `output:columns`, `exactness:exact`, `keying:caller_id` | backends: `cpu_python_reference` | This is a generic preparation/layout primitive. It preserves caller IDs and geometry columns and does not add app-specific intersection, join, overlay, or predicate semantics. |

Discovery metadata:

| Node | Aliases | Intent phrases | Reference | Distinction |
| --- | --- | --- | --- | --- |
| `execution.prepared_rt_state` | `prepared_rt_state`, `prepared_scene`, `prepared_handle`, `reusable_index` | `reuse prepared Embree or OptiX state across queries`, `find prepared scene and query state lifetime metadata` | docs/features/engine_support_matrix.md | - |
| `execution.capacity_overflow_contract` | `capacity_overflow`, `overflow_contract`, `fail_closed_capacity`, `fail closed overflow capacity`, `bounded_capacity` | `fail closed when exact bounded output capacity is exceeded`, `find overflow and complete coverage metadata for bounded rows` | docs/rtdl_primitive_catalog.md | - |
| `execution.spatial_order_points_2d` | `spatial_order_points_2d`, `morton_point_order`, `z_order_points`, `locality_order_points` | `order 2d points by spatial locality before packing`, `morton order points before packing`, `use morton or axis point ordering while preserving record ids` | docs/rtdl_primitive_catalog.md | Reorders caller-owned query records before execution; it does not prepare an RT scene or emit witness rows. |
| `execution.spatial_order_segments_2d` | `spatial_order_segments_2d`, `morton_segment_order`, `z_order_segments`, `locality_order_segments` | `order 2d segments by centroid locality before packing`, `morton order segments before packing`, `use morton or axis segment ordering while preserving segment ids` | docs/rtdl_primitive_catalog.md | Reorders caller-owned segment records before execution; it does not prepare an RT scene or emit segment-pair witness rows. |
| `execution.segment_columns_2d` | `segment_columns_2d`, `segment_column_batch`, `packed_segment_columns`, `segment_column_layout` | `prepare reusable 2d segment columns before packing`, `convert segment records to id and endpoint columns`, `cache segment column arrays while preserving caller ids` | docs/rtdl_primitive_catalog.md | Builds reusable segment columns for packing and prepared-state inputs; it does not itself perform locality ordering unless the caller requests an order mode, and it does not build an RT scene. |

### Traversal Layer

Owns app-independent RT predicate traversal against prepared or query geometry.

| Node | Status | Summary | Outputs | Depends on | Capabilities | Backends / partners | Boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `traversal.any_hit` | `stable_primitive` | Existence of at least one hit between query geometry and prepared/build geometry. | `hit_flag` | `execution.prepared_rt_state` | `intent:exists`, `shape:generic`, `output:mask`, `exactness:exact`, `keying:none` | backends: `cpu_python_reference`, `cpu`, `embree`, `optix` | - |
| `traversal.closest_hit` | `internal_substrate` | Closest or first accepted hit where the contract needs one representative primitive. | `hit_flag`, `hit_id`, `hit_distance` | `execution.prepared_rt_state` | - | - | - |
| `traversal.count_hits` | `stable_primitive` | Count positive hit results without materializing full witness rows. | `hit_count` | `traversal.any_hit` | `intent:count`, `shape:generic`, `output:scalar`, `exactness:exact`, `keying:none` | backends: `cpu_python_reference`, `cpu`, `embree`, `optix` | - |
| `traversal.aabb_index_query_2d` | `internal_generic_path` | Prepared 2-D AABB point/range predicate queries. | `predicate_count`, `predicate_flag` | `execution.prepared_rt_state` | - | - | - |
| `traversal.aabb_point_contains` | `internal_generic_path` | Indexed AABB contains query point. | `count` | `traversal.aabb_index_query_2d` | - | - | - |
| `traversal.aabb_range_contains` | `internal_generic_path` | Indexed AABB contains query AABB. | `count` | `traversal.aabb_index_query_2d` | - | - | - |
| `traversal.aabb_range_intersects` | `internal_generic_path` | Indexed AABB intersects query AABB. | `count` | `traversal.aabb_index_query_2d` | - | - | - |
| `traversal.fixed_radius_count_threshold` | `stable_primitive` | Count nearby points within a radius and optionally return threshold/core flags. | `count`, `threshold_reached` | `execution.prepared_rt_state` | `intent:count`, `shape:fixed_radius`, `dim:2d`, `dim:3d`, `output:scalar`, `output:mask`, `exactness:exact`, `keying:by_query_id` | backends: `cpu_python_reference`, `cpu`, `embree`, `optix` | - |

Discovery metadata:

| Node | Aliases | Intent phrases | Reference | Distinction |
| --- | --- | --- | --- | --- |
| `traversal.any_hit` | `any_hit`, `exists`, `hit_exists`, `has_hit`, `boolean_hit` | `does any query geometry hit prepared geometry`, `return a boolean hit flag without materializing witness rows` | docs/features/ray_tri_anyhit/README.md | - |
| `traversal.count_hits` | `count_hits`, `hit_count`, `count_positive_hits`, `scalar_count` | `count hits without returning every witness row`, `compute a scalar hit count` | docs/features/ray_tri_hitcount/README.md | - |
| `traversal.fixed_radius_count_threshold` | `fixed_radius_count`, `within_radius_count`, `neighbor_count`, `density_count`, `radius_threshold` | `count points within a radius`, `return neighbor counts and threshold flags per query point` | docs/features/fixed_radius_neighbors/README.md | - |

### Row Emission Layer

Owns exact or candidate row emission before bounded materialization or reduction.

| Node | Status | Summary | Outputs | Depends on | Capabilities | Backends / partners | Boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `rows.generic_candidate_rows` | `internal_substrate` | App-independent row streams that carry IDs, not domain meaning. | `row_stream` | `layer.traversal` | - | - | - |
| `rows.ray_triangle_hit_stream_3d` | `candidate_behavior` | Emit bounded app-free 3-D ray/triangle hit rows for partner continuation. | `ray_id`, `primitive_id` | `traversal.any_hit`, `execution.capacity_overflow_contract` | `intent:collect_rows`, `shape:ray_triangle`, `dim:3d`, `output:rows`, `output:witness`, `exactness:bounded`, `keying:by_ray_id` | backends: `cpu_python_reference`, `embree`, `optix` | The engine emits only ray and primitive ids. Mapping primitive ids to group keys, payload values, predicates, or app rows is app or partner code. |
| `rows.aabb_range_intersection_rows` | `internal_generic_path` | Emit generic (query_id, indexed_id) rows for 2-D AABB intersections. | `query_id`, `indexed_id` | `traversal.aabb_range_intersects`, `execution.capacity_overflow_contract` | - | - | Exact app refinement remains outside this primitive. |
| `rows.expanded_aabb_point_membership_rows` | `candidate_behavior` | Emit generic bounded rows for points contained by caller-expanded 2-D AABBs. | `source_id`, `box_id`, `metadata_flags`, `row_offsets` | `traversal.aabb_point_contains`, `execution.capacity_overflow_contract` | `intent:membership`, `intent:collect_rows`, `shape:aabb`, `dim:2d`, `output:rows`, `exactness:bounded`, `keying:by_query_id` | backends: `cpu_python_reference`, `cpu`, `embree`, `optix` | Box expansion and row interpretation are caller-owned; native code emits app-free IDs only. |
| `rows.point_closed_shape_boundary_event_columns` | `candidate_behavior` | Emit one deterministic first boundary-event column row for each point/closed-shape pair that has a non-colinear crossing along a caller-selected ray direction. | `point_id`, `shape_id`, `boundary_id`, `crossing_t`, `crossing_x`, `crossing_y`, `event_kind` | `traversal.closest_hit`, `execution.capacity_overflow_contract` | `intent:membership`, `intent:nearest`, `intent:collect_rows`, `shape:closed_shape`, `dim:2d`, `output:columns`, `output:witness`, `exactness:exact`, `keying:by_query_id` | backends: `cpu_python_reference`, `planned_optix` | The primitive emits generic boundary-event columns only. Shape membership classification, map/entity lookup, parity rules, and paper-system semantics remain caller-owned. |
| `rows.segment_pair_intersection_rows_2d` | `candidate_behavior` | Emit or count generic 2-D finite segment-pair intersections under an explicit non-collinear, endpoint-inclusive predicate contract. | `left_id`, `right_id`, `intersection_x`, `intersection_y`, `status` | `traversal.any_hit`, `execution.capacity_overflow_contract` | `intent:intersection`, `intent:count`, `intent:collect_rows`, `shape:segment_pair`, `dim:2d`, `output:rows`, `output:scalar`, `output:columns`, `exactness:exact`, `keying:caller_id` | backends: `cpu_python_reference`, `embree`, `optix` | The primitive owns only generic segment-pair intersection semantics. Join interpretation, map/entity lookup, paper-system meaning, and caller-specific grouping remain app or partner code. |
| `rows.segment_polygon_rows` | `internal_substrate` | Generic segment/polygon witness rows used by spatial workloads. | `segment_id`, `polygon_id` | `traversal.any_hit` | - | - | - |
| `rows.fixed_radius_neighbor_rows` | `internal_substrate` | Neighbor candidate rows emitted by fixed-radius search paths. | `query_id`, `neighbor_id`, `distance` | `traversal.fixed_radius_count_threshold` | `intent:collect_rows`, `intent:nearest`, `shape:fixed_radius`, `dim:2d`, `dim:3d`, `output:rows`, `output:witness`, `exactness:bounded`, `keying:by_query_id` | backends: `cpu_python_reference`, `cpu`, `embree`, `optix` | - |
| `rows.aggregate_frontier_collect` | `candidate_behavior` | Emit app-independent aggregate-frontier collect rows: IDs, kind codes, and source offsets from prepared aggregate-tree traversal. | `source_id`, `frontier_kind_code`, `item_id`, `owner_aggregate_id`, `dfs_index`, `resume_index`, `metadata_flags`, `row_offsets` | `rows.generic_candidate_rows`, `execution.capacity_overflow_contract` | `intent:frontier`, `intent:collect_rows`, `shape:aggregate_frontier`, `dim:2d`, `dim:3d`, `output:rows`, `exactness:bounded`, `keying:by_query_id` | backends: `cpu_python_reference`, `cpu`, `embree`, `optix`, `hiprt` | Force laws, scores, and app-owned reductions remain app or partner code. |
| `rows.graph_triangle_witness_rows` | `internal_substrate` | Generic row shapes used by graph-like and triangle-witness examples. | `left_id`, `right_id`, `witness_id` | `rows.generic_candidate_rows` | - | - | Graph interpretation remains app code. |

Discovery metadata:

| Node | Aliases | Intent phrases | Reference | Distinction |
| --- | --- | --- | --- | --- |
| `rows.ray_triangle_hit_stream_3d` | `ray_triangle_rows`, `hit_stream`, `witness_rows`, `all_hit_rows` | `emit bounded ray triangle hit rows`, `collect ray id and primitive id witnesses for partner continuation` | docs/features/ray_tri_anyhit/README.md | - |
| `rows.expanded_aabb_point_membership_rows` | `expanded_aabb_rows`, `aabb_point_membership_rows`, `box_membership_rows` | `emit rows for points inside caller expanded AABBs`, `collect source id and box id membership rows with overflow checks` | docs/features/db_workloads/README.md | - |
| `rows.point_closed_shape_boundary_event_columns` | `point_closed_shape_first_crossing`, `closed_shape_boundary_event`, `first_boundary_crossing`, `best_boundary_crossing`, `upward_ray_boundary_event` | `find the first boundary crossing for points against closed shapes`, `emit typed boundary event columns for point shape probes`, `select a closest crossing boundary event without app entity semantics` | docs/rtdl_primitive_catalog.md | Membership rows answer whether a point is inside a shape, segment/polygon rows emit segment-shape witnesses, and count_hits returns only scalar hit counts; this contract returns the representative boundary event itself. |
| `rows.segment_pair_intersection_rows_2d` | `segment_pair_intersection`, `segment_pair_intersection_count`, `segment_pair_left_id_dense_count`, `line_segment_intersection`, `finite_segment_intersection`, `lsi_count` | `count finite 2d segment pair intersections`, `emit segment pair intersection witness rows`, `reduce segment pair intersections by caller supplied left id`, `find the segment pair denominator and endpoint contract` | docs/reports/goal3625_segment_pair_intersection_contract_foundation_2026-06-06.md | any_hit/count_hits expose only generic traversal summaries; generic_candidate_rows carries id rows without the finite segment predicate; segment_polygon_rows is a different shape family; grouped reductions aggregate explicit keys but do not own the denominator, endpoint, or collinearity policy. |
| `rows.fixed_radius_neighbor_rows` | `fixed_radius_rows`, `neighbor_rows`, `nearest_neighbor_rows`, `radius_neighbors` | `emit neighbor rows within a fixed radius`, `return query neighbor distance rows for later ranking or reduction` | docs/features/fixed_radius_neighbors/README.md | - |
| `rows.aggregate_frontier_collect` | `aggregate_frontier_rows`, `frontier_collect`, `aggregate_tree_rows` | `emit aggregate frontier ids and offsets from prepared aggregate traversal`, `collect generic aggregate tree frontier rows without app force laws` | docs/rtdl_primitive_catalog.md | - |

### Bounded Materialization Layer

Owns bounded exact output materialization and row-schema validation.

| Node | Status | Summary | Outputs | Depends on | Capabilities | Backends / partners | Boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `materialization.collect_k_bounded` | `stable_primitive` | Collect up to K rows with exact fail-closed overflow semantics. | `candidate_id_rows`, `valid_count`, `overflowed` | `rows.generic_candidate_rows`, `execution.capacity_overflow_contract` | `intent:topk`, `intent:collect_rows`, `shape:generic`, `output:rows`, `output:witness`, `exactness:bounded`, `keying:none` | backends: `cpu_python_reference`, `cpu`, `embree`, `optix`, `hiprt` | - |
| `materialization.prepared_output_buffers` | `internal_substrate` | Reusable host/device result buffers for bounded row output. | `prepared_result_buffer` | `execution.buffer_descriptors`, `materialization.collect_k_bounded` | - | - | - |
| `materialization.row_schema_validation` | `stable_behavior` | Validate row width, row ordering, duplicate policy, and exact-output completeness. | `validated_result` | `materialization.collect_k_bounded` | `intent:collect_rows`, `shape:generic`, `output:rows`, `exactness:bounded`, `keying:none` | backends: `cpu_python_reference`, `cpu`, `embree`, `optix`, `hiprt` | - |

Discovery metadata:

| Node | Aliases | Intent phrases | Reference | Distinction |
| --- | --- | --- | --- | --- |
| `materialization.collect_k_bounded` | `collect_k`, `bounded_collect`, `bounded_witness`, `top_k_rows` | `collect a bounded number of witness rows`, `fail closed when exact bounded output overflows capacity` | docs/features/knn_rows/README.md | - |
| `materialization.row_schema_validation` | `row_schema_validation`, `row_width_validation`, `bounded_result_validation` | `validate row width ordering duplicate policy and completeness`, `check bounded row materialization metadata before consuming rows` | docs/rtdl_primitive_catalog.md | - |

### Reduction Layer

Owns compact summaries over traversal hits, rows, or partner-resident columns.

| Node | Status | Summary | Outputs | Depends on | Capabilities | Backends / partners | Boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `reduction.scalar` | `stable_primitive` | Reduce primitive outputs to scalar counts, sums, minima, or maxima. | `scalar_count`, `scalar_sum`, `scalar_min`, `scalar_max` | `layer.traversal` | `intent:reduce`, `shape:generic`, `output:scalar`, `exactness:exact`, `keying:none` | backends: `cpu_python_reference`, `cpu`, `embree`, `optix`, `hiprt` | - |
| `reduction.count_hits` | `stable_primitive` | Scalar count over hit flags or emitted positive rows. | `count` | `traversal.any_hit` | `intent:count`, `shape:generic`, `output:scalar`, `exactness:exact`, `keying:none` | backends: `cpu_python_reference`, `cpu`, `embree`, `optix` | - |
| `reduction.graph_cycle_count` | `stable_primitive` | Scalar count over canonical ascending graph-cycle witness candidates without returning each witness row. | `count` | `rows.graph_triangle_witness_rows`, `reduction.scalar` | `intent:count`, `intent:reduce`, `shape:generic`, `output:scalar`, `exactness:exact`, `keying:none` | backends: `cpu_python_reference`, `cpu`, `embree`, `optix`, `hiprt` | The primitive counts generic canonical graph-cycle witnesses; graph analytics meaning and app interpretation remain outside the engine. |
| `reduction.reduce_int` | `stable_primitive` | Integer count and sum reductions. | `int64_result` | `rows.generic_candidate_rows` | `intent:reduce`, `shape:generic`, `output:scalar`, `exactness:exact`, `keying:none` | backends: `cpu_python_reference`, `cpu`, `embree`, `optix` | - |
| `reduction.reduce_float` | `stable_primitive` | Floating min, max, and sum with explicit tolerance policy. | `float64_result` | `rows.generic_candidate_rows` | `intent:reduce`, `shape:generic`, `output:scalar`, `exactness:exact`, `keying:none` | backends: `cpu_python_reference`, `cpu`, `embree`, `optix` | - |
| `reduction.grouped` | `internal_substrate` | Per-group flags, counts, sums, minima, maxima, and fused stats. | `grouped_rows` | `rows.generic_candidate_rows` | `intent:reduce`, `intent:count`, `shape:generic`, `output:grouped`, `output:scalar`, `exactness:exact`, `keying:by_group_id` | backends: `cpu_python_reference`, `cpu`, `optix`, `hiprt`<br>partner ops: `segmented_count_i64`, `segmented_sum_f64`, `grouped_argmin_f64` | - |
| `reduction.group_any` | `internal_substrate` | Per-group boolean existence. | `group_id`, `any_flag` | `reduction.grouped` | - | - | - |
| `reduction.group_count` | `internal_substrate` | Per-group count aggregation. | `group_id`, `count` | `reduction.grouped` | - | - | - |
| `reduction.group_sum` | `internal_substrate` | Per-group integer or floating sum. | `group_id`, `sum` | `reduction.grouped` | - | - | - |
| `reduction.group_min_max` | `internal_substrate` | Per-group minimum and maximum. | `group_id`, `min`, `max` | `reduction.grouped` | - | - | - |
| `reduction.group_stats` | `internal_substrate` | Fused grouped count, sum, min, and max statistics. | `group_id`, `count`, `sum`, `min`, `max` | `reduction.grouped` | - | - | - |
| `reduction.ray_triangle_primitive_grouped_i64` | `candidate_behavior` | All-hit 3-D ray/triangle primitive-id deduplication followed by grouped integer reduction over app-provided group ids and payloads. | `group_id`, `count`, `sum`, `min`, `max` | `traversal.any_hit`, `reduction.grouped` | `intent:reduce`, `intent:count`, `shape:ray_triangle`, `dim:3d`, `output:grouped`, `exactness:exact`, `keying:by_group_id` | backends: `cpu_python_reference`, `optix` | Query encoding and group/value semantics remain app code. |
| `reduction.columnar_compact_summary` | `stable_compatibility_path` | Compact summaries over app-owned columnar/denormalized input. | `compact_summary` | `execution.partner_resident_handoff`, `reduction.grouped` | `intent:reduce`, `shape:generic`, `output:columns`, `exactness:exact`, `keying:by_group_id` | backends: `cpu_python_reference`, `cpu`, `embree`, `optix` | Not SQL, not a DBMS, and not a query planner. |

Discovery metadata:

| Node | Aliases | Intent phrases | Reference | Distinction |
| --- | --- | --- | --- | --- |
| `reduction.scalar` | `scalar_reduction`, `reduce_scalar`, `count_sum_min_max`, `compact_scalar_summary` | `reduce primitive outputs to scalar counts sums minima or maxima`, `compute compact scalar summaries without returning rows` | docs/features/reduce_rows/README.md | - |
| `reduction.count_hits` | `count_hits_reduction`, `positive_row_count`, `hit_flag_count` | `count hit flags or emitted positive rows`, `compute scalar hit count as a reduction` | docs/features/ray_tri_hitcount/README.md | - |
| `reduction.graph_cycle_count` | `graph_cycle_count`, `canonical_cycle_count`, `triangle_witness_count` | `count canonical graph cycle witnesses without materializing rows`, `compute a scalar count from graph witness candidates` | docs/rtdl_primitive_catalog.md | rows.graph_triangle_witness_rows emits witnesses for downstream interpretation; reduction.count_hits counts generic hit flags and does not own graph-cycle canonical seed validation. |
| `reduction.reduce_int` | `reduce_int`, `integer_reduction`, `integer count sum reductions`, `int_count_sum`, `i64_reduce` | `reduce integer rows to count or sum`, `compute int64 scalar reductions over generic rows` | docs/features/reduce_rows/README.md | - |
| `reduction.reduce_float` | `reduce_float`, `floating_reduction`, `float_min_max_sum`, `f64_reduce` | `reduce floating rows to min max or sum`, `compute float64 scalar reductions with tolerance policy` | docs/features/reduce_rows/README.md | - |
| `reduction.grouped` | `grouped_reduction`, `group_by`, `group_count`, `group_sum`, `segmented_reduction` | `reduce rows per group id`, `compute grouped count sum min max or stats` | docs/features/reduce_rows/README.md | - |
| `reduction.ray_triangle_primitive_grouped_i64` | `ray_triangle_grouped_reduction`, `primitive_grouped_reduction`, `grouped_i64_reduction` | `reduce ray triangle primitive hits by caller supplied group id`, `count or sum primitive payloads per group after ray triangle traversal` | examples/current/research_benchmarks/raydb_style/README.md | Combines ray/triangle traversal with caller-supplied primitive group ids; plain grouped reductions do not perform traversal and count_hits is not keyed. |
| `reduction.columnar_compact_summary` | `columnar_compact_summary`, `columnar_grouped_aggregate`, `columnar_payload_summary` | `summarize app owned columnar payloads with grouped reductions`, `lower columnar aggregate rows without SQL or DBMS semantics` | docs/features/db_workloads/README.md | - |

### Continuation Layer

Owns reusable post-traversal continuations that remain app-independent.

| Node | Status | Summary | Outputs | Depends on | Capabilities | Backends / partners | Boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `continuation.fixed_radius_graph` | `internal_substrate` | Generic continuation over fixed-radius candidate streams and group/component pressure. | `component_or_group_rows` | `rows.fixed_radius_neighbor_rows`, `reduction.grouped` | `intent:components`, `intent:reduce`, `shape:fixed_radius`, `dim:3d`, `output:columns`, `output:grouped`, `exactness:exact`, `keying:by_query_id` | backends: `optix`<br>partner ops: `cupy_grouped_stream_component_labels` | Cluster semantics remain app code. |
| `continuation.predicate_aware_boundary_union` | `candidate_behavior` | Candidate continuation for fixed-radius component grouping with caller-supplied vertex predicates and deterministic boundary-item assignment policy. | `component_signature`, `boundary_assignment_summary`, `policy_metadata` | `rows.fixed_radius_neighbor_rows`, `continuation.fixed_radius_graph` | `intent:components`, `intent:reduce`, `shape:fixed_radius`, `dim:3d`, `output:columns`, `output:grouped`, `exactness:exact`, `keying:by_query_id` | backends: `optix`<br>partner ops: `numba_grouped_stream_component_labels`, `cupy_direct_status_union_preview` | Caller owns predicate meaning and app semantics; RTDL owns only generic predicate flags, component roots, boundary items, and deterministic assignment policy metadata. |
| `continuation.partner_resident` | `internal_substrate` | Partner-selected post-traversal continuation over RTDL buffer descriptors. Partner roles are explicit metadata, not hidden routing or native-engine policy. | `partner_owned_result` | `execution.partner_resident_handoff` | - | - | - |
| `continuation.segmented_chunked_rows` | `internal_substrate` | Page generic row streams with deterministic continuation tokens to avoid unbounded materialization and device-memory pressure. | `row_pages`, `continuation_state` | `rows.generic_candidate_rows`, `execution.capacity_overflow_contract` | `intent:collect_rows`, `shape:generic`, `output:rows`, `output:columns`, `exactness:bounded`, `keying:by_query_id` | backends: `cpu_python_reference`, `cpu`, `embree`, `optix` | - |
| `continuation.ranked_summary` | `internal_substrate` | Summarize candidate quality or bounded nearest/ranked rows without owning app policy. | `ranked_summary` | `rows.fixed_radius_neighbor_rows`, `reduction.scalar` | `intent:nearest`, `intent:topk`, `intent:reduce`, `shape:fixed_radius`, `dim:2d`, `dim:3d`, `output:grouped`, `output:scalar`, `exactness:bounded`, `keying:by_query_id` | backends: `cpu_python_reference`, `cpu`, `embree`, `optix`<br>partner ops: `grouped_argmin_f64`, `grouped_topk_f64` | - |

Discovery metadata:

| Node | Aliases | Intent phrases | Reference | Distinction |
| --- | --- | --- | --- | --- |
| `continuation.fixed_radius_graph` | `fixed_radius_graph_components`, `radius_graph_component_labels`, `grouped_stream_component_labels`, `fixed_radius_component_continuation` | `compute component labels over a fixed radius graph`, `avoid dense adjacency row materialization for fixed radius graph components`, `run grouped stream continuation for fixed radius graph component labels` | docs/reports/goal3155_fixed_radius_graph_component_front_door_2026-06-03.md | Consumes fixed-radius traversal pressure into component-label columns; it does not emit full neighbor rows like rows.fixed_radius_neighbor_rows, page arbitrary row streams like continuation.segmented_chunked_rows, or own app policy beyond the generic component threshold. |
| `continuation.predicate_aware_boundary_union` | `predicate_aware_boundary_union`, `predicate_component_union`, `fixed_radius_boundary_assignment`, `border_assignment_policy`, `predicate_direct_status_grouped_union` | `assign boundary items to deterministic component roots from caller supplied predicate flags`, `compute predicate aware fixed radius component signatures without app specific clustering logic`, `compare counts only and policy bound component size contracts for fixed radius components` | docs/reports/goal4190_rt_dbscan_counts_only_mixed_route_probe_rtx4000ada_2026-06-09.md | Extends fixed_radius_graph with caller-supplied predicate flags and an explicit deterministic boundary assignment policy. It is not plain grouped reduction, not arbitrary row paging, and not an app-specific clustering or DBSCAN primitive. |
| `continuation.segmented_chunked_rows` | `segmented_rows`, `chunked_rows`, `paged_rows`, `streaming_rows` | `page large row streams with deterministic continuation tokens`, `avoid all at once materialization of large generic row outputs` | docs/rtdl_primitive_catalog.md | - |
| `continuation.ranked_summary` | `ranked_summary`, `top_k_summary`, `nearest_ranked`, `candidate_quality` | `summarize nearest candidate quality by query id`, `compute bounded ranked nearest summaries from fixed radius rows` | docs/features/knn_rows/README.md | Summarizes already emitted fixed-radius rows; it does not own traversal or materialize full witness rows like collect_k_bounded. |

### Candidate / Experimental Layer

Records design pressure that is not yet a stable app-independent primitive contract.

| Node | Status | Summary | Outputs | Depends on | Capabilities | Backends / partners | Boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `candidate.aggregate_frontier_traversal` | `candidate_behavior` | Future native/partner lowering of aggregate-tree traversal behind the generic aggregate-frontier row contract. | `frontier_rows`, `summary_inputs` | `rows.aggregate_frontier_collect`, `continuation.partner_resident` | `intent:frontier`, `intent:collect_rows`, `shape:aggregate_frontier`, `dim:2d`, `dim:3d`, `output:rows`, `exactness:bounded`, `keying:by_query_id` | backends: `cpu_python_reference`, `cpu`, `embree`, `optix`, `hiprt` | Force law and scoring math remain app or partner code. |
| `candidate.streamed_graph_lowering` | `candidate_behavior` | Lower large graph-like row contracts without all-at-once materialization. | `row_pages`, `stream_state` | `continuation.segmented_chunked_rows` | `intent:collect_rows`, `shape:generic`, `output:rows`, `exactness:bounded`, `keying:by_query_id` | backends: `cpu_python_reference`, `cpu`, `embree`, `optix` | - |
| `candidate.device_grouped_candidate_merge` | `candidate_behavior` | Merge grouped candidate streams on device before final materialization. | `grouped_candidate_summary` | `reduction.grouped`, `execution.partner_resident_handoff` | `intent:reduce`, `shape:generic`, `output:grouped`, `exactness:bounded`, `keying:by_group_id` | backends: `cpu_python_reference`, `cpu`, `optix`<br>partner ops: `segmented_count_i64`, `segmented_sum_f64`, `grouped_argmin_f64` | - |
| `candidate.closed_shape_topology_membership_count_2d` | `candidate_behavior` | Generic point/closed-shape membership count direction with an executable owner-face Python reference contract, fail-closed incident-face selector, explicit-priority tie-break helper, formal priority pipeline contract, membership-filter pipeline, and future native/device lowering. | `membership_count`, `owner_face_id`, `ownership_status`, `topology_policy_metadata` | `rows.point_closed_shape_boundary_event_columns`, `reduction.grouped` | `intent:membership`, `intent:count`, `shape:closed_shape`, `dim:2d`, `output:scalar`, `output:grouped`, `exactness:exact`, `keying:by_query_id` | backends: `cpu_python_reference`, `planned_optix` | The primitive must expose generic topology and caller-supplied owner-face filtering only. CDB source naming, RayJoin assignment interpretation, map/entity lookup, and paper-system semantics remain app code. |
| `candidate.zero_copy_row_streams` | `candidate_behavior` | Avoid unnecessary host materialization when the consumer remains device-resident. | `device_row_stream` | `execution.partner_resident_handoff`, `rows.generic_candidate_rows` | `intent:collect_rows`, `shape:generic`, `output:columns`, `exactness:bounded`, `keying:by_query_id` | backends: `metadata_only` | - |

Discovery metadata:

| Node | Aliases | Intent phrases | Reference | Distinction |
| --- | --- | --- | --- | --- |
| `candidate.aggregate_frontier_traversal` | `aggregate_frontier_traversal`, `aggregate_tree_traversal`, `frontier_traversal` | `traverse aggregate tree frontier behind generic row contract`, `future lowering for aggregate frontier rows without force law semantics` | docs/rtdl_primitive_catalog.md | - |
| `candidate.streamed_graph_lowering` | `streamed_graph_lowering`, `segmented_graph_rows`, `paged_graph_rows` | `lower large graph like row contracts with segmented row pages`, `avoid all at once graph row materialization` | docs/rtdl_primitive_catalog.md | - |
| `candidate.device_grouped_candidate_merge` | `device_grouped_candidate_merge`, `grouped_candidate_finalize`, `device_grouped_merge` | `merge grouped candidate streams on device before materialization`, `finalize grouped candidate summaries without host row expansion` | docs/rtdl_primitive_catalog.md | - |
| `candidate.closed_shape_topology_membership_count_2d` | `closed_shape_topology_membership_count`, `topology_aware_membership_count`, `face_aware_closed_shape_count`, `boundary_ownership_count`, `ring_chain_membership_count` | `count point membership in closed shapes with explicit face ring chain topology`, `avoid duplicate boundary ownership overcounts in closed shape membership`, `filter closed shape candidates by caller supplied owner face ids`, `derive owner face only when incident topology has a unique maximum`, `break incident topology ties only with caller supplied face priorities`, `find the explicit priority owner face pipeline contract`, `filter closed shape membership candidates after explicit owner face selection`, `use deterministic boundary ownership policy for point closed shape counts` | docs/reports/goal3349_owner_face_priority_pipeline_contract_2026-06-04.md | traversal.count_hits produces scalar counts without topology ownership policy; rows.point_closed_shape_boundary_event_columns emits boundary witnesses but does not classify membership; reduction.grouped only aggregates explicit keys; candidate.device_grouped_candidate_merge merges candidate streams without owning closed-shape boundary degeneracy semantics. |
| `candidate.zero_copy_row_streams` | `zero_copy_row_streams`, `device_resident_rows`, `resident_row_streams` | `avoid host materialization when consuming rows on device`, `future device resident row stream handoff for partner continuation` | docs/research/future_version_to_do_list.md | - |

## Composition Recipes

Recipes are advisory composition metadata over existing primitive nodes.
They do not execute, dispatch, auto-select partners, or authorize
performance claims.

| Recipe | Status | Summary | Primitive steps | Partner policy | Claim boundary |
| --- | --- | --- | --- | --- | --- |
| `recipe.hit_existence_to_count_summary` | `advisory_recipe` | Use a hit predicate followed by a scalar count when witness rows are not needed. | `traversal.any_hit` (traversal: predicate traversal)<br>`traversal.count_hits` (reduction: scalar hit count) | Primitive-first. No partner is required by this recipe. | Counts accepted primitive hit flags only; this is not a whole-app speedup claim. |
| `recipe.fixed_radius_ranked_candidates` | `advisory_recipe` | Compose fixed-radius counts, bounded neighbor rows, and ranked summaries by query id. | `traversal.fixed_radius_count_threshold` (traversal: count or prefilter candidate pressure)<br>`rows.fixed_radius_neighbor_rows` (row_emission: emit bounded neighbor rows)<br>`continuation.ranked_summary` (continuation: summarize candidate quality by query) | Primitive-first for traversal and row contracts. Explicit partner continuation is advisory only when the app chooses unfused ranking logic. | Ranking quality follows the selected row and continuation contract; no ANN or paper-reproduction claim is implied. |
| `recipe.ray_triangle_hit_stream_grouped_summary` | `advisory_recipe` | Compose ray/triangle traversal, bounded hit streams, and grouped reductions over caller-provided keys. | `traversal.any_hit` (traversal: ray/primitive traversal predicate)<br>`rows.ray_triangle_hit_stream_3d` (row_emission: emit app-free hit stream rows)<br>`reduction.ray_triangle_primitive_grouped_i64` (reduction: grouped primitive payload summary) | Primitive-first for supported grouped summaries. Explicit partners are allowed only for caller-chosen unfused continuation and are never auto-selected. | Not SQL, not a paper-system reproduction, and not a broad RT-core or whole-app claim. |
| `recipe.aabb_candidate_rows_to_refinement` | `advisory_recipe` | Use generic AABB predicates and candidate rows before caller-owned exact refinement. | `traversal.aabb_range_intersects` (traversal: generic range predicate)<br>`rows.aabb_range_intersection_rows` (row_emission: emit candidate id rows)<br>`continuation.segmented_chunked_rows` (continuation: page large candidate streams when needed) | Primitive-first for candidate discovery. Any exact-refinement partner is caller selected. | Candidate discovery only; no broad overlay, GIS, or whole-app claim is implied. |
| `recipe.point_closed_shape_boundary_event_selection` | `candidate_recipe` | Use a generic first-crossing boundary-event contract when membership classification needs a representative boundary event instead of only positive membership counts. | `traversal.closest_hit` (traversal: representative boundary-event traversal)<br>`rows.point_closed_shape_boundary_event_columns` (row_emission: emit typed boundary-event columns) | Primitive-first for boundary-event selection. Explicit partners remain caller-selected for classification or grouping after the event columns. | Candidate recipe only. It does not authorize release, paper-reproduction, RT-core speedup, zero-copy/device-residency, or whole-app speedup claims. |
| `recipe.segmented_rows_to_grouped_reduction` | `advisory_recipe` | Page large generic row streams and reduce them by explicit group ids. | `rows.generic_candidate_rows` (row_emission: generic row stream contract)<br>`continuation.segmented_chunked_rows` (continuation: bounded row paging)<br>`reduction.grouped` (reduction: grouped reductions over explicit keys) | Primitive-first when a fused grouped primitive fits; otherwise list explicit partner options for the caller. | A recipe is not a dispatch path and does not authorize zero-copy or performance wording. |

Recipe discovery metadata:

| Recipe | Capabilities | Aliases | Intent phrases | Recommended when | Boundary |
| --- | --- | --- | --- | --- | --- |
| `recipe.hit_existence_to_count_summary` | `intent:exists`, `intent:count`, `shape:generic`, `output:mask`, `output:scalar`, `exactness:exact`, `keying:none` | `hit_count_recipe`, `exists_then_count`, `any_hit_count`, `scalar_hit_count` | `count positive hit predicates without witness rows`, `turn any hit flags into a scalar count summary` | The caller needs a scalar count or boolean summary and not per-hit witness rows. | Caller-owned interpretation of the hit predicate stays outside the recipe. |
| `recipe.fixed_radius_ranked_candidates` | `intent:nearest`, `intent:topk`, `intent:count`, `intent:collect_rows`, `shape:fixed_radius`, `dim:2d`, `dim:3d`, `output:rows`, `output:grouped`, `output:scalar`, `exactness:bounded`, `keying:by_query_id` | `nearest_neighbor_recipe`, `top_k_candidate_recipe`, `fixed_radius_ranked_summary` | `find fixed radius neighbor candidates and summarize nearest quality`, `rank bounded nearest candidates by query id` | The caller needs nearest/top-k style summaries and can bound candidate rows. | Application ranking policy and recall interpretation stay outside the native engine. |
| `recipe.ray_triangle_hit_stream_grouped_summary` | `intent:collect_rows`, `intent:reduce`, `intent:count`, `shape:ray_triangle`, `dim:3d`, `output:rows`, `output:grouped`, `exactness:bounded`, `exactness:exact`, `keying:by_ray_id`, `keying:by_group_id` | `ray_triangle_grouped_summary`, `ray_triangle_grouped_primitive_summary`, `hit_stream_grouped_reduction`, `primitive_payload_summary` | `reduce ray triangle primitive hits by group id`, `collect ray primitive witnesses then summarize caller payloads` | The caller has ray/triangle hits and wants grouped summaries over caller-owned primitive payloads. | Primitive-to-group mapping, payload values, predicates, and app rows remain app or partner code. |
| `recipe.aabb_candidate_rows_to_refinement` | `intent:intersection`, `intent:membership`, `intent:collect_rows`, `shape:aabb`, `dim:2d`, `output:rows`, `exactness:bounded`, `keying:by_query_id` | `aabb_candidate_recipe`, `range_intersection_rows_recipe`, `candidate_pair_rows` | `emit AABB candidate rows for exact caller refinement`, `find range intersection candidates without owning app semantics` | The caller needs reusable candidate pairs and will perform exact domain refinement outside RTDL. | Exact refinement and domain scoring remain caller-owned. |
| `recipe.point_closed_shape_boundary_event_selection` | `intent:membership`, `intent:nearest`, `intent:collect_rows`, `shape:closed_shape`, `dim:2d`, `output:columns`, `output:witness`, `exactness:exact`, `keying:by_query_id` | `closed_shape_boundary_event_recipe`, `first_crossing_membership_recipe`, `boundary_event_selection_recipe` | `select first boundary crossing events for point closed shape probes`, `use boundary event columns before caller owned membership classification` | The caller needs the selected boundary event itself and scalar membership counts are too coarse for the downstream classification. | Boundary-event interpretation, parity policy, entity lookup, and final app membership classification remain caller-owned. |
| `recipe.segmented_rows_to_grouped_reduction` | `intent:collect_rows`, `intent:reduce`, `shape:generic`, `output:rows`, `output:columns`, `output:grouped`, `exactness:bounded`, `exactness:exact`, `keying:by_group_id`, `keying:by_query_id` | `segmented_grouped_reduction`, `chunked_rows_grouped_summary`, `paged_row_reduce` | `page large row streams before grouped reduction`, `avoid unbounded materialization while reducing rows by group id` | The caller has large generic row streams and explicit grouping keys. | Group meaning, value semantics, and final app interpretation remain caller-owned. |

## Advisory Planner

The current planner is an explain-only layer over primitive discovery and
composition recipes:

```python
rtdsl.plan_continuation(intent="nearest", shape="fixed_radius", dim="3d")
rtdsl.validate_primitive_advisory_planner()
```

| Property | Value |
| --- | --- |
| Planner version | `rtdl.primitive_advisory_planner.v1` |
| Executes or dispatches | `False` |
| Auto-selects partners | `False` |
| Claim boundary | Current primitive advisory plans are explain-only metadata. They do not execute, dispatch, auto-select partners, authorize release readiness, authorize public speedup wording, authorize broad RT-core wording, authorize general zero-copy or device-residency wording, or promote internal/candidate primitive steps to stable public primitives. |

Every returned plan exposes the matched recipe, each primitive step, each
step's primitive status, non-stable step warnings, optional partner-support
cells, and a `selected_partner=None` field. A plan can recommend
primitive-first execution or list explicit partner options, but it cannot
make the runtime choice for the user.

## Controlled Discovery Facets

| Facet |
| --- |
| `intent:exists` |
| `intent:count` |
| `intent:nearest` |
| `intent:membership` |
| `intent:intersection` |
| `intent:components` |
| `intent:reduce` |
| `intent:topk` |
| `intent:collect_rows` |
| `intent:frontier` |
| `intent:order` |
| `intent:prepare` |
| `shape:generic` |
| `shape:point_set` |
| `shape:segment_set` |
| `shape:fixed_radius` |
| `shape:closed_shape` |
| `shape:segment_pair` |
| `shape:ray_triangle` |
| `shape:aabb` |
| `shape:point_in_polygon` |
| `shape:aggregate_frontier` |
| `dim:2d` |
| `dim:3d` |
| `output:scalar` |
| `output:rows` |
| `output:grouped` |
| `output:mask` |
| `output:witness` |
| `output:columns` |
| `exactness:exact` |
| `exactness:approx` |
| `exactness:bounded` |
| `keying:none` |
| `keying:by_group_id` |
| `keying:caller_id` |
| `keying:by_query_id` |
| `keying:by_ray_id` |

## App-Owned Boundary Exclusions

The following semantics stay outside native engine primitive ownership:

- DBSCAN cluster expansion
- robot pose/link sampling
- contact manifold interpretation
- collision/contact physics semantics
- Barnes-Hut inverse-square force law
- SQL/DBMS query semantics
- RTNN ANN policy semantics
- RayJoin paper-system reproduction semantics
- triangle-counting graph meaning beyond emitted row contracts

## Promotion Guardrails

- New primitive proposals must preserve app-independent semantics.
- New promoted nodes with overlapping key facets must record
  `considered_alternatives` and `distinct_from`.
- Proposals must paste the `rtdsl.find_primitive(...)` alternatives
  query that was run before creating the node.
- `rtdsl.lint_new_primitive(candidate_node)` is the pre-addition
  duplicate gate.
- Promotion candidates already inserted in a local tree must run
  `rtdsl.validate_primitive_hierarchy(..., enforce_promotion_metadata=True,
  promotion_candidate_ids=(candidate_id,))`; the candidate-scoped gate
  fails closed if near-duplicate metadata is missing.
- Catalog generation and orchestration recipes are separate concerns;
  this catalog records primitive contracts and discovery metadata only.

## Claim Boundary

This catalog does not authorize release readiness, public speedup wording,
zero-copy claims, broad RT-core claims, paper-reproduction claims, or
app-specific native engine logic.
