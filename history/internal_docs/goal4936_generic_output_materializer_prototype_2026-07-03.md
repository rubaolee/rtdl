# Goal4936: Generic Output Materializer Prototype

Date: 2026-07-03

Exit label: `generic_materializer_beats_python_loop`

## Purpose

Goal4936 prototypes a generic output materializer that consumes the neutral Layer 1 row-buffer/data-shape contract from Goal4935.

This goal deliberately does not write RayJoin output-chain text. It materializes:

- one descriptor row per group;
- ordered item payload columns;
- group offsets and lengths.

Final app-specific serialization remains app-owned.

## Code Changes

Generic core module:

- `src/rtdsl/output_assembly.py`

New API:

- `GroupedOutputMaterializationResult`
- `materialize_grouped_output_row_buffer`

Public exports:

- `src/rtdsl/__init__.py`

Focused tests:

- `tests/goal4936_output_materializer_test.py`

## Contract

Input:

- `GroupedOutputRowBuffer`, produced by `prepare_grouped_output_row_buffer`.

Output:

```text
GroupedOutputMaterializationResult
  group_keys
  descriptor_columns
  group_offsets
  group_lengths
  item_columns
  stats
```

The materializer is format-neutral. It does not produce strings or files.

## Why This Is Generic

The materializer only understands:

- group keys;
- descriptor columns;
- ordered item payload columns;
- offsets and lengths.

It does not understand:

- RayJoin;
- overlay;
- Section 5.7;
- author output-chain headers;
- polygon or face id semantics;
- any text output format.

The focused test checks that `src/rtdsl/output_assembly.py` still contains none of:

- `rayjoin`
- `overlay`
- `section57`
- `author`

## Correctness Evidence

Tests cover:

1. public API export;
2. generic descriptor and item materialization;
3. non-RayJoin radius-neighbor materialization;
4. synthetic-scale materializer vs Python reference;
5. app-identity string rejection in core source;
6. previous Goal4935 row-buffer tests;
7. previous Goal4932 grouped assembly tests.

Command:

```text
PYTHONPATH=src py -m unittest \
  tests.goal4936_output_materializer_test \
  tests.goal4935_output_row_buffer_contract_test \
  tests.goal4932_generic_output_assembly_test
```

Result:

- 19 tests passed.

Compile check:

```text
py -m py_compile src/rtdsl/output_assembly.py tests/goal4936_output_materializer_test.py
```

Result:

- passed.

## Synthetic Performance Evidence

Synthetic benchmark:

- rows: `160000`
- groups: `20000`
- items per group: `8`
- shape: neutral descriptor/item row-buffer
- comparison: generic materializer vs equivalent Python row loop

Result:

```json
{
  "materializer_sec": 0.03936809999868274,
  "python_reference_sec": 0.5579695999622345,
  "speedup_vs_python_reference": 14.173140181540493,
  "row_count": 160000,
  "group_count": 20000,
  "items_per_group": 8
}
```

Interpretation:

The materializer beats the Python row loop on synthetic neutral row-buffer data.

This is a prototype proof that the Layer 1 shape can support a faster generic materialization step.

## Claim Boundary

Authorized:

- A generic host-columnar materializer exists.
- It consumes `GroupedOutputRowBuffer`.
- It materializes descriptor/item columns faster than an equivalent Python loop on synthetic data.
- It is not RayJoin-specific in core.

Not authorized:

- No RayJoin public-sample speedup claim.
- No Section 5.7 speedup claim.
- No author-program performance comparison.
- No compiled/native writer claim.
- No device-resident row-buffer claim.
- No V3/V4 claim.

## Next Step

The correct next goal is:

**Goal4937: RayJoin Public-Sample Materializer Wiring**

Goal4937 should wire the materializer into the RayJoin Section 5.7 public-sample app path and test whether it preserves byte equality and improves the real writer phase.

Goal4937 must compare against:

- Goal4933 plain writer: `2.069s`;
- Goal4933 generic-wired writer: `2.982s`;
- new materializer-wired writer.

Minimum continuation condition:

- byte-equal correctness;
- repeated writer time strictly below `2.069s`.

Target:

- `output_chain_write_sec <= 1.65s`.
