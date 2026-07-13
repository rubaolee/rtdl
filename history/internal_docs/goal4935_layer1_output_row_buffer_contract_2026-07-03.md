# Goal4935: Layer 1 Output Row-Buffer/Data-Shape Contract

Date: 2026-07-03

Exit label: `layer1_shape_contract_ready`

## Purpose

Goal4935 defines the neutral row-buffer/data-shape contract required before any generic output materializer work.

Goal4934 concluded that a compiled writer would be premature because the current RayJoin Section 5.7 path still feeds generic assembly with Python strings, Python lists, dictionaries, and author-specific output-chain state.

Goal4935 therefore creates a minimal Layer 1 host-columnar contract:

- generic column roles;
- primitive column validation;
- descriptor/item split;
- validity mask support;
- optional dedupe key support;
- deterministic handoff to existing grouped assembly.

This goal does **not** implement a compiled writer, native writer, or device-resident row-buffer.

## Code Changes

Core generic module:

- `src/rtdsl/output_assembly.py`

New public types/functions:

- `GroupedOutputRowBufferSchema`
- `GroupedOutputRowBuffer`
- `prepare_grouped_output_row_buffer`
- `assemble_grouped_output_row_buffer`

Public exports:

- `src/rtdsl/__init__.py`

Focused tests:

- `tests/goal4935_output_row_buffer_contract_test.py`

## Contract

The new contract is:

```text
GroupedOutputRowBufferSchema
  group_key_columns
  item_order_columns
  group_descriptor_columns
  item_payload_columns
  validity_column
  dedupe_key_columns
```

An application maps its domain data into these neutral roles.

RTDL core may validate and assemble:

- group keys;
- item order keys;
- descriptor columns;
- item payload columns;
- validity masks;
- optional dedupe keys.

RTDL core may not know:

- RayJoin;
- overlay;
- Section 5.7;
- author output-chain headers;
- polygon/face id semantics;
- app-specific text formatting.

## Validation Rules

`prepare_grouped_output_row_buffer` enforces:

1. all columns are one-dimensional;
2. all columns have equal length;
3. all required schema columns exist;
4. object dtype columns are rejected;
5. schema role names are unique;
6. descriptor columns must be invariant within a group unless validation is explicitly disabled;
7. the schema marker must be `rtdl.grouped_output_row_buffer.v1`.

The object-dtype rejection is important. It prevents the exact failure mode exposed in Goal4933: feeding Python strings/lists into a supposedly generic materializer.

## Why This Is Generic

The core module contains no app identity terms. The focused test checks that `src/rtdsl/output_assembly.py` does not contain:

- `rayjoin`
- `overlay`
- `section57`
- `author`

The contract is intentionally shaped around database/array roles:

- groups;
- descriptors;
- ordered items;
- payload columns;
- validity masks.

Those roles are useful for RayJoin-style output, but also for non-RayJoin grouped results such as radius-neighbor or spatial-join outputs.

## RayJoin Adapter Proof

The test `test_rayjoin_style_adapter_can_map_to_neutral_columns` demonstrates that a RayJoin-like app can map its output state into neutral columns:

- `group_id`
- `item_order`
- `first_item_id`
- `last_item_id`
- `left_region_id`
- `right_region_id`
- `item_id`
- `x`
- `y`

These names are deliberately generic. They represent the app adapter's chosen columns, not RTDL core semantics.

The proof is limited:

- It does not wire the full public sample.
- It does not claim speedup.
- It only proves a shape contract can carry the needed descriptor/item structure without Python text.

## Non-RayJoin Proof

The test `test_non_rayjoin_radius_neighbor_output_uses_same_shape` uses the same contract for a radius-neighbor style grouped output:

- `query_id`
- `rank`
- `query_result_count`
- `neighbor_id`
- `distance`
- `emit`

This proves the contract is not only useful for RayJoin-style output.

## Test Evidence

Commands run:

```text
py -m py_compile src/rtdsl/output_assembly.py tests/goal4935_output_row_buffer_contract_test.py
PYTHONPATH=src py -m unittest tests.goal4935_output_row_buffer_contract_test tests.goal4932_generic_output_assembly_test
```

Result:

- 14 tests passed.

## What This Enables

Goal4935 enables Goal4936 to prototype a generic materializer against a stable, neutral input shape.

Goal4936 must consume this contract, not Python object/list/string state.

## What This Does Not Authorize

Goal4935 does not authorize:

- compiled output writer implementation;
- native writer implementation;
- device-resident row-buffer implementation;
- RayJoin-specific writer in RTDL core;
- public performance claim;
- V3/V4 claim;
- Section 5.7 speedup claim.

## Completion Judgment

Goal4935 should close with:

`layer1_shape_contract_ready`

The next goal may be Goal4936, a generic materializer prototype, but only if it consumes `GroupedOutputRowBuffer`/`GroupedOutputRowBufferSchema` or a strictly compatible neutral shape.
