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

## Current Primitive Layers

RTDL currently has five layers. They should not be collapsed into one flat
list.

### Layer 1: Stable Core Execution Primitives

These are the current stable generic execution primitive tokens recorded in
`src/rtdsl/v1_5_migration_inventory.py`.

| Primitive | Behavior | Main use |
| --- | --- | --- |
| `ANY_HIT` | Existence of a hit between query geometry and prepared/build geometry | visibility, robot screening, ray/segment screening |
| `FIXED_RADIUS_COUNT_THRESHOLD_2D` | Count nearby points within a radius, optionally threshold-capped | density, coverage, hotspot/core predicates |
| `DB_COMPACT_SUMMARY` | Compatibility token for generic columnar compact summary | columnar predicate plus count/sum summaries |
| `POLYGON_PAIR_EXACT_AREA_SUMMARY` | Candidate discovery plus exact pair-area summary | polygon overlap and Jaccard-style summaries |

Naming note: `DB_COMPACT_SUMMARY` remains a compatibility token. The preferred
conceptual name is columnar compact summary.

### Layer 2: Stable Scalar Reduction Primitives

These are summary operations over primitive rows or hit streams.

| Primitive | Behavior |
| --- | --- |
| `COUNT_HITS` | Count positive hit rows. |
| `REDUCE_FLOAT(MIN)` | Floating minimum reduction. |
| `REDUCE_FLOAT(MAX)` | Floating maximum reduction. |
| `REDUCE_FLOAT(SUM)` | Floating sum reduction with tolerance policy. |
| `REDUCE_INT(COUNT)` | Integer count reduction. |
| `REDUCE_INT(SUM)` | Integer sum reduction. |

### Layer 3: Experimental Collection Primitive

| Primitive | Status | Boundary |
| --- | --- | --- |
| `COLLECT_K_BOUNDED` | Experimental | Requires fail-closed overflow, native Embree/OptiX parity, benchmarks, and external review before stable promotion. |

### Layer 4: Shared Grouped-Reduction Substrate

These operations are recorded in `src/rtdsl/grouped_reduction.py` as
`rtdl.grouped_reduction.v1`.

| Operation | Behavior |
| --- | --- |
| `group_any` | Per-group boolean existence. |
| `group_count` | Per-group row/count aggregation. |
| `group_sum_i64` | Per-group signed integer sum. |
| `group_sum_f64` | Per-group floating sum. |
| `group_min_i64` | Per-group signed integer minimum. |
| `group_max_i64` | Per-group signed integer maximum. |
| `group_sum_count_i64` | Fused per-group sum and count. |
| `group_stats_i64` | Fused per-group count, sum, min, and max. |

Status: internal shared substrate. Backend support and performance claims are
separate from the contract. Full native migration is still future work.

### Layer 5: App Adapters And Partner Operators

App adapters compose primitives and partner operations for one domain. They are
allowed to contain domain vocabulary, but they must not become engine
primitives without promotion.

Examples:

| Adapter or operation | Owner | Boundary |
| --- | --- | --- |
| robot pose flags over grouped any-hit rows | `rtdsl.app_adapters.robot_collision` | App adapter over generic any-hit/group-any behavior. |
| Barnes-Hut pairwise inverse-square partner force | `rtdsl.app_adapters.barnes_hut` | App/partner math, not native RTDL engine primitive. |
| RayDB-style query/schema names | benchmark app | App semantics over generic columnar grouped reductions. |

## How Users Select Primitives

Start from the behavior needed, not the benchmark app name.

| User need | Use this layer | Candidate primitive path |
| --- | --- | --- |
| I need to know whether anything is hit. | traversal/existence | `ANY_HIT` |
| I need a scalar hit count. | traversal + scalar reduction | `ANY_HIT` + `COUNT_HITS` |
| I need nearby-point counts or threshold flags. | fixed-radius count | `FIXED_RADIUS_COUNT_THRESHOLD_2D` or a prepared fixed-radius variant |
| I need grouped flags, counts, sums, min/max, or stats. | grouped reduction | `rtdl.grouped_reduction.v1` operation over app-provided group keys |
| I need compact columnar aggregate summaries. | columnar compact summary | columnar compact summary compatibility path |
| I need candidate rows/witness rows. | collection | existing row/witness path if available; otherwise candidate for `COLLECT_K_BOUNDED`-style promotion |
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

Rejected candidate:

```text
generic_aggregate_frontier_inverse_square_scalar_sum_3d_v1
```

Reason: it hardcoded `source_weight * target_or_aggregate_weight / distance^2`.
That is app/workload math, not generic engine behavior.

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
