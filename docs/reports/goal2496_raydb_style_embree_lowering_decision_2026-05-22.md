# Goal2496: RayDB-Style Embree Lowering Decision

Date: 2026-05-22

## Status

Goal2496 decides the first backend direction for the RayDB-style benchmark
after the CPU reference in Goal2495.

Decision: do not add new native DB/RayDB ABI. The next backend step should
lower the generic `ColumnarRecordSet` / `ColumnarAggregatePlan` contract through
the existing Embree columnar payload capability where available, while treating
older Python DB-named wrappers as compatibility surfaces.

## What Exists Already

Embree runtime already requires these native symbols:

- `rtdl_embree_columnar_payload_create`
- `rtdl_embree_columnar_payload_create_from_columns`
- `rtdl_embree_columnar_payload_destroy`
- `rtdl_embree_columnar_payload_multi_predicate_scan`
- `rtdl_embree_columnar_payload_grouped_reduction_count`
- `rtdl_embree_columnar_payload_grouped_reduction_sum`

This is close to the desired app-agnostic shape: columnar payload, predicates,
grouped reductions. It is not RayDB-specific.

The current Python compatibility layer still exposes older names such as:

- `prepare_embree_db_dataset`
- `PreparedEmbreeDbDataset`
- `grouped_count`
- `grouped_sum`

Those names are acceptable as historical compatibility wrappers, but new
RayDB-style work should not expand them or add new database-specific native ABI.

## Lowering Choice

The first backend lowering target should be:

```text
ColumnarRecordSet + ColumnarAggregatePlan
-> generic Embree columnar payload descriptor
-> grouped count/sum result
-> compare with Goal2495 CPU oracle
```

First backend result modes:

- `count`
- `sum`

Deferred backend result modes:

- `min`
- `max`
- `avg_as_sum_count`

Reason: the existing Embree native columnar payload exports count and sum. Min,
max, and average-as-sum/count should wait until we either add generic reduction
modes or explicitly route them through a partner/Python continuation.

## Boundary

Goal2496 should not:

- add native `raydb`, `sql`, `database`, `table`, `ssb`, or query-name symbols;
- add a new RayDB native API;
- claim RayDB reproduction;
- time authors code;
- require a pod;
- claim public speedup.

Goal2496 may add:

- a Python adapter that converts `ColumnarRecordSet` into the already-supported
  Embree columnar payload format;
- a skip-if-unavailable test for local Embree native library availability;
- a report showing CPU oracle parity when Embree is present.

## Why This Matters

This goal is exactly the app-driven reconstruction rule in practice. RayDB-style
work is not forcing a new DBMS layer. It is forcing a cleaner generic columnar
payload lowering boundary:

- app owns query/schema names;
- Python/runtime owns typed column descriptors;
- Embree owns generic columnar predicate and grouped reduction execution;
- native code remains app-name-free for new work.

## Next Implementation Target

Goal2497 should implement the Python adapter and local Embree parity test:

- convert Goal2495 fixture columns into row dictionaries only if required by the
  current compatibility wrapper;
- prefer direct columnar handoff if the existing runtime exposes one cleanly;
- compare Embree count/sum rows against `evaluate_columnar_grouped_aggregate`;
- skip cleanly when `librtdl_embree` is unavailable;
- record that min/max/avg are still CPU-only until generic reductions expand.
