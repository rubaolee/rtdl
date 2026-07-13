# Goal5070 Non-Force Genericity Proof Result

Date: 2026-07-06

## Verdict Label

`completed_non_force_genericity_proof_contract_only`

## Objective

Goal5070 was required by the Goal5065 review: the aggregate hierarchy / frontier reduce contract must be shown on a substantially different reducer and opening policy, not merely another inverse-square force-field variant.

## Implemented Generic Opening

Added to `src/rtdsl/aggregate_hierarchy.py`:

- `AGGREGATE_HIERARCHY_3D_OPENING_LEAF_ONLY`
- `AGGREGATE_HIERARCHY_3D_SUPPORTED_OPENINGS`
- `LeafOnlyOpening`

`LeafOnlyOpening` is a topology-only opening policy:

- it does not use size/distance;
- it does not use node size;
- it does not encode a force law;
- it is not tied to RT-BarnesHut.

It represents a traversal policy that descends to leaves before reducing. This is substantially different from `SizeDistanceOpening(max_ratio=...)`.

## Implemented Genericity Proof

Added `tests/goal5070_non_force_genericity_proof_test.py`.

The proof uses:

- opening: `LeafOnlyOpening()`
- reducer: `aggregate_count`
- same execution contract: `AggregateFrontierReduceExecutionContract3D`

This proves the contract can express a non-force aggregate traversal/reduction case:

- no inverse-square scalar sum;
- no inverse-square vector sum;
- no size/distance opening;
- no app-specific opening object.

## Public Contract Updates

Updated public exports in `src/rtdsl/__init__.py`:

- `LeafOnlyOpening`
- `AGGREGATE_HIERARCHY_3D_OPENING_LEAF_ONLY`
- `AGGREGATE_HIERARCHY_3D_SUPPORTED_OPENINGS`

`describe_aggregate_hierarchy_3d_contract()` now lists both opening policies:

- `size_distance_opening`
- `leaf_only_opening`

## Boundary

Goal5070 does not:

- implement a traversal backend;
- add CUDA/OptiX/native symbols;
- add a paper app shortcut;
- claim speedup;
- claim paper reproduction;
- move RT-BarnesHut comparator or payload policy into RTDL core.

Unsupported opening objects fail closed.

## Verification

Executed:

```text
py -m unittest tests.goal5066_aggregate_hierarchy_contract_test tests.goal5067_rt_barneshut_aggregate_hierarchy_adapter_test tests.goal5068_aggregate_hierarchy_descriptor_extension_test tests.goal5069_aggregate_frontier_reduce_execution_contract_test tests.goal5070_non_force_genericity_proof_test
```

Result:

```text
Ran 24 tests in 0.061s
OK
```

Executed:

```text
py -m unittest tests.goal5063_rt_barneshut_paper_reproduction_scaffold_test tests.goal5066_aggregate_hierarchy_contract_test tests.goal5067_rt_barneshut_aggregate_hierarchy_adapter_test tests.goal5068_aggregate_hierarchy_descriptor_extension_test tests.goal5069_aggregate_frontier_reduce_execution_contract_test tests.goal5070_non_force_genericity_proof_test
```

Result:

```text
Ran 49 tests in 3.386s
OK
```

The local Python runtime still prints `Could not find platform independent libraries <prefix>` before test output. The tests completed successfully despite that environment warning.

## What This Proves

- The aggregate hierarchy contract is not only an inverse-square force-field shape.
- The execution contract can pair a topology-only opening with a non-force reducer.
- The public API can express a different aggregate traversal use case without app identity.

## What This Does Not Prove

- It does not prove runtime execution.
- It does not prove backend readiness.
- It does not prove performance.
- It does not prove RT-BarnesHut paper completion.

## Next Logical Goal

Goal5071 can be a release-boundary consolidation for Goals5066-5070:

- summarize the generic RTDL API additions;
- summarize RT-BarnesHut app-owned adapter status;
- confirm public surface leak scans;
- decide whether the next implementation goal should be a CPU reference executor or a Numba partner prototype.
