# Goal5073 Aggregate Frontier Reduce Numba Parity Prototype Result

Date: 2026-07-06

## Verdict Label

`completed_optional_numba_cpu_parity_prototype_for_generic_aggregate_frontier_reduce`

## Purpose

Goal5073 adds the first Numba partner prototype for the generic aggregate hierarchy line.

The goal is parity against the Goal5072 CPU reference executor. It is not a CUDA backend, not a native traversal backend, not device-resident, and not a performance claim.

## What Changed

Updated:

- `src/rtdsl/aggregate_hierarchy.py`
- `src/rtdsl/__init__.py`
- `tests/goal5069_aggregate_frontier_reduce_execution_contract_test.py`
- `tests/goal5070_non_force_genericity_proof_test.py`

Added:

- `tests/goal5073_aggregate_frontier_reduce_numba_parity_test.py`

## Public API Additions

New optional Numba executor:

```python
aggregate_frontier_reduce_numba_available()
aggregate_frontier_reduce_numba_3d(execution, *, softening=0.0)
run_aggregate_frontier_reduce_numba_3d(execution, *, softening=0.0)
```

New/exported status metadata:

```python
AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS_NUMBA
AGGREGATE_FRONTIER_REDUCE_3D_NUMBA_REDUCERS
```

API maturity is now:

```text
reference_and_optional_numba_cpu_executor_no_native_backend
```

Backend status is now:

```text
reference: implemented_cpu_reference
numba:     optional_numba_cpu_reference_prototype
cuda:      not_implemented_contract_only
optix:     not_implemented_contract_only
embree:    not_implemented_contract_only
hiprt:     not_implemented_contract_only
```

## Numba Prototype Semantics

Input:

- `AggregateFrontierReduceExecutionContract3D`
- `backend` must be `numba`
- hierarchy must include:
  - `source_leaf_node_index`
  - `node_subtree_end_index`

Supported reducers:

- `aggregate_count`
- `inverse_square_scalar_sum`

Supported opening policies:

- `LeafOnlyOpening()`
- `SizeDistanceOpening(max_ratio=...)`

The wrapper converts the validated generic hierarchy columns into NumPy arrays and runs a CPU `numba.njit` traversal kernel. The result rows use the same public output schema as the CPU reference executor.

## Runtime Dependency

Local environment initially did not include Numba:

```text
WARNING: Package(s) not found: numba
```

Numba was installed locally for verification:

```text
py -m pip install numba
```

Installed packages:

```text
numba-0.66.0
llvmlite-0.48.0
```

After installation:

```text
aggregate_frontier_reduce_numba_available: True
```

The executor still fails closed if Numba is missing. It does not silently fall back to the Python reference path.

## Parity Evidence

Goal5073 tests compare Numba rows against `aggregate_frontier_reduce_reference_3d` for:

1. `LeafOnlyOpening + aggregate_count`
2. `SizeDistanceOpening + inverse_square_scalar_sum`

The tests compare:

- source ids;
- reducer values;
- visited-node counts;
- aggregate contribution counts;
- exact contribution counts;
- status codes.

The missing-runtime branch is also represented. In this local run it is skipped because Numba is now installed.

## Verification

Goal5073 focused run:

```text
py -m unittest tests.goal5073_aggregate_frontier_reduce_numba_parity_test
```

Result:

```text
Ran 6 tests in 2.690s
OK (skipped=1)
```

Combined RT-BarnesHut scaffold + aggregate hierarchy regression:

```text
py -m unittest tests.goal5063_rt_barneshut_paper_reproduction_scaffold_test tests.goal5066_aggregate_hierarchy_contract_test tests.goal5067_rt_barneshut_aggregate_hierarchy_adapter_test tests.goal5068_aggregate_hierarchy_descriptor_extension_test tests.goal5069_aggregate_frontier_reduce_execution_contract_test tests.goal5070_non_force_genericity_proof_test tests.goal5072_aggregate_frontier_reduce_cpu_reference_test tests.goal5073_aggregate_frontier_reduce_numba_parity_test
```

Result:

```text
Ran 60 tests in 5.767s
OK (skipped=1)
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
aggregate_frontier_reduce_numba_available True True
aggregate_frontier_reduce_numba_3d True True
run_aggregate_frontier_reduce_numba_3d True True
AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS_NUMBA True True
AGGREGATE_FRONTIER_REDUCE_3D_NUMBA_REDUCERS True True
numba_available True
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

## What This Does Not Claim

Not claimed:

- CUDA execution;
- OptiX traversal;
- native backend implementation;
- device residency;
- author-paper reproduction;
- RT-BarnesHut whole-program parity;
- performance improvement.

This is a generic optional CPU Numba parity prototype.

## Next Step

Recommended next goal:

```text
Goal5074: integrate the generic Numba aggregate frontier executor into the RT-BarnesHut paper app adapter in a bounded same-input parity mode
```

Goal5074 should remain app-owned:

- input: app prepared arrays adapted to `AggregateHierarchy3D`;
- execution: public `aggregate_frontier_reduce_numba_3d`;
- oracle: public `aggregate_frontier_reduce_reference_3d`;
- no app code imported into `src/rtdsl`;
- no performance claim until parity and timing are separately reviewed.
