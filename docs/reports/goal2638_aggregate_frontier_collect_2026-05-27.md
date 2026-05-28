# Goal2638 Aggregate Frontier Collect Contract

Date: 2026-05-27

## Decision

Add `AGGREGATE_FRONTIER_COLLECT_2D` as an app-independent row-emission
contract for Barnes-Hut-style aggregate tree traversal pressure.

This is the next correct step after rejecting the native inverse-square force
primitive in Goal2549. The engine may own traversal and frontier IDs. It must
not own the Barnes-Hut inverse-square force law, scoring formula, timestep
integration, or any app-specific reduction.

3-AI review closure for this candidate contract is recorded in
`docs/reports/goal2638_3ai_consensus_2026-05-27.md`.

## Contract

Name:

`generic_aggregate_frontier_collect_2d_v1`

RTDL operation label:

`AGGREGATE_FRONTIER_COLLECT_2D`

Python contract constant:

`rtdsl.AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT`

Python API:

```python
rtdsl.collect_aggregate_frontier_2d(
    source_points,
    tree_nodes,
    theta=...,
    max_rows_per_source=None,
    max_total_rows=None,
    include_debug_diagnostics=False,
)
```

Result layout:

- `source_ids`: source order.
- `row_offsets`: source-offset array of length `source_count + 1`.
- `frontier_rows`: ID-only Python reference rows for debugging and tests.
- `frontier_i64_rows`: row-major partner/native-ready rows with schema
  `(source_id, frontier_kind_code, item_id, owner_aggregate_id, dfs_index,
  resume_index, metadata_flags)`.
- `per_source_summary`: counts and offsets.
- `debug_diagnostics`: optional side channel, emitted only when
  `include_debug_diagnostics=True`; default `frontier_rows` do not contain
  distance or opening-ratio diagnostics.

`metadata_flags` is a reserved contract lane. Current rows must set it to
`0`, meaning no flags set. Partners must ignore unknown future non-zero flags
unless a later contract revision documents them.

Adapters:

- `aggregate_frontier_collect_to_columnar_record_set`: converts the collection
  result into app-independent columnar row payloads.
- `aggregate_frontier_collect_to_partner_columns`: converts the same ID-only
  result into Torch/CuPy-owned int64 columns for downstream partner code.
- `plan_aggregate_frontier_collect_lowering`: records the current target status
  for CPU, partner, Embree, and OptiX.

Kind codes:

- `1`: accepted aggregate node.
- `2`: exact fallback item from a leaf aggregate.

Overflow policy:

`fail_closed_before_result_materialization`

If `max_rows_per_source` or `max_total_rows` is exceeded, the collector raises
`AggregateFrontierOverflowError` with `partial_result_returned=False`.

## Boundary

The contract emits generic IDs, source offsets, and reserved metadata flags
only. Diagnostic distance/opening-ratio fields are not part of default
frontier rows; if needed for tests, they must stay in the explicit
`debug_diagnostics` side channel. The contract does not emit or compute:

- force vectors;
- inverse-square scalar sums;
- source mass times target mass;
- application scores;
- timestep or N-body solver state;
- Barnes-Hut-specific native ABI symbols.

Goal2639 adds the app-name-free native ABI contract and the local Embree native
row collector. OptiX lowering remains future work. This still does not claim
RT-core performance or paper reproduction.

Barnes-Hut inverse-square force reference helpers were moved to
`rtdsl.app_reference.aggregate_force_math`. The top-level `rtdsl.*`
compatibility exports remain for existing examples/tests, but the engine
aggregate-tree module no longer owns the force law.

## Barnes-Hut Integration

The Barnes-Hut research benchmark now exposes:

`aggregate_frontier_collect_bucketized_cpu`

That mode builds the generic bucketized aggregate tree, runs
`collect_aggregate_frontier_2d`, and returns only frontier IDs, offsets, and
metadata. Force computation remains in the existing app/partner paths.

## Runtime Insight

The implementation uses DFS subtree membership metadata:

- `resume_index` gives each node's subtree end in DFS order;
- leaf membership maps each source id to its leaf DFS index;
- containment is checked by range:
  `node.dfs_index <= source_leaf_dfs < subtree_end`.

This preserves the Goal2544 insight without baking Barnes-Hut force semantics
into the engine.

## Claim Boundary

Allowed:

- `AGGREGATE_FRONTIER_COLLECT_2D` is an app-independent CPU reference and
  partner-ready row-layout contract.
- The row layout reserves `metadata_flags` for future backend/version flags
  without adding app-specific fields.
- Partner adapters may consume the emitted ID columns without copying force
  math into the engine.
- The Barnes-Hut app can consume this generic frontier and apply force math
  outside the engine.

Not allowed:

- native Embree/OptiX performance claims;
- RT-BarnesHut paper reproduction claims;
- public speedup wording;
- claims that the engine computes Barnes-Hut force;
- claims that native aggregate-frontier lowering is complete.
