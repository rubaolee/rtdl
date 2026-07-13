# Goal4938 Layer 3 Boundary Relocation Report

Date: 2026-07-03

## Verdict

`boundary_must_move_to_path_split_continuation_before_more_writer_work`

Goal4938 inspected the RayJoin Section 5.7 writer after Goal4937. The conclusion is that another generic output materializer pass is not the right next implementation. The expensive work lives earlier: the app's Python chain loop is doing path/chain splitting, face/point id bookkeeping, and output-chain descriptor construction before RTDL's generic materializer sees anything.

## Why This Goal Exists

Goal4937 tested the obvious Layer 3 wiring:

```text
RayJoin app chain loop -> generic materializer -> app text formatter
```

It preserved byte equality but missed the performance gate. The reason was structural: the app still paid the same `chain_loop_map0` and `chain_loop_map1` cost, then paid a new materialization cost.

Goal4938 asks where the boundary should move if the next implementation is to have a real chance.

## Evidence Inspected

Files:

- `Paper-reproduction-apps/rayjoin-paper/section57_overlay.py`
- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_numba.py`
- `src/rtdsl/output_assembly.py`
- `history/internal_docs/goal4905_writer_internal_breakdown_report_2026-07-03.md`
- `history/internal_docs/goal4934_layer3_feasibility_writer_semantics_audit_2026-07-03.md`
- `history/internal_docs/goal4937_rayjoin_public_sample_materializer_wiring_2026-07-03.md`
- `history/internal_docs/antigravity_goal4937_rayjoin_public_sample_materializer_wiring_review_2026-07-03.md`

Key measured facts:

- Goal4905 found bulk file writing is not the bottleneck: `bulk writelines` was about `0.044s`.
- Goal4937 rerun1 found the materializer route remained byte-equal but slower:
  - plain writer: `2.537364s`
  - materializer writer: `3.067069s`
  - materializer route chain loops: `0.930846s + 0.791196s`
  - materializer assembly: `1.037157s`

## Current Chain Loop Responsibilities

The current Section 5.7 app writer does the following inside the Python chain loop:

| Responsibility | Current Location | Classification |
|---|---|---|
| Iterate CDB chains and edges | app Python writer | Generic shape, but RayJoin data adapter currently supplies it |
| Group intersections by edge id | app Python writer | Generic grouping if supplied as columns |
| Insert intersection points into chain order | app Python writer | Generic path-split shape |
| Split output chains at consecutive intersections | app Python writer | Generic path-split shape with app-supplied labels |
| Query midpoint face between consecutive intersections | already computed before writer | App/overlay label input |
| Decide keep/drop for emitted chain pieces | app Python writer | App policy; must remain app-owned or be supplied as validity mask |
| Assign compact face-pair ids | app Python writer | App dictionary-encoding policy, generic if expressed as key columns |
| Assign compact point ids | app Python writer | Generic dictionary-encoding shape, but exact policy is app-owned |
| Create output-chain descriptor fields | app Python writer | Generic descriptor rows after app supplies columns |
| Format author-compatible text | app Python writer | App-specific, must remain outside RTDL core |

## Boundary Mistake In Goal4937

Goal4937 moved only this part into RTDL generic code:

```text
already-built chain descriptors + already-built point lines
  -> generic materializer
```

That was too late. The generic layer received data after the app had already done the expensive path/chain work. It could not remove the chain loop.

## Correct Boundary

The next boundary must be:

```text
base chain topology
+ split events ordered by edge and position
+ per-interval labels / app validity masks
  -> generic path-split / grouped-record continuation
  -> descriptor/item row buffer
  -> app-owned final text formatter
```

This is not merely an output writer. It is a reusable continuation primitive:

> Turn path/chain topology plus ordered split events into grouped descriptor/item rows.

Possible neutral name:

`prepare_grouped_path_split_output_rows`

or:

`assemble_grouped_path_split_records`

## Proposed Generic Contract

Inputs should be primitive columns, not RayJoin objects:

### Chain columns

- `chain_id`
- `point_offset`
- `point_count`
- optional chain descriptor columns supplied by app

### Base point columns

- `point_id` or original point index
- `x`
- `y`
- `chain_id`
- `point_order`

### Split-event columns

- `chain_id`
- `edge_id`
- `event_order`
- `x`
- `y`
- optional `display_x`
- optional `display_y`
- optional label columns supplied by app

### Interval/label columns

- `left_label`
- `right_label`
- `other_label`
- `validity`

The generic continuation may:

- merge original chain points with split events in stable order,
- split a path into grouped pieces when app-supplied boundary flags say so,
- preserve or emit descriptor columns,
- dictionary-encode neutral key columns if requested,
- produce a `GroupedOutputRowBuffer`.

The generic continuation must not:

- know RayJoin,
- know polygon overlay,
- compute RayJoin keep/drop policy,
- compute RayJoin midpoint face labels,
- write author text format,
- assign author-specific polygon ids unless expressed as generic dictionary encoding over supplied key columns.

## Why This Is Still Potentially Generic

This shape is not unique to RayJoin. It appears in:

- polyline/path segmentation by event rows,
- spatial join reporting grouped hit intervals,
- ray/path contact reporting,
- trajectory segmentation,
- road-network or mesh-edge event extraction,
- any "base chain + ordered events -> grouped emitted records" workload.

RayJoin remains the exam workload. It cannot be the only proof.

## Next Implementation Gate

Do not implement a faster RayJoin writer directly.

The next goal should be:

**Goal4939: Generic grouped path-split row-buffer prototype**

Scope:

1. Define a neutral host-columnar path-split schema.
2. Implement a small host-columnar prototype in `src/rtdsl` with no RayJoin words.
3. Add synthetic tests:
   - one non-RayJoin path-split fixture,
   - one RayJoin-shaped fixture at tiny scale.
4. Require the module source to contain no app-identity terms such as `rayjoin`, `overlay`, `map0`, `map1`, `section57`, or `author`.
5. Only after synthetic tests pass, wire it into the RayJoin public sample as an app adapter.
6. Performance gate on RayJoin:
   - byte equality first,
   - writer time must beat the same-run plain writer,
   - minimum useful target: at least `1.10x` writer speedup,
   - strong target: at least `1.25x` writer speedup.

## Kill Conditions

Stop if any of these happen:

- The proposed schema needs RayJoin-specific field names in RTDL core.
- The generic prototype cannot express a non-RayJoin path-split fixture.
- RayJoin wiring still executes the old Python chain loop before calling the generic layer.
- The RayJoin route is byte-equal but not faster than the same-run plain writer.
- The implementation improves RayJoin only by embedding author output semantics in RTDL core.

## Decision

The next performance attempt is allowed only if it attacks the chain loop directly through a generic path-split continuation. Another downstream materializer or text writer wrapper is not authorized.

Exit label:

`boundary_must_move_to_path_split_continuation_before_more_writer_work`
