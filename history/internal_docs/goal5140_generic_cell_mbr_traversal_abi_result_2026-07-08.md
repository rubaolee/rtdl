# Goal5140 - Generic Cell-MBR Traversal ABI Result

## Verdict

`generic_cell_mbr_traversal_native_abi_specified_no_backend`

## Why This Goal Exists

Goals5138-5139 created reference/front-door contracts for:

```text
point columns
-> grid cell descriptors
-> radius cell candidates
-> nearest-state inline/offload/pruned frontiers
```

The next step is to define the native/RT-facing ABI that can eventually produce
the same frontier rows from a traversal backend. Goal5140 specifies that ABI and
adds a reference row-table adapter. It does not implement an OptiX/Embree/HIPRT
backend.

## Implemented Public API

New public symbols:

```python
CELL_MBR_FRONTIER_KIND_CODES
CELL_MBR_TRAVERSAL_NATIVE_ABI_CONTRACT
CELL_MBR_TRAVERSAL_ROW_SCHEMA
cell_mbr_frontiers_to_row_table_numpy_columns
cell_mbr_traversal_native_abi_contract
validate_cell_mbr_traversal_native_abi_contract
plan_cell_mbr_traversal_lowering
```

## Native ABI Contract

Contract:

```text
generic_cell_mbr_nearest_frontier_native_abi_v1
```

Reference contracts:

```text
python_reference_contract = generic_nearest_state_cell_frontier
row_table_reference_contract = generic_cell_mbr_nearest_frontier_row_table
```

Status:

```text
specified_native_abi_no_backend_implementation
executable = false
app_generic = true
```

Frontier kind codes:

```text
1 = inline
2 = offload
3 = pruned
```

Row schema:

```text
frontier_kind_code
query_row_id
query_point_id
cell_id
point_begin_offset
point_count
min_distance
max_distance
```

Overflow policy:

```text
fail_closed_no_partial_rows
```

If a future native backend overflows row capacity, it must set overflow and
surface no partial rows as a valid result.

## Reference Row-Table Adapter

`cell_mbr_frontiers_to_row_table_numpy_columns(...)` flattens the Goal5139
reference output:

```text
inline_frontier + offload_frontier + pruned_frontier
```

into one ABI-shaped column table with `frontier_kind_codes`.

This gives future native backends an exact row shape to match.

## Test Evidence

Command:

```text
py -m unittest tests.goal5140_generic_cell_mbr_traversal_abi_test tests.goal5139_generic_nearest_state_frontier_api_test tests.goal5138_generic_grid_cell_candidate_api_test
```

Result:

```text
Ran 11 tests in 1.039s
OK
```

The tests verify:

1. `validate_cell_mbr_traversal_native_abi_contract()` returns an app-neutral,
   non-executable ABI contract;
2. the ABI row schema matches the row-table adapter;
3. `plan_cell_mbr_traversal_lowering("numpy")` is executable reference;
4. `plan_cell_mbr_traversal_lowering("optix")` is explicitly non-executable
   until a backend exists;
5. the generic ABI source window contains no app/paper/author identity tokens.

Machine-readable contract:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5140_generic_cell_mbr_traversal_abi_contract_2026-07-08.json
```

## What This Proves

Goal5140 proves that the native handoff target for the scalable route is no
longer vague. The backend contract is explicit:

```text
query points + cell MBR descriptors + nearest state
-> ABI row table of inline/offload/pruned cell work
```

## What This Does Not Prove

This does not prove:

- OptiX/Embree/HIPRT backend implementation;
- shader payload nearest state;
- heavy-cell CUDA continuation;
- radius-growth loop;
- paper figure reproduction;
- performance or parity.

## Architectural Position

The current system ladder is:

```text
Goal5138: point grid + radius cell candidates
Goal5139: nearest-state frontier split
Goal5140: native/RT ABI row schema for that frontier
```

This is the correct precondition before writing any backend code. Without this
ABI, backend work would be tempted to hardcode the application route.

## Recommended Next Goal

```text
Goal5141 - Generic cell-MBR traversal backend feasibility spike
```

The feasibility spike should choose one backend target, likely OptiX first, and
answer whether the ABI can be implemented without app identity or copied author
code. It should remain a bounded backend spike, not a full paper-performance
claim.
