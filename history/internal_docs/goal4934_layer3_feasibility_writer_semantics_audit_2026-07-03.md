# Goal4934: Layer 3 Feasibility And Writer Semantics Audit

Date: 2026-07-03

Exit label: `needs_layer1_shape_before_decision`

## Purpose

Goal4934 decides whether the remaining RayJoin Section 5.7 writer bottleneck is ready for a generic compiled output backend, or whether the work is still entangled with app-specific author/RayJoin semantics.

This goal does not implement runtime code. It is a gate before any compiled/vectorized writer work.

## Inputs Inspected

Primary source:

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_numba.py`

Relevant evidence:

- `history/internal_docs/goal4933_rayjoin_public_sample_generic_assembly_pod_smoke_2026-07-03.md`
- `history/internal_docs/goal4933_pod_artifacts/section57_overlay_numba.json`
- `src/rtdsl/output_assembly.py`
- `tests/goal4932_generic_output_assembly_test.py`

Worktree state before the audit:

- `git status --short` was clean.

## Current Measured Fact

Goal4933 proved the first generic output assembly layer is correct but not faster:

| Route | `output_chain_write_sec` | Correctness |
|---|---:|---|
| Plain Section 5.7 writer | `2.069s` | byte-equal |
| Generic-wired writer | `2.982s` | byte-equal |

The generic-wired writer breakdown was:

| Phase | Seconds |
|---|---:|
| `generic_output_assembly_sec` | `0.331` |
| `chain_loop_map0_sec` | `1.266` |
| `chain_loop_map1_sec` | `1.046` |
| `skip_plan_sec` | `0.066` |
| `group_xsects_map0_sec` | `0.007` |
| `group_xsects_map1_sec` | `0.079` |
| `bulk_writelines_sec` | `0.074` |

Interpretation:

The generic grouping layer is on path, but the expensive work remains in Python chain loops and author-compatible line materialization.

## Writer Operation Classification

The table below classifies the current `write_output_chains_streaming_numba_skip` path. Categories are deliberately strict:

- **Generic**: can honestly belong in RTDL core.
- **Generic if supplied as columns**: can belong in core only after the app has already produced neutral columnar inputs.
- **App-specific**: belongs in the RayJoin paper-reproduction app, not RTDL core.
- **File IO**: ordinary output side effect, not a performance architecture feature.

| Code region | Operation | Classification | Reason |
|---|---|---|---|
| lines 78-98 | `_writer_skip_plan`: compute chain has-intersections, terminal keep, skip mask | Generic if supplied as columns | The operation "skip by has-items and keep-mask" is generic, but `terminal_keep` is RayJoin/overlay keep policy. Core can consume a boolean validity mask; it should not compute this policy. |
| lines 119-138 | initialize `face_ids`, `point_ids`, `output_lines`, `chain_headers`, `point_lines`, caches | App-specific current state | These are Python object/list/dict structures tied to author output assembly. They are exactly what Layer 1 must replace with columnar buffers. |
| lines 150-156 | `create_polygon`: assign compact ids to sorted face-pair tuples | App-specific | This is RayJoin overlay polygon/face-id policy. A generic core may dictionary-encode arbitrary keys in the future, but this exact policy cannot live in core. |
| lines 158-178 | `record_output_chain`: create author chain header and append point line references | Mixed; current form app-specific | Group descriptor creation is generic in principle, but the header fields and text layout are author output-chain semantics. Core can store descriptor columns, not write this header. |
| lines 180-210 | `materialize_output_lines_from_generic_assembly` | Mixed; grouping generic, reconstruction app-specific | `assemble_grouped_sequences` is generic. But rebuilding `lines` from `chain_headers` and `point_lines` is still Python text/list work and uses RayJoin schema metadata. |
| lines 212-219 | `point_record`: assign point id and format coordinate line | App-specific | The exact point-id policy and `"{x:.6f} {y:.6f}\n"` text are author-output rules. A future generic dictionary encoder is possible, but this is not one. |
| lines 221-226 | `display_line`: cache formatted coordinate string | App-specific | This is author text formatting and string caching. It is not generic output assembly. |
| lines 228-270 | `emit_direct_dataset_chain`: emit chains with no intersections | App-specific | It uses chain face fields, terminal face classification, point dedupe, author chain ids, and author text lines. |
| lines 272-326 | `flush`: output split chains with intersections | App-specific with small generic subpieces | The keep rule, polygon id construction, dedupe, debug dump, and author line generation are RayJoin/overlay output semantics. Generic core could later consume already-built descriptor/item columns. |
| lines 327-362 | `flush_plain_chain`: output plain chain segment after splits | App-specific with small generic subpieces | Same issue as `flush`: the operation builds author output-chain records, not generic output rows. |
| lines 364-371 | group intersections by edge id | Generic if supplied as columns | Grouping rows by key is generic. But the key meaning, `eid0/eid1`, and intersection row shape are RayJoin/LSI app data. |
| lines 372-395 | iterate dataset chains; skip/no-xsect direct-chain handling | App-specific orchestration | This walks RayJoin CDB chain topology and applies author output policy. Core should not know this. |
| lines 396-421 | walk points, inject intersection points, split by midpoint face | App-specific | This is the heart of Section 5.7 overlay output semantics. It cannot be hidden inside RTDL core as "generic writer." |
| lines 423-425 | call generic assembly and record timing | Generic call, but too late | The call is clean, but it happens after app-specific Python strings and headers already exist. |
| lines 426-428 | `handle.writelines(output_lines)` | File IO | Bulk write is already small (`0.074s` in Goal4933). It is not the bottleneck. |

## Decision

Goal4934 exits:

`needs_layer1_shape_before_decision`

Reason:

Layer 3 is not ready for compiled implementation because the current writer still feeds it Python object/list/string state. The remaining expensive chain loops combine:

- RayJoin CDB chain traversal;
- overlay split policy;
- midpoint face policy;
- face/point id assignment;
- author-compatible output-chain header semantics;
- author-compatible fixed-decimal coordinate text.

However, this is not a full stop. There are reusable generic subproblems:

- grouping by keys;
- stable ordering inside groups;
- descriptor columns;
- item columns;
- validity masks;
- optional dictionary encoding;
- record-buffer materialization.

Those can become RTDL features only if they are exposed through a neutral row-buffer/data-shape contract first.

## Proposed Generic Output IR

The honest generic target is not "write RayJoin output faster." It is:

> typed columns in, deterministic grouped records out.

Minimum candidate IR:

```text
OutputGroupBuffer
  group_key_columns: int/float/string-like primitive columns
  descriptor_columns: primitive columns, one row per group
  group_offsets: int64[group_count]
  group_lengths: int64[group_count]

OutputItemBuffer
  group_id: int64[item_count]
  item_order: int64[item_count]
  payload_columns: primitive columns, one row per item
  validity: optional bool[item_count]

OptionalDictionaryEncodingPlan
  key_columns: primitive columns
  output_id_column: int64
  stable_order: first_seen | sorted

OutputMaterializationPlan
  output_shape: offsets_and_items | descriptors_and_items | columnar_records
  ordering: stable
  formatting: none | generic_numeric_text | app_owned
```

What RTDL core may do:

- sort/group rows;
- produce offsets and lengths;
- materialize descriptor/item columnar records;
- optionally dictionary-encode neutral primitive keys;
- optionally produce generic numeric text if the format is declared generically.

What RTDL core must not do:

- write RayJoin output-chain headers;
- assign RayJoin polygon ids from overlay face pairs;
- decide RayJoin keep/drop policy;
- split chains by midpoint face;
- know map0/map1 overlay semantics in the output layer;
- reproduce the author text format as a built-in RTDL output mode.

## Why Layer 1 Must Come Next

The current generic assembly is called after these app-owned Python objects already exist:

- `chain_headers: dict[int, str]`
- `point_lines: list[str]`
- `point_line_chain_ids: list[int]`
- `point_line_orders: list[int]`

That is too late. A compiled materializer cannot recover performance if its input is already Python text.

The next required goal is therefore:

**Goal4935: Layer 1 Output Row-Buffer/Data-Shape Contract**

It should define the neutral columns the writer can pass to any generic materializer. A RayJoin adapter may map author-specific state into those columns, but the generic materializer must not know why those columns exist.

## Feasibility Judgment

Layer 3 is feasible **only after** Goal4935 proves a neutral row-buffer/data-shape contract.

Current status:

- `layer3_generic_feasible`: not proven.
- `writer_is_app_specific_stop`: too strong, because generic subproblems exist.
- `needs_layer1_shape_before_decision`: correct.

## Required Next Gate

Goal4935 should answer:

1. Can RayJoin output data be represented as neutral descriptor/item columns before text formatting?
2. Can a non-RayJoin fixture use the same shape?
3. Does this shape avoid RayJoin words and author output-chain semantics?
4. Does it keep app-specific final formatting out of RTDL core?

If yes, proceed to a materializer prototype.

If no, stop the performance line and keep output assembly as app-local/paper-reproduction infrastructure.

## Non-Claims

This report does not authorize:

- compiled writer implementation;
- device-resident row-buffer implementation;
- public v2.14.2 performance claim;
- RayJoin-specific output writer in RTDL core;
- any V3/V4 claim;
- any claim that Goal4933 improved performance.

## Final Recommendation

Do Goal4935 next.

Do not implement Goal4936/compiled materializer until Goal4935 proves the neutral data shape.
