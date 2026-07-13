# Goal4939 Grouped Path-Split Row-Buffer Prototype

Date: 2026-07-03

## Verdict

`generic_path_split_prototype_ready_for_rayjoin_adapter_gate`

Goal4939 implemented the generic path-split row-buffer prototype authorized by Goal4938. It does not wire into RayJoin yet. It first proves that RTDL can express the earlier boundary as a neutral columnar continuation:

```text
base path chains + ordered split events + app-supplied interval descriptors
  -> grouped descriptor/item row buffer
  -> existing grouped output materializer
```

## Files Changed

- `src/rtdsl/output_assembly.py`
- `src/rtdsl/__init__.py`
- `tests/goal4939_grouped_path_split_records_test.py`

## New API

```python
assemble_grouped_path_split_records(
    *,
    chain_ids,
    chain_point_offsets,
    chain_point_counts,
    point_x,
    point_y,
    split_chain_ids=None,
    split_edge_orders=None,
    split_event_orders=None,
    split_x=None,
    split_y=None,
    interval_descriptor_columns=None,
    interval_validity=None,
    output_group_ids=None,
    dedupe_consecutive_points=True,
) -> GroupedOutputRowBuffer
```

The function returns the existing `GroupedOutputRowBuffer`, so it composes with:

- `assemble_grouped_output_row_buffer`
- `materialize_grouped_output_row_buffer`

## What It Does

For each chain:

1. Walk the base points in order.
2. Insert split events by `(edge_order, event_order)`.
3. Emit one grouped record per interval between split boundaries.
4. Repeat app-supplied descriptor columns over the item rows in that interval.
5. Return neutral row-buffer columns:
   - `group_id`
   - `item_order`
   - descriptor columns supplied by the caller
   - item payload columns `x`, `y`

The caller owns semantic labels and final formatting.

## What It Does Not Do

The prototype does not:

- know RayJoin;
- know polygon overlay;
- compute keep/drop policy;
- compute midpoint faces;
- write author text;
- use map0/map1 concepts;
- change native RT traversal;
- claim RayJoin performance.

## Generic Proof

The first test fixture is a non-app path segmentation workload:

```text
path: (0,0) -> (10,0) -> (20,0)
events: (5,0), (12,0), (18,0)
output intervals:
  [(0,0), (5,0)]
  [(5,0), (10,0), (12,0)]
  [(12,0), (18,0)]
  [(18,0), (20,0)]
```

This proves the shape is not tied to RayJoin output.

The second shape test uses two labeled planar chains with descriptor columns, but still uses only neutral terms such as `left_label` and `right_label`.

## Guardrails

The tests assert that `src/rtdsl/output_assembly.py` contains none of these app-identity tokens:

- `rayjoin`
- `overlay`
- `section57`
- `author`
- `map0`
- `map1`

The implementation also rejects:

- object dtype descriptor columns,
- wrong descriptor interval counts,
- duplicate chain ids,
- split events that reference unknown chain ids.

## Verification

Commands:

```text
PYTHONPATH=src py -m unittest tests.goal4939_grouped_path_split_records_test tests.goal4932_generic_output_assembly_test tests.goal4935_output_row_buffer_contract_test tests.goal4936_output_materializer_test
PYTHONPATH=src py -m py_compile src/rtdsl/output_assembly.py src/rtdsl/__init__.py tests/goal4939_grouped_path_split_records_test.py
```

Result:

```text
Ran 26 tests in 1.568s
OK
```

## Why This Matters

Goal4937 proved that attaching the generic materializer after RayJoin has already built chain structures is too late. Goal4939 creates the earlier generic boundary that Goal4938 required.

This is still only a host-columnar prototype. It proves shape and correctness on synthetic fixtures. It does not prove RayJoin speedup yet.

## Next Goal

Goal4940 should wire this path-split row-buffer into the RayJoin Section 5.7 public sample as an app adapter.

Required gates:

1. Do not put RayJoin terms in RTDL core.
2. Preserve byte equality first.
3. Compare same-run writer time against the existing plain writer.
4. Pass only if the path-split route removes the old Python chain loop before generic materialization.
5. Stop if it is byte-equal but not faster.

## Exit Label

`generic_path_split_prototype_ready_for_rayjoin_adapter_gate`
