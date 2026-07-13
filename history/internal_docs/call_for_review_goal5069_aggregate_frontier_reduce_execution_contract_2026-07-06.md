# Call For Review: Goal5069 Aggregate Frontier Reduce Execution Contract

Date: 2026-07-06

Please review:

- `history/internal_docs/goal5069_aggregate_frontier_reduce_execution_contract_result_2026-07-06.md`
- `src/rtdsl/aggregate_hierarchy.py`
- `tests/goal5069_aggregate_frontier_reduce_execution_contract_test.py`
- `tests/goal5068_aggregate_hierarchy_descriptor_extension_test.py`

## Requested Verdict Labels

Use one:

- `approve_goal5069_backend_neutral_execution_contract_no_backend`
- `approve_with_required_amendments`
- `block_goal5069_execution_contract`

## Context

Goal5066 added generic `AggregateHierarchy3D` schema.
Goal5067 mapped RT-BarnesHut prepared arrays into that schema.
Goal5068 promoted `source_leaf_node_index` and `node_subtree_end_index` as optional generic traversal descriptors.

Goal5069 now defines a backend-neutral aggregate frontier reduce execution contract, but still does not implement a backend.

## Review Questions

1. Does `AggregateFrontierReduceExecutionContract3D` remain a contract/plan object rather than an executor?
2. Are the listed backend names (`reference`, `numba`, `cuda`, `optix`, `embree`, `hiprt`) clearly vocabulary only, with status `not_implemented_contract_only`?
3. Does the contract correctly refuse `backend_execution_authorized` and `native_backend_symbols_authorized`?
4. Is the output schema generic enough for scalar and vector reducers?
5. Are required descriptor columns correctly identified as `source_leaf_node_index` and `node_subtree_end_index`?
6. Is the overflow policy `fail_closed_before_result_materialization` appropriate for a future exact traversal/reduction backend?
7. Do unsupported backends, unsupported overflow policies, and negative capacity fail closed?
8. Does the implementation avoid Torch/CUDA/OptiX/native execution and app identity leakage?
9. Did the Goal5063/5066/5067/5068/5069 regression preserve current RT-BarnesHut bounded same-input evidence?
10. Is Goal5070 the right next step: a substantially different reducer and opening policy over the same contract, not another inverse-square force-field variant?

## Expected Review Output

Please include:

- verdict label;
- blocking findings, if any;
- required amendments, if any;
- non-blocking notes;
- answers to the 10 review questions.
