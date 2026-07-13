# Goal5072 Aggregate Frontier Reduce CPU Reference Executor Result

Date: 2026-07-06

## Verdict Label

`completed_cpu_reference_executor_for_generic_aggregate_frontier_reduce`

## Purpose

Goal5072 implements the first executable path for the generic aggregate hierarchy line.

The goal is not to reproduce RT-BarnesHut performance and not to add a native backend. The goal is to provide a small, deterministic CPU reference executor that future Numba/CUDA/OptiX implementations can compare against.

## What Changed

Updated:

- `src/rtdsl/aggregate_hierarchy.py`
- `src/rtdsl/__init__.py`
- `tests/goal5066_aggregate_hierarchy_contract_test.py`
- `tests/goal5069_aggregate_frontier_reduce_execution_contract_test.py`

Added:

- `tests/goal5072_aggregate_frontier_reduce_cpu_reference_test.py`

## Public API Additions

New public executor:

```python
aggregate_frontier_reduce_reference_3d(execution, *, softening=0.0)
run_aggregate_frontier_reduce_reference_3d(execution, *, softening=0.0)
```

New/exported status metadata:

```python
AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS
AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS_REFERENCE
AGGREGATE_FRONTIER_REDUCE_3D_REFERENCE_REDUCERS
```

Backend status is now explicit:

```text
reference: implemented_cpu_reference
numba:     not_implemented_contract_only
cuda:      not_implemented_contract_only
optix:     not_implemented_contract_only
embree:    not_implemented_contract_only
hiprt:     not_implemented_contract_only
```

## Reference Executor Semantics

Input:

- `AggregateFrontierReduceExecutionContract3D`
- `backend` must be `reference`
- hierarchy must include generic descriptor columns:
  - `source_leaf_node_index`
  - `node_subtree_end_index`

Supported reducers:

- `aggregate_count`
- `inverse_square_scalar_sum`

Supported opening policies:

- `LeafOnlyOpening()`
- `SizeDistanceOpening(max_ratio=...)`

Output:

```text
source_id
reducer_value_0
reducer_value_1
reducer_value_2
visited_node_count
aggregate_contribution_count
exact_contribution_count
status_code
```

The executor returns rows plus metadata. It fails closed before materialization when `max_output_rows` is too small.

## Genericity Guard

The executor is generic over aggregate hierarchies. It does not reference RT-BarnesHut, author payload logic, Torch extensions, or native OptiX symbols.

The implementation intentionally supports two different shapes:

1. `SizeDistanceOpening + inverse_square_scalar_sum`
2. `LeafOnlyOpening + aggregate_count`

This prevents the reference executor from being merely an inverse-square force-field app in generic clothing.

## What This Does Not Claim

Not claimed:

- native backend implementation;
- device residency;
- Numba/CUDA/OptiX execution;
- RT-BarnesHut paper completion;
- performance improvement;
- parity with author code.

This is a correctness oracle and contract execution reference only.

## Verification

Focused regression:

```text
py -m unittest tests.goal5066_aggregate_hierarchy_contract_test tests.goal5068_aggregate_hierarchy_descriptor_extension_test tests.goal5069_aggregate_frontier_reduce_execution_contract_test tests.goal5070_non_force_genericity_proof_test tests.goal5072_aggregate_frontier_reduce_cpu_reference_test
```

Result:

```text
Ran 25 tests in 0.015s
OK
```

Aggregate hierarchy + RT-BarnesHut adapter regression:

```text
py -m unittest tests.goal5066_aggregate_hierarchy_contract_test tests.goal5067_rt_barneshut_aggregate_hierarchy_adapter_test tests.goal5068_aggregate_hierarchy_descriptor_extension_test tests.goal5069_aggregate_frontier_reduce_execution_contract_test tests.goal5070_non_force_genericity_proof_test tests.goal5072_aggregate_frontier_reduce_cpu_reference_test
```

Result:

```text
Ran 29 tests in 0.063s
OK
```

Combined RT-BarnesHut scaffold + aggregate hierarchy regression:

```text
py -m unittest tests.goal5063_rt_barneshut_paper_reproduction_scaffold_test tests.goal5066_aggregate_hierarchy_contract_test tests.goal5067_rt_barneshut_aggregate_hierarchy_adapter_test tests.goal5068_aggregate_hierarchy_descriptor_extension_test tests.goal5069_aggregate_frontier_reduce_execution_contract_test tests.goal5070_non_force_genericity_proof_test tests.goal5072_aggregate_frontier_reduce_cpu_reference_test
```

Result:

```text
Ran 54 tests in 3.432s
OK
```

Syntax check:

```text
py -m py_compile src/rtdsl/aggregate_hierarchy.py src/rtdsl/__init__.py
```

Result:

```text
OK
```

Export check:

```text
aggregate_frontier_reduce_reference_3d True True
run_aggregate_frontier_reduce_reference_3d True True
AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS True True
AGGREGATE_FRONTIER_REDUCE_3D_REFERENCE_REDUCERS True True
```

Core app-identity scan:

```text
BarnesHut|Treelogy|RTBH|author-optix-payload|load_inline|import torch|rtdl_optix|rayjoin|RayJoin
```

Result for `src/rtdsl/aggregate_hierarchy.py`:

```text
0 matches
```

The local Python runtime still prints:

```text
Could not find platform independent libraries <prefix>
```

The tests completed successfully despite this local environment warning.

## Next Step

Recommended next goal:

```text
Goal5073: Numba reference-parity prototype for aggregate frontier reduce
```

Required boundary for Goal5073:

- use `aggregate_frontier_reduce_reference_3d` as the oracle;
- support both `SizeDistanceOpening + inverse_square_scalar_sum` and `LeafOnlyOpening + aggregate_count`;
- do not import RT-BarnesHut app code into core;
- do not claim performance until parity passes.
