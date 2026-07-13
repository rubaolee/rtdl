# Goal5066 Aggregate Hierarchy Contract / Schema Result

Date: 2026-07-06

## Verdict Label

`completed_aggregate_hierarchy_contract_schema_only_no_backend`

## Objective

Goal5066 was authorized after the Goal5065 review amendments as a narrow contract/schema step:

- extract the generic part of the RT-BarnesHut reproduction discussion into an RTDL language contract;
- keep the public API app-name-free;
- avoid backend execution, CUDA/native rewrites, app migration, or performance claims;
- preserve the existing RT-BarnesHut bounded same-input evidence.

## Implemented Public Contract

Added `src/rtdsl/aggregate_hierarchy.py` with a schema-only public contract:

- `AggregateHierarchy3D`
- `PreparedAggregateHierarchy3D`
- `AggregateFrontierReduceSpec3D`
- `SizeDistanceOpening(max_ratio=...)`
- `aggregate_hierarchy_3d(...)`
- `prepare_aggregate_hierarchy_3d(...)`
- `aggregate_frontier_reduce_spec_3d(...)`
- `describe_aggregate_hierarchy_3d_contract()`
- `validate_aggregate_hierarchy_3d_contract()`

The contract covers:

- point columns: `point_x`, `point_y`, `point_z`, `point_weight`;
- node columns: `node_cx`, `node_cy`, `node_cz`, `node_half_size`, `node_weight`;
- topology columns: `member_offsets`, `member_indices`, `child_offsets`, `child_indices`;
- optional continuation columns: `node_next_index`, `node_resume_index`, `node_rope_index`;
- generic opening policy: `SizeDistanceOpening(max_ratio=...)`;
- generic reducer vocabulary:
  - `aggregate_count`;
  - `inverse_square_scalar_sum`;
  - `inverse_square_vector_sum`.

## Boundary

The implementation is deliberately contract-only:

- `api_maturity = contract_schema_only_no_backend`;
- `backend_execution_authorized = false`;
- `native_backend_symbols_authorized = false`;
- `paper_reproduction_claim_authorized = false`;
- `whole_program_speedup_claim_authorized = false`;
- no CUDA, OptiX, native, or runtime backend was added;
- no RT-BarnesHut author comparator mechanism was moved into RTDL core;
- no app migration was attempted.

This does not claim the RT-BarnesHut paper reproduction is complete. It only creates a generic RTDL language surface that can later host a hierarchy-traversal implementation if future goals authorize that work.

## Genericity Checks

The public API uses generic names:

- `AggregateHierarchy3D`;
- `SizeDistanceOpening`;
- `AggregateFrontierReduceSpec3D`.

It does not expose the rejected `BarnesHutOpening` name. The contract test checks public exports and `dir(rtdsl)` for app identity names, and the new module source for app identity leakage.

The test also verifies that `aggregate_count` is accepted as a non-force reducer. This matters because the next genericity proof must not merely be another inverse-square force-field case.

## Validation Semantics

The contract validates:

- matching point-column lengths;
- matching node-column lengths;
- finite numeric values;
- non-negative weights and node half sizes;
- monotonic offset arrays;
- member index bounds;
- child index bounds;
- continuation columns as zero-based node indices with `-1` as missing sentinel;
- unsupported reducer rejection;
- invalid `SizeDistanceOpening(max_ratio <= 0)` rejection.

External adapters must translate their own dump formats into this public schema before using it.

## Files Changed

- `src/rtdsl/aggregate_hierarchy.py`
- `src/rtdsl/__init__.py`
- `tests/goal5066_aggregate_hierarchy_contract_test.py`

## Verification

Executed:

```text
py -m py_compile src/rtdsl/aggregate_hierarchy.py
```

Result: passed.

Executed:

```text
py -m unittest tests.goal5066_aggregate_hierarchy_contract_test
```

Result:

```text
Ran 6 tests in 0.004s
OK
```

Executed:

```text
py -m unittest tests.goal5063_rt_barneshut_paper_reproduction_scaffold_test tests.goal5066_aggregate_hierarchy_contract_test
```

Result:

```text
Ran 31 tests in 3.100s
OK
```

The local Python runtime still prints `Could not find platform independent libraries <prefix>` before test output. The tests completed successfully despite that environment warning.

## What This Does Not Prove

- It does not prove a native 3D aggregate traversal backend.
- It does not prove device-resident hierarchy traversal.
- It does not prove RT-BarnesHut whole-program reproduction.
- It does not prove paper-scale benchmark parity.
- It does not prove a speedup.
- It does not migrate `goal2547_barnes_hut_3d_scalar_subtree_kernel.py` onto this API.

## Next Logical Goal

The next goal can be `Goal5067`: build an app-owned RT-BarnesHut adapter that maps the author prepared-state dump into `AggregateHierarchy3D` and reports any schema gap, without changing the backend or claiming performance.
