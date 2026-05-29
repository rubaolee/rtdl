# RTDL Primitive Catalog And Promotion Rules

Date: 2026-05-26

Status: internal architecture catalog. This document organizes the current
RTDL primitive surface; it does not authorize public release wording, public
speedup claims, external ABI stability, authors-code parity, or paper
reproduction claims.

## What Primitive Means

An RTDL primitive is an app-independent runtime operation that RTDL agrees to
own, schedule, optimize, and test across supported execution paths.

A primitive must have:

- app-independent semantics;
- typed inputs and outputs;
- explicit result layout;
- backend or partner lowering rules;
- deterministic, tolerance, capacity, and overflow behavior;
- correctness tests and evidence boundaries;
- claim wording that blocks app/product overreach.

If removing operation `X` would force multiple apps to reimplement the same
low-level behavior, `X` is a primitive candidate. If removing `X` only breaks
one domain's interpretation, `X` is app code.

Examples:

| Operation | Classification | Reason |
| --- | --- | --- |
| `ANY_HIT` | Primitive | Many apps need existence over rays/segments/primitives. |
| `COUNT_HITS` | Primitive | Many apps need count summary without materializing hit rows. |
| `group_sum_i64` | Shared grouped-reduction operation | Reusable grouped aggregation behavior across columnar and app-adapter paths. |
| DBSCAN cluster expansion | App code | It is DBSCAN domain semantics. |
| Robot pose/link sampling | App code | It is robotics domain lowering. |
| Barnes-Hut inverse-square force law | App/partner code | It is workload math, even if given a generic-looking name. |

## Hierarchical Primitive Organization

The top-level organization is a dependency hierarchy. Lower layers provide
runtime substrate for higher layers. Stability, maturity, backend coverage, and
implementation owner are metadata on each node; they are not the hierarchy.

The source-of-truth code for this hierarchy is
`src/rtdsl/primitive_hierarchy.py` and is exported as:

```python
rtdsl.primitive_hierarchy()
rtdsl.primitive_layer_map()
rtdsl.validate_primitive_hierarchy()
```

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

App semantics are deliberately outside the hierarchy. If a proposed native node
needs DBSCAN, robot, contact, collision, RayDB, RayJoin, RTNN, Barnes-Hut
force-law, SQL, or graph-domain meaning, it is app/partner code unless it is
redesigned as an app-independent behavior.

### Current Hierarchy

```text
Execution / Residency
  prepared RT state
  buffer descriptors
  partner-resident handoff
  capacity / overflow contracts

Traversal
  ANY_HIT
  CLOSEST_HIT / first-hit-like paths
  COUNT_HITS
  AABB_INDEX_QUERY_2D predicates
    point_contains
    range_contains
    range_intersects
  FIXED_RADIUS_COUNT_THRESHOLD

Row Emission
  generic candidate / witness rows
  ray/triangle hit stream rows
  AABB range_intersection_rows
  EXPANDED_AABB_POINT_MEMBERSHIP_2D rows
  segment / polygon rows
  fixed-radius neighbor rows
  aggregate-frontier collect rows
  graph / triangle witness rows

Bounded Materialization
  COLLECT_K_BOUNDED
  prepared output buffers
  row schema validation

Reduction
  scalar reductions
    COUNT_HITS
    REDUCE_INT(COUNT|SUM)
    REDUCE_FLOAT(MIN|MAX|SUM)
  grouped / keyed reductions
    group_any
    group_count
    group_sum
    group_min / group_max
    group_sum_count / group_stats
    RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D
  columnar compact summary

Continuation
  fixed-radius graph continuation
  Triton-first partner continuation
  segmented / chunked row continuation (`SEGMENTED_ROW_STREAM` /
    `CHUNKED_ROW_CONTINUATION`)
  candidate-quality / ranked-summary continuation

Candidate / Experimental
  aggregate-frontier traversal
  streamed / segmented graph lowering
  device-resident grouped candidate merge / finalize
  future zero-copy row streams
```

Status metadata used below:

| Status | Meaning |
| --- | --- |
| Stable primitive | RTDL owns the app-independent behavior under stated backend and evidence boundaries. |
| Experimental primitive | A contract exists, but promotion requires additional parity, safety, benchmark, or review gates. |
| Internal substrate | Shared implementation contract used by RTDL paths, but not yet an externally stable primitive. |
| Candidate behavior | Reusable pressure exists, but the primitive contract is not accepted yet. |
| App or partner code | Domain semantics, custom math, or partner-specific implementation that RTDL does not own as a primitive. |
| Rejected candidate | A proposed primitive violated app-independence or safety rules and must stay out of the engine. |

## Layer Details

The sections below provide behavior details for the hierarchy nodes. A user
should first identify the layer and behavior they need, then check status,
backend coverage, and claim boundaries.

### Traversal Layer

These behaviors answer whether prepared/query geometry intersects or hits.

| Primitive or operation | Status | Behavior | Typical outputs |
| --- | --- | --- | --- |
| `ANY_HIT` | Stable primitive | Existence of a hit between query geometry and prepared/build geometry | boolean flag, countable hit flag |

Common composition:

```text
ANY_HIT -> COUNT_HITS
ANY_HIT -> group_any
ANY_HIT -> app-owned postprocessing
```

### Spatial Neighborhood Traversal

These behaviors evaluate fixed-radius spatial relationships without requiring
full neighbor-row materialization.

| Primitive or operation | Status | Behavior | Typical outputs |
| --- | --- | --- | --- |
| `FIXED_RADIUS_COUNT_THRESHOLD_2D` | Stable primitive | Count nearby 2-D points within a radius, optionally threshold-capped | scalar count, threshold predicate, density/core flag |

Examples that compose this behavior: service coverage, hotspot screening,
DBSCAN core predicate counts, and fixed-radius candidate filtering. DBSCAN
cluster expansion and connected components remain app code.

### Exact Geometry Summaries

These behaviors combine geometric candidate discovery with exact compact
summaries.

| Primitive or operation | Status | Behavior | Typical outputs |
| --- | --- | --- | --- |
| `POLYGON_PAIR_EXACT_AREA_SUMMARY` | Stable primitive | Discover candidate polygon pairs and summarize exact integer-grid overlap area | compact area summary |

The stable behavior is not a broad GIS overlay engine. Full overlay semantics,
domain-specific score interpretation, and row-level app workflows remain
outside the primitive.

### Reduction Layer: Scalar Reductions

These behaviors reduce a stream of primitive outputs to scalar summaries.

| Primitive or operation | Status | Behavior |
| --- | --- | --- |
| `COUNT_HITS` | Stable primitive | Count positive hit rows. |
| `REDUCE_FLOAT(MIN)` | Stable primitive | Floating minimum reduction. |
| `REDUCE_FLOAT(MAX)` | Stable primitive | Floating maximum reduction. |
| `REDUCE_FLOAT(SUM)` | Stable primitive | Floating sum reduction with tolerance policy. |
| `REDUCE_INT(COUNT)` | Stable primitive | Integer count reduction. |
| `REDUCE_INT(SUM)` | Stable primitive | Integer sum reduction. |

### Reduction Layer: Grouped And Keyed Reductions

These behaviors reduce rows by group key. They are recorded in
`src/rtdsl/grouped_reduction.py` as `rtdl.grouped_reduction.v1`.

| Primitive or operation | Status | Behavior |
| --- | --- | --- |
| `group_any` | Internal substrate | Per-group boolean existence. |
| `group_count` | Internal substrate | Per-group row/count aggregation. |
| `group_sum_i64` | Internal substrate | Per-group signed integer sum. |
| `group_sum_f64` | Internal substrate | Per-group floating sum. |
| `group_min_i64` | Internal substrate | Per-group signed integer minimum. |
| `group_max_i64` | Internal substrate | Per-group signed integer maximum. |
| `group_sum_count_i64` | Internal substrate | Fused per-group sum and count. |
| `group_stats_i64` | Internal substrate | Fused per-group count, sum, min, and max. |
| `RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D` | Candidate behavior with native OptiX evidence | All-hit 3-D ray/triangle primitive-id deduplication followed by grouped integer reduction over caller-provided group ids and payload values. Goal2645 adds the app-agnostic native symbol; Goal2646 adds typed packed host-buffer use in the RayDB paper-shaped benchmark path plus a prepared device-resident primitive-payload ABI. Query encoding and group/value semantics remain app code. |

Grouped-reduction operations are reusable behavior, but backend support and
external stability are separate decisions. Do not call them stable external
primitives until promotion explicitly says so.

### Reduction Layer: Columnar Compact Summaries

These behaviors produce compact columnar aggregate summaries without claiming
SQL or DBMS semantics.

| Primitive or operation | Status | Behavior | Naming boundary |
| --- | --- | --- | --- |
| columnar compact summary | Stable compatibility path | Conjunctive scan count, grouped integer count, and grouped integer sum over app-owned columnar/denormalized input | `DB_COMPACT_SUMMARY` is a legacy compatibility token; columnar compact summary is the preferred conceptual name. |

This behavior is not SQL, a DBMS, a query planner, joins, indexes,
transactions, or row-output materialization.

### Row Emission And Bounded Materialization Layers

These behaviors return bounded rows or witness/candidate rows rather than only
compact summaries.

| Primitive or operation | Status | Behavior | Boundary |
| --- | --- | --- | --- |
| `RAY_TRIANGLE_HIT_STREAM_3D` | Candidate behavior | Emit bounded app-free `(ray_id, primitive_id)` rows or typed hit columns from 3-D ray/triangle all-hit traversal | Goal2684 adds the generic row contract, CPU reference, Embree native ABI, OptiX native ABI, Python wrappers, and RayDB hit-stream plus Triton continuation wiring. Goal2685 adds the typed-column handoff contract (`ray_ids:int64`, `primitive_ids:int64`) plus generic typed primitive payload columns (`primitive_group_ids:int64`, `primitive_values:float64`) so the app can feed partner continuation without rebuilding an app-shaped primitive row table. Current Goal2685 local evidence still uses a host-row bridge; native device-column output, pod timing, and external review are required before any zero-copy or performance claim. Primitive-to-group/value mapping, predicate encoding, SQL/RayDB interpretation, and grouped continuation remain outside the native engine. |
| `AABB_INDEX_QUERY_2D` range intersection rows | Internal generic row path | Emit `(query_id, indexed_id)` candidate rows for 2-D AABB intersections from a prepared generic index | Goal2622 added the CPU reference row path; Goal2623 added the generic OptiX native row emitter with explicit fail-closed capacity overflow; Goal2634 added prepared Embree/OptiX row-output reuse for benchmark timing. Exact app refinement remains outside the engine. |
| `EXPANDED_AABB_POINT_MEMBERSHIP_2D` | Candidate behavior | Emit source-offset plus row-major `(source_id, box_id, metadata_flags)` rows for points inside caller-expanded 2-D AABBs | Goal2640 adds the CPU/Embree reference row contract and an app-name-free OptiX native point-contains row symbol scaffold over the existing generic AABB RT traversal. It is intended as a reusable RT-core subroutine for aggregate-frontier-style near/exclusion discovery. The engine sees only points, expanded boxes, ids, row offsets, and fail-closed capacity; box expansion policy and app interpretation remain outside native code. |
| `AGGREGATE_FRONTIER_COLLECT_2D` | Candidate behavior | Emit source-offset plus row-major i64 frontier IDs and reserved `metadata_flags` from a prepared aggregate tree using an app-independent opening predicate | CPU reference, columnar payload adapter, Torch/CuPy partner-column adapter, native ABI contract `generic_aggregate_frontier_collect_2d_native_abi_v1`, local Embree native row collection, and app-name-free OptiX native row collection exist. Goal2639 pod evidence validates same-contract Embree/OptiX parity, fail-closed overflow, and a host-side timing baseline, but this remains row-collection evidence, not RT-core speedup evidence. Current `metadata_flags=0` means no flags set; partners must ignore unknown future non-zero flags until a later contract revision defines them. Default rows are ID-only; optional distance/opening-ratio diagnostics stay outside primitive output. Force laws, scoring, and app reductions remain outside the engine. |
| `COLLECT_K_BOUNDED` | Stable primitive | Bounded row collection with exact fail-closed overflow policy | Promoted by Goal2621 contact-manifold evidence: local Mac Embree parity, RTX A5000 OptiX parity, standalone C++ CPU baseline, and 3-AI promotion consensus. Linux Embree parity has not been separately recorded. |
| bounded witness-row collection | Stable behavior | App-facing witness rows over an app-owned row schema, routed through `COLLECT_K_BOUNDED` when bounded materialization is required | The app may call rows collision/contact witnesses, but the primitive only owns generic candidate-id row collection. |
| witness/candidate row paths | App or partner code unless promoted | App-facing row materialization for a specific workflow | Must not silently truncate exact outputs. |

### Continuation Layer: Segmented Row Streams

These behaviors let RTDL and partner paths process large exact row outputs
without requiring all rows to be materialized as one host table.

| Primitive or operation | Status | Behavior | Boundary |
| --- | --- | --- | --- |
| `SEGMENTED_ROW_STREAM` | Internal substrate | Page a generic row stream into deterministic chunks with opaque continuation tokens | CPU/reference contract in `src/rtdsl/segmented_row_stream.py`; native OptiX/Embree page emission is future evidence work. |
| `CHUNKED_ROW_CONTINUATION` | Alias / compatibility term | Same contract as `SEGMENTED_ROW_STREAM`, emphasizing continuation scheduling | No separate semantics. |

Required contract properties:

- row schema is explicit and app-independent;
- page capacity is explicit and positive;
- continuation tokens are deterministic and stream-local;
- reconstructing a complete stream must exactly recover row order and values;
- incomplete windows are marked with a non-null continuation token;
- exact outputs must fail closed on capacity overflow, with no partial result
  presented as complete.

This primitive does not define graph, DBSCAN, contact, SQL, or other app
semantics. Apps can attach meaning after reconstructing or consuming pages, but
the engine only owns row pagination and completion metadata.

### Candidate / Experimental Layer: Aggregate Frontier And Tree Traversal

These behaviors are candidate areas exposed by Barnes-Hut-style workloads, but
the accepted generic contract is not finished.

| Primitive or operation | Status | Behavior | Boundary |
| --- | --- | --- | --- |
| aggregate-frontier traversal | Candidate behavior | Native/partner lowering target for the `AGGREGATE_FRONTIER_COLLECT_2D` row contract | The generic CPU contract, app-name-free native ABI specification, Embree native row collector, and OptiX native row collector exist. Goal2639 records pod parity and host-side timing evidence; RT-core speedup evidence remains future work. |
| Barnes-Hut inverse-square force accumulation | App or partner code | Workload math over selected points/nodes | Not an RTDL engine primitive. |

Rejected candidate:

```text
generic_aggregate_frontier_inverse_square_scalar_sum_3d_v1
```

Reason: it hardcoded `source_weight * target_or_aggregate_weight / distance^2`.
That is app/workload math, not generic engine behavior.

### App Adapters And Partner Operators

App adapters compose behavior families for one domain. They are allowed to
contain domain vocabulary, but they must not become engine primitives without
promotion.

Examples:

| Adapter or operation | Status | Boundary |
| --- | --- | --- |
| robot pose flags over grouped any-hit rows | App adapter | App adapter over generic any-hit/group-any behavior. |
| Barnes-Hut pairwise inverse-square partner force | App or partner code | App/partner math, not native RTDL engine primitive. |
| RayDB-style query/schema names | App code | App semantics over generic columnar grouped reductions. |

## How Users Select Primitives

Start from the behavior needed, not the benchmark app name.

| User need | Use this behavior family | Candidate primitive path |
| --- | --- | --- |
| I need to know whether anything is hit. | traversal/existence | `ANY_HIT` |
| I need a scalar hit count. | traversal + scalar reduction | `ANY_HIT` + `COUNT_HITS` |
| I need nearby-point counts or threshold flags. | fixed-radius count | `FIXED_RADIUS_COUNT_THRESHOLD_2D` or a prepared fixed-radius variant |
| I need grouped flags, counts, sums, min/max, or stats. | grouped/keyed reductions | `rtdl.grouped_reduction.v1` operation over app-provided group keys |
| I need compact columnar aggregate summaries. | columnar compact summaries | columnar compact summary compatibility path |
| I need candidate rows/witness rows. | collection and row materialization | existing row/witness path if available; otherwise candidate for `COLLECT_K_BOUNDED`-style promotion |
| I need custom force/scoring/math. | app/partner operator | keep math in app/partner code until a regulated operator mechanism exists |
| I need a full domain solver. | app code | compose primitives; RTDL does not own the solver semantics |

Multiple primitives can be composed, but composition does not make a new engine
primitive. For example:

```text
fixed-radius counts -> threshold flags -> grouped union -> component labels
```

is an RT-DBSCAN app pipeline. The low-level fixed-radius/grouped behaviors are
primitive candidates or primitives; DBSCAN cluster semantics remain app code.

## Benchmark-App Primitive Injection History

Benchmark apps did not get a free path to inject native primitives. They
created pressure, and the reusable parts were promoted or recorded as shared
substrates.

| Benchmark app | Pressure injected | Result |
| --- | --- | --- |
| RT-DBSCAN | Fixed-radius graph continuation, grouped union, adjacency and continuation memory pressure | Generic fixed-radius and grouped-continuation pressure; DBSCAN cluster expansion stayed app code. |
| Robot collision | Prepared static scene reuse, grouped finite segment probes, group-any pose flags, count-only result | Generic prepared any-hit/group-any and buffer-reuse pressure; robot pose/link semantics stayed app code. |
| Bounded contact witness / contact-manifold | Exact bounded witness rows, fail-closed overflow, app-owned contact summaries, and prepared AABB broadphase candidate discovery | Promoted `COLLECT_K_BOUNDED` as a stable generic bounded row primitive with row schema `(query_group_id, query_triangle_id, scene_triangle_id)`; Goal2622 added generic `AABB_INDEX_QUERY_2D` broadphase candidate rows, and Goal2634 moved the benchmark row to prepared Embree/OptiX AABB row-output median timing; collision/contact semantics stay in Python app code. |
| RayDB-style | Columnar grouped count/sum/min/max/stats, device column handoff, group capacity; paper-shaped row-as-triangle any-hit grouped reduction; generic RT hit-stream handoff to Triton continuation | `DeviceColumnDescriptor`, `rtdl.grouped_reduction.v1`, candidate `RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D`, and candidate `RAY_TRIANGLE_HIT_STREAM_3D`; SQL/DBMS/RayDB semantics stayed app code. |
| Barnes-Hut | Aggregate frontier traversal and fused force accumulation pressure | Aggregate-frontier primitive remains future work; app-specific inverse-square native primitive was rejected. |

## Primitive Promotion Pipeline

New behavior must pass through these stages.

Promotion path:

```text
app code -> candidate primitive -> experimental primitive -> stable primitive
```

| Stage | Meaning | Allowed claims |
| --- | --- | --- |
| App code | Domain-specific Python, benchmark, or partner logic | App owns behavior; no engine primitive claim. |
| Candidate primitive | A benchmark exposes reusable pressure and a proposed app-independent contract | Design discussion only. |
| Experimental primitive | Contract exists with tests, fail-closed behavior, and bounded evidence, but is not stable | Internal use only; no public/stable claim. |
| Stable primitive | App-independent contract with backend parity/evidence and required review | May be used as supported RTDL primitive within stated boundaries. |
| Rejected candidate | Proposed primitive violates app-independence or safety rules | Must stay app/partner code or be redesigned. |

Promotion requires:

- app-name-free semantics;
- typed input and output schemas;
- deterministic or tolerance policy;
- capacity and overflow policy;
- backend lowering plan;
- tests covering boundaries and failures;
- evidence for at least one supported backend, and parity when required;
- evidence that app semantics remain outside native engines;
- external review for architecture, public wording, or release-impacting
  changes.

## Scheduling And Control Rules

The app does not schedule native primitives directly. It declares primitive
intent and data contracts; RTDL or the partner path chooses the execution
route.

Scheduling inputs:

- primitive kind: traversal, collection, scalar reduction, grouped reduction,
  columnar summary, or prepared-state query;
- backend availability: Embree, OptiX, partner, or CPU reference;
- prepared-state lifetime;
- data residency and descriptor availability;
- output mode: scalar, compact rows, rows/witnesses, grouped rows;
- capacity and overflow policy;
- claim/evidence boundary.

Control rules:

- no silent truncation for exact outputs;
- app-defined math must run in app/partner space unless an operator mechanism
  is reviewed;
- native engine code must not contain app vocabulary or domain-specific
  semantics for supported primitive paths;
- compatibility aliases do not authorize external ABI stability;
- public wording requires separate evidence and consensus.

## Open Organization Work

The catalog shows the current shape, but it also exposes cleanup work:

- rename or supersede compatibility wording such as `DB_COMPACT_SUMMARY` with
  columnar-first public wording;
- decide whether grouped-reduction operations become stable primitives or stay
  an internal substrate;
- design a regulated partner/operator mechanism for app-owned custom math;
- define an app-independent aggregate-frontier primitive before revisiting
  Barnes-Hut-style native traversal;
- keep benchmark apps linked to the primitive pressure they created, without
  letting app semantics enter the engine.
