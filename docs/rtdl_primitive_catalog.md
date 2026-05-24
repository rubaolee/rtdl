# RTDL Primitive Catalog And Promotion Rules

Date: 2026-05-23

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

## Behavior-First Primitive Taxonomy

The top-level organization is behavior. Stability, maturity, backend coverage,
and implementation owner are metadata on a behavior family; they are not the
primary taxonomy. A user should first ask "what runtime behavior do I need?",
then check whether that behavior is stable, experimental, internal substrate,
candidate, or app-owned.

Status metadata used below:

| Status | Meaning |
| --- | --- |
| Stable primitive | RTDL owns the app-independent behavior under stated backend and evidence boundaries. |
| Experimental primitive | A contract exists, but promotion requires additional parity, safety, benchmark, or review gates. |
| Internal substrate | Shared implementation contract used by RTDL paths, but not yet an externally stable primitive. |
| Candidate behavior | Reusable pressure exists, but the primitive contract is not accepted yet. |
| App or partner code | Domain semantics, custom math, or partner-specific implementation that RTDL does not own as a primitive. |
| Rejected candidate | A proposed primitive violated app-independence or safety rules and must stay out of the engine. |

### Hit And Traversal Predicates

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

### Spatial Neighborhood Predicates

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

### Scalar Reductions

These behaviors reduce a stream of primitive outputs to scalar summaries.

| Primitive or operation | Status | Behavior |
| --- | --- | --- |
| `COUNT_HITS` | Stable primitive | Count positive hit rows. |
| `REDUCE_FLOAT(MIN)` | Stable primitive | Floating minimum reduction. |
| `REDUCE_FLOAT(MAX)` | Stable primitive | Floating maximum reduction. |
| `REDUCE_FLOAT(SUM)` | Stable primitive | Floating sum reduction with tolerance policy. |
| `REDUCE_INT(COUNT)` | Stable primitive | Integer count reduction. |
| `REDUCE_INT(SUM)` | Stable primitive | Integer sum reduction. |

### Grouped And Keyed Reductions

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

Grouped-reduction operations are reusable behavior, but backend support and
external stability are separate decisions. Do not call them stable external
primitives until promotion explicitly says so.

### Columnar Compact Summaries

These behaviors produce compact columnar aggregate summaries without claiming
SQL or DBMS semantics.

| Primitive or operation | Status | Behavior | Naming boundary |
| --- | --- | --- | --- |
| columnar compact summary | Stable compatibility path | Conjunctive scan count, grouped integer count, and grouped integer sum over app-owned columnar/denormalized input | `DB_COMPACT_SUMMARY` is a legacy compatibility token; columnar compact summary is the preferred conceptual name. |

This behavior is not SQL, a DBMS, a query planner, joins, indexes,
transactions, or row-output materialization.

### Collection And Row Materialization

These behaviors return bounded rows or witness/candidate rows rather than only
compact summaries.

| Primitive or operation | Status | Behavior | Boundary |
| --- | --- | --- | --- |
| `COLLECT_K_BOUNDED` | Experimental primitive | Bounded row collection with exact fail-closed overflow policy | Requires native Embree/OptiX parity, benchmarks, and external review before stable promotion. |
| witness/candidate row paths | App or partner code unless promoted | App-facing row materialization for a specific workflow | Must not silently truncate exact outputs. |

### Aggregate Frontier And Tree Traversal

These behaviors are candidate areas exposed by Barnes-Hut-style workloads, but
the accepted generic contract is not finished.

| Primitive or operation | Status | Behavior | Boundary |
| --- | --- | --- | --- |
| aggregate-frontier traversal | Candidate behavior | Select aggregate/tree nodes according to an app-independent opening predicate and emit a bounded frontier or summary input | Needs a generic contract before native promotion. |
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
| RayDB-style | Columnar grouped count/sum/min/max/stats, device column handoff, group capacity | `DeviceColumnDescriptor` and `rtdl.grouped_reduction.v1`; SQL/DBMS semantics stayed app code. |
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
