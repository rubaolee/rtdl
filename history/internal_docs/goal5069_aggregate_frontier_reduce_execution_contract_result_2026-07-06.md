# Goal5069 Aggregate Frontier Reduce Execution Contract Result

Date: 2026-07-06

## Verdict Label

`completed_backend_neutral_execution_contract_no_backend`

## Objective

Goal5069 defines a backend-neutral execution contract for aggregate frontier reduce over `AggregateHierarchy3D`.

It is intentionally not a backend implementation. The goal is to separate:

- hierarchy input schema;
- traversal descriptors;
- opening policy;
- reducer;
- output row schema;
- backend execution status;
- overflow semantics.

## Implemented Contract

Updated `src/rtdsl/aggregate_hierarchy.py` with:

- `AGGREGATE_FRONTIER_REDUCE_3D_EXECUTION_CONTRACT`
- `AGGREGATE_FRONTIER_REDUCE_3D_BACKENDS`
- `AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS_NOT_IMPLEMENTED`
- `AGGREGATE_FRONTIER_REDUCE_3D_OUTPUT_SCHEMA`
- `AGGREGATE_FRONTIER_REDUCE_3D_OVERFLOW_POLICY`
- `AggregateFrontierReduceExecutionContract3D`
- `aggregate_frontier_reduce_execution_contract_3d(...)`

The execution contract consumes an `AggregateFrontierReduceSpec3D` and records:

- selected backend;
- backend status;
- required descriptor columns;
- output row schema;
- overflow policy;
- max output rows;
- claim boundary.

## Backend Status

Supported backend names are declared as vocabulary only:

- `reference`
- `numba`
- `cuda`
- `optix`
- `embree`
- `hiprt`

Every backend status is currently:

```text
not_implemented_contract_only
```

This is deliberate. Goal5069 does not authorize execution or native symbols.

## Output Schema

The backend-neutral output row schema is:

- `source_id`
- `reducer_value_0`
- `reducer_value_1`
- `reducer_value_2`
- `visited_node_count`
- `aggregate_contribution_count`
- `exact_contribution_count`
- `status_code`

This schema can represent scalar reducers by using `reducer_value_0`, while vector reducers can use all three reducer value columns.

## Required Descriptors

The execution contract requires:

- `source_leaf_node_index`
- `node_subtree_end_index`

These were promoted in Goal5068 as generic hierarchy traversal descriptors.

## Overflow Policy

The only accepted overflow policy is:

```text
fail_closed_before_result_materialization
```

Unsupported backends, unsupported overflow policies, and negative `max_output_rows` fail closed.

## Boundary

Goal5069 does not:

- implement CUDA/Torch/OptiX/native execution;
- add native symbols;
- move RT-BarnesHut comparator policy into core;
- encode author payload policy;
- claim paper reproduction;
- claim speedup.

## Verification

Executed:

```text
py -m unittest tests.goal5066_aggregate_hierarchy_contract_test tests.goal5067_rt_barneshut_aggregate_hierarchy_adapter_test tests.goal5068_aggregate_hierarchy_descriptor_extension_test tests.goal5069_aggregate_frontier_reduce_execution_contract_test
```

Result:

```text
Ran 19 tests in 0.075s
OK
```

Executed:

```text
py -m unittest tests.goal5063_rt_barneshut_paper_reproduction_scaffold_test tests.goal5066_aggregate_hierarchy_contract_test tests.goal5067_rt_barneshut_aggregate_hierarchy_adapter_test tests.goal5068_aggregate_hierarchy_descriptor_extension_test tests.goal5069_aggregate_frontier_reduce_execution_contract_test
```

Result:

```text
Ran 44 tests in 3.534s
OK
```

The local Python runtime still prints `Could not find platform independent libraries <prefix>` before test output. The tests completed successfully despite that environment warning.

## What This Proves

- RTDL now has a backend-neutral contract shape for 3D aggregate frontier reduce.
- The contract can express backend status without pretending implementation exists.
- Output schema and overflow policy are explicit.
- The RT-BarnesHut scaffold still passes with the new generic contract additions.

## What This Does Not Prove

- It does not prove a reference reducer implementation.
- It does not prove Numba, CUDA, OptiX, Embree, or HIPRT execution.
- It does not prove device residency.
- It does not prove RT-BarnesHut paper completion.
- It does not prove any performance.

## Next Logical Goal

Goal5070 should provide the genericity proof requested in the Goal5065 review: a substantially different reducer and opening policy over the same `AggregateHierarchy3D` execution contract. Another inverse-square force-field variant is not sufficient.
