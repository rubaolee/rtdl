# Goal5067 RT-BarnesHut Prepared Arrays To AggregateHierarchy3D Adapter Result

Date: 2026-07-06

## Verdict Label

`completed_app_owned_prepared_arrays_to_aggregate_hierarchy_adapter`

## Objective

Goal5067 followed Goal5066's contract/schema-only RTDL API by building the first app-owned adapter:

- consume the RT-BarnesHut prepared-array packet already produced/read by the reproduction scaffold;
- map it into RTDL's generic `AggregateHierarchy3D` contract;
- expose exactly which fields remain app-owned and are not promoted into core;
- avoid backend execution, CUDA/native changes, app migration, and performance claims.

## Implemented Adapter

Added:

- `Paper-reproduction-apps/rt-barneshut-paper/aggregate_hierarchy_adapter.py`

The adapter provides:

- `prepared_arrays_to_aggregate_hierarchy(prepared, max_ratio=0.5)`
- `read_prepared_arrays_as_aggregate_hierarchy(path, max_ratio=0.5, reader=None)`
- `describe_adapter_contract()`

The adapter returns a packet with:

- `hierarchy`: `rtdsl.AggregateHierarchy3D`
- `prepared_hierarchy`: `rtdsl.PreparedAggregateHierarchy3D`
- `reduce_spec`: `rtdsl.AggregateFrontierReduceSpec3D`
- `metadata`: contract/gap/boundary metadata

## Mapping

Prepared-array input fields mapped into generic RTDL schema:

- `point_x`, `point_y`, `point_z`, `point_mass` -> `point_x`, `point_y`, `point_z`, `point_weight`
- `node_cx`, `node_cy`, `node_cz`, `node_half_size`, `node_mass` -> generic node columns
- `member_offsets`, `member_indices` -> member topology
- `child_offsets`, `child_indices` -> child topology
- `node_next_prim_index` -> `node_next_index`
- `node_resume_index` -> `node_resume_index`
- `node_auto_rope_index` -> `node_rope_index`

The opening and reducer are represented as:

- `SizeDistanceOpening(max_ratio=0.5)`
- `inverse_square_scalar_sum`

## Schema Gap Report

The adapter deliberately leaves these fields app-owned and not promoted into RTDL core:

- `source_leaf_node_index`
- `node_subtree_end_index`
- `contract_source`
- `tree`
- `points`
- `nodes`

These are currently needed by the RT-BarnesHut diagnostic execution/comparator line, but Goal5067 does not authorize making them public RTDL language primitives.

Supersession note: Goal5068 later promoted `source_leaf_node_index` and
`node_subtree_end_index` as generic optional traversal descriptors in
`AggregateHierarchy3D`. The remaining app-owned fields after Goal5068 are
`contract_source`, `tree`, `points`, and `nodes`.

## Boundary

The adapter is app-owned. It does not:

- add a native symbol;
- run CUDA/OptiX;
- import Torch;
- use `load_inline`;
- move author comparator/payload policy into RTDL core;
- claim speedup;
- claim full paper reproduction.

RTDL core receives only the generic `AggregateHierarchy3D` contract from Goal5066.

## Verification

Executed:

```text
py -m unittest tests.goal5067_rt_barneshut_aggregate_hierarchy_adapter_test
```

Result:

```text
Ran 4 tests in 0.063s
OK
```

Executed:

```text
py -m unittest tests.goal5063_rt_barneshut_paper_reproduction_scaffold_test tests.goal5066_aggregate_hierarchy_contract_test tests.goal5067_rt_barneshut_aggregate_hierarchy_adapter_test
```

Result:

```text
Ran 35 tests in 3.098s
OK
```

The local Python runtime still prints `Could not find platform independent libraries <prefix>` before test output. The tests completed successfully despite that environment warning.

## What This Proves

- The existing RT-BarnesHut prepared-array reader can feed the generic `AggregateHierarchy3D` contract.
- Author-binary continuation fields can be represented with the generic continuation names:
  - `node_next_index`;
  - `node_rope_index`;
  - `node_resume_index`.
- The app-owned fields not present in the public RTDL contract are explicitly reported.
- The adapter does not require a backend rewrite.

## What This Does Not Prove

- It does not prove a device-resident 3D aggregate traversal backend.
- It does not prove native RTDL execution of this hierarchy.
- It does not prove paper-scale reproduction.
- It does not prove whole-program parity.
- It does not prove a performance improvement.

## Next Logical Goal

Goal5068 can decide whether the schema gaps are acceptable for the next stage, or whether the public generic contract needs a separate extension for source-to-leaf mappings / subtree-end descriptors. That decision should remain generic and must not promote RT-BarnesHut comparator policy into core.
