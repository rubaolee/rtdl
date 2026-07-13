# Goal5068 Aggregate Hierarchy Descriptor Extension Result

Date: 2026-07-06

## Verdict Label

`completed_generic_source_leaf_and_subtree_descriptor_extension`

## Objective

Goal5067 exposed two remaining app-owned fields in the RT-BarnesHut prepared-array adapter:

- `source_leaf_node_index`
- `node_subtree_end_index`

Goal5068 decided whether these fields are RT-BarnesHut-specific or generic hierarchy traversal descriptors. The result: both are generic enough to belong in the `AggregateHierarchy3D` schema as optional descriptors.

## Design Decision

Promoted as generic optional descriptor columns:

- `source_leaf_node_index`: one node index per point/source row, pointing to the leaf node that owns that source.
- `node_subtree_end_index`: one exclusive DFS subtree-end index per node.

These are not force-law or comparator semantics. They are generic traversal descriptors:

- source-to-leaf descriptors support containment/self-exclusion policies;
- subtree-end descriptors support DFS range skipping/resume behavior;
- neither requires a Barnes-Hut-specific opening rule;
- neither encodes author payload policy.

## Implementation

Updated `src/rtdsl/aggregate_hierarchy.py`:

- added optional `source_leaf_node_index`;
- added optional `node_subtree_end_index`;
- added descriptor metadata in `AggregateHierarchy3D.to_metadata()`;
- added contract description entries:
  - `descriptor_columns = ("source_leaf_node_index", "node_subtree_end_index")`;
  - `descriptor_index_base = "zero_based"`.

Updated `Paper-reproduction-apps/rt-barneshut-paper/aggregate_hierarchy_adapter.py`:

- passes `source_leaf_node_index` and `node_subtree_end_index` into `AggregateHierarchy3D`;
- moves those fields from `app_owned_fields_not_promoted_to_core` into `generic_descriptor_fields_promoted`.

## Validation Semantics

`source_leaf_node_index` is validated fail-closed:

- length must equal `point_count`;
- each value must be a valid node index;
- each value must reference a leaf node;
- the referenced leaf must contain the corresponding point index in its member range.

`node_subtree_end_index` is validated fail-closed:

- length must equal `node_count`;
- each value must satisfy `node_index < end <= node_count`;
- each child index for a node must be inside that node's subtree range.

## Boundary

This does not promote:

- author comparator policy;
- author OptiX payload policy;
- inverse-square force semantics;
- CUDA/Torch kernel code;
- native backend symbols;
- performance claims.

The RT-BarnesHut adapter remains app-owned. RTDL core receives only generic descriptors.

## Verification

Executed:

```text
py -m unittest tests.goal5066_aggregate_hierarchy_contract_test tests.goal5067_rt_barneshut_aggregate_hierarchy_adapter_test tests.goal5068_aggregate_hierarchy_descriptor_extension_test
```

Result:

```text
Ran 14 tests in 0.086s
OK
```

Executed:

```text
py -m unittest tests.goal5063_rt_barneshut_paper_reproduction_scaffold_test tests.goal5066_aggregate_hierarchy_contract_test tests.goal5067_rt_barneshut_aggregate_hierarchy_adapter_test tests.goal5068_aggregate_hierarchy_descriptor_extension_test
```

Result:

```text
Ran 39 tests in 3.170s
OK
```

The local Python runtime still prints `Could not find platform independent libraries <prefix>` before test output. The tests completed successfully despite that environment warning.

## What This Proves

- The two descriptor fields are now expressible in generic RTDL schema.
- The RT-BarnesHut adapter can map author prepared arrays without listing those two fields as app-owned gaps.
- The descriptors are validated structurally, not blindly accepted.

## What This Does Not Prove

- It does not prove a 3D native traversal backend.
- It does not prove a device-resident hierarchy traversal.
- It does not prove a force-law implementation.
- It does not prove whole-program paper reproduction.
- It does not prove a speedup.

## Next Logical Goal

Goal5069 can define a backend-neutral execution contract for aggregate frontier reduce over `AggregateHierarchy3D`, still without implementing CUDA/native execution. That contract should separate:

- traversal descriptor inputs;
- opening policy;
- reducer;
- output row schema;
- backend execution status.
