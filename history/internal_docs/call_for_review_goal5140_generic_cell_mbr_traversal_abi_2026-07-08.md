# Call For Review - Goal5140 Generic Cell-MBR Traversal ABI

Please strictly review Goal5140.

## Files Under Review

```text
history/internal_docs/goal5140_generic_cell_mbr_traversal_abi_result_2026-07-08.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5140_generic_cell_mbr_traversal_abi_contract_2026-07-08.json
src/rtdsl/partner_continuations.py
src/rtdsl/__init__.py
tests/goal5140_generic_cell_mbr_traversal_abi_test.py
```

## Context

Goal5138 added generic point-grid cell-MBR descriptors and radius cell
candidates. Goal5139 added generic nearest-state frontier splitting. Goal5140
now specifies the native/RT ABI row schema for that frontier.

This is not a backend implementation. It is a contract and row-table adapter.

## Review Questions

1. Is the `generic_cell_mbr_nearest_frontier_native_abi_v1` ABI app-neutral?
2. Does the ABI correctly point to the Goal5139 reference contract
   (`generic_nearest_state_cell_frontier`) and row-table contract
   (`generic_cell_mbr_nearest_frontier_row_table`)?
3. Is the row schema sufficient for a future native traversal backend:
   frontier kind, query id, cell id, point span/count, min/max distance?
4. Is the `fail_closed_no_partial_rows` overflow policy appropriate and clearly
   specified?
5. Does `plan_cell_mbr_traversal_lowering` correctly distinguish executable
   NumPy reference from non-executable native/OptiX backend status?
6. Does the implementation avoid app/paper/author identity leaks in the generic
   ABI surface?
7. Does the result correctly avoid claiming native backend execution, shader
   payload implementation, performance, or paper figure reproduction?
8. Is the recommended next goal correct: a bounded generic backend feasibility
   spike, not an application-specific implementation?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve | approve_with_required_amendments | revise | block

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to review questions:
1. ...
2. ...
...
8. ...
```

## Requested Verdict Label

If approved:

```text
approve_goal5140_generic_cell_mbr_traversal_native_abi
```
