# Goal5071 RT-BarnesHut / Aggregate Hierarchy Release Boundary Consolidation

Date: 2026-07-06

## Verdict Label

`completed_release_boundary_consolidation_for_aggregate_hierarchy_contract_line`

## Purpose

Goal5071 consolidates Goals5066-5070. It does not add new API or implementation. It records:

- what generic RTDL language surface now exists;
- what remains RT-BarnesHut app-owned;
- what was verified locally;
- what public-surface leakage was checked;
- what the next implementation decision should be.

## Generic RTDL Additions

The generic system additions are in `src/rtdsl/aggregate_hierarchy.py` and exported through `rtdsl`.

### Schema

- `AggregateHierarchy3D`
- `PreparedAggregateHierarchy3D`
- `aggregate_hierarchy_3d(...)`
- `prepare_aggregate_hierarchy_3d(...)`

Generic columns:

- point columns: `point_x`, `point_y`, `point_z`, `point_weight`
- node columns: `node_cx`, `node_cy`, `node_cz`, `node_half_size`, `node_weight`
- topology columns: `member_offsets`, `member_indices`, `child_offsets`, `child_indices`
- continuation columns: `node_next_index`, `node_resume_index`, `node_rope_index`
- descriptor columns: `source_leaf_node_index`, `node_subtree_end_index`

### Opening Policies

- `SizeDistanceOpening(max_ratio=...)`
- `LeafOnlyOpening()`

The second policy was added specifically to prove that the contract is not only an inverse-square force-field shape.

### Reducers

- `aggregate_count`
- `inverse_square_scalar_sum`
- `inverse_square_vector_sum`

### Execution Contract

- `AggregateFrontierReduceSpec3D`
- `AggregateFrontierReduceExecutionContract3D`
- `aggregate_frontier_reduce_spec_3d(...)`
- `aggregate_frontier_reduce_execution_contract_3d(...)`

Declared backend vocabulary:

- `reference`
- `numba`
- `cuda`
- `optix`
- `embree`
- `hiprt`

All backend statuses are currently:

```text
not_implemented_contract_only
```

This is a contract line, not an executor line.

## RT-BarnesHut App-Owned Pieces

The paper app remains under `Paper-reproduction-apps/rt-barneshut-paper/`.

App-owned pieces include:

- patched author setup and comparator scripts;
- prepared-state dump reader;
- force-output comparison;
- author phase-boundary review;
- `goal2547_barnes_hut_3d_scalar_subtree_kernel.py` diagnostic CUDA extension path;
- `aggregate_hierarchy_adapter.py`, which maps app prepared arrays into generic `AggregateHierarchy3D`;
- raw app fields that remain outside RTDL core:
  - `contract_source`
  - raw `tree`
  - raw `points`
  - raw `nodes`

The app adapter no longer treats `source_leaf_node_index` or `node_subtree_end_index` as app-only gaps; those are now generic descriptors.

## Current RT-BarnesHut Reproduction Status

The current status remains bounded:

- bounded same-input force-kernel reproduction is complete;
- paper reproduction is not complete;
- whole-program parity is not claimed;
- paper-scale benchmark parity is not claimed.

Known evidence from the RT-BarnesHut line:

- body count: `32768`
- mismatch count: `0`
- max relative error: `2.3653388501211796e-06`
- narrow resident force-kernel comparison:
  - RTDL resident kernel min: `1.1904959678649902 ms`
  - author RT force phase: `5.579 ms`
  - narrow min ratio RTDL/author: `0.21338877359114364`
- broader prep+kernel envelope:
  - RTDL approx: `336.98 ms`
  - author approx: `99.91 ms`
  - RTDL approx `3.37x` slower

The broader envelope remains the honest context for end-to-end interpretation.

## Verification

Latest focused aggregate hierarchy contract run:

```text
py -m unittest tests.goal5066_aggregate_hierarchy_contract_test tests.goal5067_rt_barneshut_aggregate_hierarchy_adapter_test tests.goal5068_aggregate_hierarchy_descriptor_extension_test tests.goal5069_aggregate_frontier_reduce_execution_contract_test tests.goal5070_non_force_genericity_proof_test
```

Result:

```text
Ran 24 tests in 0.061s
OK
```

Latest combined RT-BarnesHut scaffold + aggregate hierarchy run:

```text
py -m unittest tests.goal5063_rt_barneshut_paper_reproduction_scaffold_test tests.goal5066_aggregate_hierarchy_contract_test tests.goal5067_rt_barneshut_aggregate_hierarchy_adapter_test tests.goal5068_aggregate_hierarchy_descriptor_extension_test tests.goal5069_aggregate_frontier_reduce_execution_contract_test tests.goal5070_non_force_genericity_proof_test
```

Result:

```text
Ran 49 tests in 3.386s
OK
```

The local Python runtime still prints `Could not find platform independent libraries <prefix>` before test output. The tests completed successfully despite that environment warning.

## Public Surface Scan

Executed scan target:

```text
README.md docs examples/current src/rtdsl/aggregate_hierarchy.py
```

Patterns:

```text
Goal[0-9]+|Claude|Gemini|Antigravity|call_for_review|verdict|BarnesHut|RTBH|Treelogy|author-optix-payload
```

Findings:

- `src/rtdsl/aggregate_hierarchy.py`: no matches for goal numbers, internal review terms, app identity, or backend implementation terms.
- `README.md` / `docs` / `examples/current`: existing Barnes-Hut benchmark/app catalog references remain present and are appropriate for public app/benchmark documentation.

Interpretation:

- Core public API surface is app-name-free.
- Public benchmark/app docs may mention Barnes-Hut/RT-BarnesHut as app names.

## What Is Ready

Ready as contract-level RTDL language surface:

- generic 3D aggregate hierarchy schema;
- generic traversal descriptors;
- two opening policies;
- multiple reducer names;
- backend-neutral execution contract;
- app adapter from RT-BarnesHut prepared arrays to generic schema;
- non-force genericity proof.

## What Is Not Ready

Not ready:

- reference executor;
- Numba executor;
- CUDA/OptiX/native backend;
- device-resident traversal;
- performance claims;
- full RT-BarnesHut paper reproduction.

## Next Implementation Decision

Before implementing runtime execution, choose one:

1. **CPU reference executor first**
   - Pros: easiest correctness oracle, backend-independent, helps future Numba/CUDA tests.
   - Cons: no performance value.

2. **Numba prototype first**
   - Pros: aligns with the user-selected partner direction.
   - Cons: harder to debug without a reference executor, risk of app-shaped implementation.

Recommendation: CPU reference executor first, then Numba. The reference executor should support both:

- `SizeDistanceOpening + inverse_square_scalar_sum`;
- `LeafOnlyOpening + aggregate_count`.

That keeps the next step generic rather than RT-BarnesHut-shaped.
