# Call For Review: Goal5067 RT-BarnesHut Prepared Arrays To AggregateHierarchy3D Adapter

Date: 2026-07-06

Please review:

- `history/internal_docs/goal5067_rt_barneshut_aggregate_hierarchy_adapter_result_2026-07-06.md`
- `Paper-reproduction-apps/rt-barneshut-paper/aggregate_hierarchy_adapter.py`
- `tests/goal5067_rt_barneshut_aggregate_hierarchy_adapter_test.py`
- `src/rtdsl/aggregate_hierarchy.py`

## Requested Verdict Labels

Use one:

- `approve_goal5067_app_owned_adapter_to_generic_hierarchy`
- `approve_with_required_amendments`
- `block_goal5067_adapter`

## Context

Goal5066 added a schema-only public RTDL contract:

- `AggregateHierarchy3D`
- `SizeDistanceOpening`
- `AggregateFrontierReduceSpec3D`

Goal5067 should remain app-owned. Its job is to prove that the current RT-BarnesHut prepared-state packet can be mapped into the generic contract and to expose the remaining schema gaps. It must not implement a backend or move author comparator policy into RTDL core.

## Review Questions

1. Does the adapter correctly consume the existing prepared-array reader output rather than inventing a second source format?
2. Does it map point, node, member, child, and continuation columns into `AggregateHierarchy3D` correctly?
3. Does it map `node_next_prim_index` / `node_auto_rope_index` to generic `node_next_index` / `node_rope_index` names without promoting app identity into RTDL core?
4. Does it correctly use `SizeDistanceOpening(max_ratio=0.5)` and `inverse_square_scalar_sum` as a reducer spec?
5. Is the schema gap report honest, especially for `source_leaf_node_index` and `node_subtree_end_index`?
6. Does the adapter avoid Torch/CUDA/native execution and remain app-owned?
7. Does the adapter avoid claiming full paper reproduction, speedup, or backend readiness?
8. Do the tests prove both synthetic prepared arrays and author-binary continuation fields map into the generic contract?
9. Did the combined Goal5063/5066/5067 regression preserve the existing RT-BarnesHut evidence?
10. Is the proposed next step correct: decide generically whether source-to-leaf and subtree-end descriptors belong in the public contract, without moving comparator policy into core?

## Expected Review Output

Please include:

- verdict label;
- blocking findings, if any;
- required amendments, if any;
- non-blocking notes;
- answers to the 10 review questions.
