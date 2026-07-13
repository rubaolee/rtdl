# Goal4931: Generic Output-Assembly Layer Design

Date: 2026-07-03

Status: design-only goal; no implementation authorized by this document.

## Purpose

Goal4930 measured the v2.14.2 RayJoin Section 5.7 hot path and found that the
remaining writer cost is dominated by structural output-chain assembly, not by
final text/file writing:

```text
measured structural assembly subtotal: ~2.001 s
bulk text/file write subtotal:         ~0.064 s
```

Goal4931 designs the next generic layer before implementation. The design must
avoid the mistake of hiding RayJoin output rules in RTDL core. RTDL may provide
compiled/generic structure assembly. The application owns the final paper-format
or product-format bytes.

## Non-Authorization

Goal4931 does not authorize:

- implementation of a compiled writer;
- implementation of a device-resident row-buffer pipeline;
- changes under `src/native/**` or `src/rtdsl/**`;
- RayJoin-specific text/topology formatting in RTDL core;
- a v2.14.2 release claim;
- performance claims beyond citing Goal4930 measurements.

## Design Principle

RTDL should assemble generic grouped structures from typed rows:

```text
typed rows -> generic grouped/chained structure -> app-owned final formatting
```

It must not know that the final consumer is RayJoin. It may know generic ideas:

- grouping keys;
- stable ordering keys;
- payload columns;
- record validity masks;
- group offsets;
- sequence descriptors;
- optional per-group reductions;
- compact binary/columnar output.

It must not know app identities:

- RayJoin;
- polygon overlay;
- author output-chain text format;
- map0/map1 paper-output line rules;
- paper-specific topology byte layout.

## Proposed Public Concept

### `GroupedSequenceAssemblyPlan`

A declarative plan for turning typed rows into grouped, ordered sequences.

Required fields:

| Field | Meaning |
| --- | --- |
| `group_key_columns` | One or more integer/string-like key columns that identify an output group. |
| `order_key_columns` | Stable sort keys inside each group. |
| `payload_columns` | Columns to carry into the output sequence. |
| `validity_column` | Optional boolean/integer mask column; invalid rows are skipped. |
| `dedupe_key_columns` | Optional columns used to collapse duplicate payload records. |
| `group_policy` | `preserve_empty`, `skip_empty`, or `emit_empty_descriptor`. |
| `output_shape` | `offsets_and_items`, `descriptors_and_items`, or `columnar_records`. |

This is generic. A spatial join could group by `left_id`; kNN could group by
`query_id`; RayJoin can group by output-chain id in the app layer.

### `GroupedSequenceAssemblyResult`

A compact output structure:

| Field | Meaning |
| --- | --- |
| `group_ids` | Group identifiers in output order. |
| `group_offsets` | Prefix-sum offsets into the item arrays. |
| `group_lengths` | Item count per group. |
| `item_columns` | Columnar payload arrays after validity, ordering, and optional dedupe. |
| `descriptor_flags` | Optional generic flags such as `empty`, `single_record`, `direct_descriptor`. |
| `stats` | Assembly timing, skipped rows, emitted rows, groups, bytes. |

The result is not a text writer. It is a reusable structural representation that
apps can serialize however they need.

## RayJoin Mapping Without Core App Identity

RayJoin Section 5.7 can use this design as follows:

```text
RTDL public LSI/PIP rows
  -> RayJoin app computes app-owned chain ids and payload fields
  -> GroupedSequenceAssemblyPlan(
       group_key_columns=["chain_id"],
       order_key_columns=["segment_order", "point_order"],
       payload_columns=["point_id", "x", "y", "face0", "face1"],
       validity_column="emit",
       output_shape="descriptors_and_items"
     )
  -> GroupedSequenceAssemblyResult
  -> RayJoin app adapter writes exact AuthorOfficial text/topology bytes
```

Allowed in RTDL core:

- grouping the rows by `chain_id` as a generic key;
- sorting within each group by supplied ordering keys;
- producing offsets/items/descriptors.

Forbidden in RTDL core:

- deciding RayJoin polygon-overlay semantics;
- writing the exact author output-chain byte format;
- naming the API after RayJoin or Section 5.7;
- embedding `map0`/`map1` author-format text rules in the generic assembler.

## Why This Is Not Just a RayJoin Helper

The same primitive must also serve at least one non-RayJoin consumer before
productization. Candidate proof workloads:

1. **Spatial join grouped pairs**
   - Input rows: `{left_id, right_id, hit_flag}`.
   - Group by: `left_id`.
   - Payload: `right_id`.
   - Output: grouped candidate list per left object.

2. **kNN / nearest-witness result groups**
   - Input rows: `{query_id, candidate_id, distance}`.
   - Group by: `query_id`.
   - Order by: `distance`.
   - Payload: `{candidate_id, distance}`.

3. **Component-style grouped reductions**
   - Input rows: `{component_id, item_id, value}`.
   - Group by: `component_id`.
   - Payload: `{item_id, value}`.

RayJoin can be the exam workload, but it cannot be the only proof that the
layer is generic.

## Implementation Shape For A Future Goal

Goal4931 intentionally does not implement this. A future implementation goal
should choose the smallest staged route:

### Stage A: Host-columnar prototype

- Input: NumPy arrays or buffer views already produced by current RTDL app code.
- Compute: Numba or native compiled grouping/order assembly.
- Output: `GroupedSequenceAssemblyResult`.
- Purpose: prove the API and remove Python per-chain loops without changing
  native RTDL traversal.

This is the least risky first implementation. It targets Goal4930's structural
assembly bottleneck without pretending to be device-resident yet.

### Stage B: Row-buffer compatible ABI

- Same logical plan/result as Stage A.
- Input columns can be backed by RTDL row buffers.
- Ownership/lifetime are explicit.
- No Python object materialization between stages.

This becomes the bridge to Layer 1.

### Stage C: Device-resident assembly

- Same API contract.
- Columns remain resident; assembly runs on device or native compiled memory.
- App adapter receives compact structure, not millions of Python records.

This is a later v2.14.2 performance step and must be separately reviewed.

## Correctness Contract

Any implementation of this design must preserve:

- deterministic group order;
- deterministic row order within a group;
- explicit tie-breaking for equal order keys;
- exact row counts before/after validity and dedupe;
- byte-equality of the RayJoin app adapter output when used for RayJoin;
- equality of grouped-pair outputs for a non-RayJoin app.

No performance result counts unless correctness passes first.

## Performance Target For A Future Implementation Goal

Goal4930 measured structural assembly at about `2.001 s`.

A future implementation goal may use these bounded targets:

| Target | Meaning |
| --- | --- |
| Minimum useful target | structural assembly improves by at least `1.25x` with byte equality. |
| Strong target | structural assembly improves by at least `2.0x`. |
| Hot-body target | total RayJoin hot body improves over Goal4930 by at least `10%`. |

These targets are intentionally bounded to the measured assembly layer. They do
not imply broad RayJoin, RTDL, or paper-reproduction speedup claims.

## Exit Gate For Goal4931

Goal4931 is complete when it has:

1. a generic plan/result interface;
2. a clear RayJoin mapping that keeps final formatting app-owned;
3. red-line checks blocking RayJoin identity in RTDL core;
4. at least one required non-RayJoin proof workload for future implementation;
5. future implementation stages ordered from low-risk host-columnar prototype to
   row-buffer/device-resident versions;
6. explicit correctness and performance gates.

## Recommended Next Goal If Approved

If this design is approved, the next goal should be:

**Goal4932: Host-Columnar Generic Grouped-Sequence Assembly Prototype**

Scope:

- implement the Stage A host-columnar prototype only;
- no native RTDL traversal changes;
- no RayJoin text formatting in RTDL core;
- wire RayJoin Section 5.7 through the generic assembler only at the app layer;
- prove one non-RayJoin grouped-output consumer;
- measure structural assembly before/after;
- preserve byte equality.
