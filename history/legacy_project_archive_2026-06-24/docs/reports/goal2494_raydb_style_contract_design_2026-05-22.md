# Goal2494: RayDB-Style Contract Design

Date: 2026-05-22

## Status

Goal2494 designs the first RTDL contract for the RayDB-style benchmark-app
campaign. This is a design goal, not an implementation or performance claim.

The contract is intentionally synthetic and app-agnostic. It borrows the
RayDB-shaped pressure discovered in Goal2493 but does not reproduce the RayDB
system and does not put database vocabulary into native engines.

## Existing RTDL Surface

RTDL already has useful database-shaped pieces:

- `src/rtdsl/db_reference.py` defines row-oriented `PredicateClause`,
  `PredicateBundle`, and `GroupedAggregateQuery`.
- `examples/v2_0/features/database/` contains small conjunctive scan, grouped
  count, and grouped sum examples.
- `src/rtdsl/partner_adapters.py` exposes generic partner grouped reductions
  such as count, sum, min, and max by integer key.

These are not enough for the RayDB-style benchmark pressure because they do not
make the columnar prepared-index boundary first-class. The missing layer is a
contract that can describe an already-denormalized table as typed columns,
encode selected columns into geometry axes, and choose a result mode without
embedding app names in the engine.

## Design Rule

Use database terms only in Python benchmark/app code and docs. Native Embree and
OptiX implementation paths must continue to use generic terms such as records,
columns, axes, prepared scenes, rays, hits, groups, and reductions.

The native engine should not know:

- RayDB;
- SQL;
- SSB;
- table names;
- query names;
- database operators;
- Star Schema Benchmark semantics.

## Minimal Contract

The first contract is:

```text
ColumnarRecordSet
+ AxisEncodingPlan
+ PredicateRangeSet
+ GroupSlotMap
+ AggregatePlan
-> PreparedAxisScene
-> GroupedAggregateResult
```

### `ColumnarRecordSet`

App-owned typed columns with equal row count.

Required fields:

- `row_ids`: stable uint32 row IDs;
- `value_columns`: one or more numeric columns used by aggregate plans;
- `group_columns`: one or more integer-coded group key columns;
- `predicate_columns`: one or more integer or float predicate columns;
- `record_count`: common column length.

This is a Python/runtime descriptor. It can be backed by Python lists, NumPy,
CuPy, Torch, or RTDL-owned buffers in future goals.

### `AxisEncodingPlan`

App-owned mapping from selected columns into geometry axes.

First-slice restriction:

- one aggregate/value axis;
- one compact group-slot axis;
- one merged predicate axis.

This matches the first RayDB pressure without making general SQL query planning
an RTDL goal.

### `PredicateRangeSet`

Conjunctive range/equality predicates over predicate columns.

First-slice restrictions:

- only `eq`, `lt`, `le`, `gt`, `ge`, and `between`;
- no disjunction;
- no joins;
- no subqueries;
- no nullable three-valued SQL logic.

### `GroupSlotMap`

Stable mapping from one or more group-key column values to dense integer result
slots.

This is required because grouped RT aggregation needs bounded output slots. It
also makes the no-meaningful-group case explicit instead of silently collapsing
all atomics into one scalar.

### `AggregatePlan`

First-slice result modes:

- `count`;
- `sum`;
- `min`;
- `max`;
- `avg_as_sum_count`.

`avg_as_sum_count` is deliberately expressed as two primitive reductions, not a
magical average operator.

### `PreparedAxisScene`

Prepared generic geometry/index state over encoded records.

First-slice semantics:

- records are encoded as generic primitives;
- the prepared scene can be reused across repeated predicate queries;
- build time is reported separately from query time;
- app code owns the mapping from original table values to encoded coordinates.

### `GroupedAggregateResult`

Output is compact, bounded, and non-row-materializing by default:

- `group_slots`;
- aggregate vectors;
- optional hit count or duplicate-hit metadata;
- optional group-key decode table owned by Python.

Materialized row output is out of scope for the first RayDB-style slice.

## CPU Reference Contract

Goal2495 should implement the CPU reference over this same logical contract:

1. Normalize column lengths and row IDs.
2. Evaluate predicate clauses directly over the columnar input.
3. Build `GroupSlotMap`.
4. Produce grouped count/sum/min/max and `avg_as_sum_count`.
5. Emit JSON with the contract metadata and claim boundary.

The CPU reference is the oracle. It does not need RT acceleration.

## Embree And OptiX Contract

Embree and OptiX should only receive generic encoded geometry/query descriptors.
They should not receive database names or query names.

Implementation choices are deferred:

- Embree may use an existing prepared ray/triangle path or a new generic
  encoded-axis helper if required.
- OptiX should reuse existing prepared-scene and grouped reduction patterns
  where possible.
- If the first backend implementation cannot support grouped `sum/min/max`
  natively, it may return generic hit/group columns and let Python or a partner
  perform the aggregate as an explicitly named continuation.

## Known Failure Modes To Track

The RayDB intake and earlier reports identify these risks:

- no-group or single-group aggregation can collapse into one hot atomic slot;
- too many groups can also fragment output and reduce locality;
- duplicate primitive hits require explicit deduplication policy;
- full row materialization can dominate traversal;
- online BVH rebuilds can erase RT traversal benefit;
- old authors-code toolchains are not a stable baseline for RTDL development.

These are design constraints, not blockers.

## Chosen Goal2495 Starting Point

Goal2495 should implement only the CPU reference and fixture:

- a tiny denormalized table with integer-coded fields;
- two queries: one grouped count and one grouped sum;
- optional min/max if low-risk;
- JSON output with `all_match_cpu_reference: true` for self-checks;
- no Embree, OptiX, or authors-code timing.

This gives us a concrete app-shaped surface before touching native code.

## Non-Claims

Goal2494 does not claim:

- a stable public API;
- RayDB reproduction;
- authors-code comparison;
- SQL engine support;
- DBMS behavior;
- row materialization support;
- Embree or OptiX performance;
- native database-specific ABI.

## Exit Criteria

Goal2494 is complete when:

- this report defines the minimal contract;
- tests lock the app-agnostic native boundary and the Goal2495 starting point;
- no code is added to native engines;
- Goal2495 has a clear CPU-reference implementation target.
