# Call For Review - Goal5139 Generic Nearest-State Frontier

Please strictly review Goal5139.

## Files Under Review

```text
history/internal_docs/goal5139_generic_nearest_state_frontier_result_2026-07-08.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5139_generic_nearest_state_frontier_contract_2026-07-08.json
src/rtdsl/partner_continuations.py
src/rtdsl/__init__.py
tests/goal5139_generic_nearest_state_frontier_api_test.py
```

## Context

Goal5138 implemented generic point-grid tight cell-MBR descriptors and radius
cell-MBR candidate rows. Goal5139 builds the next generic reference contract:

```text
cell candidates + current nearest state
-> inline frontier
-> offload frontier
-> pruned frontier
```

This is a NumPy reference/front-door contract. It is not an OptiX/native
backend and it is not the X-HD scalable route yet.

## Review Questions

1. Is `nearest_state_frontier_from_cell_candidates_numpy_columns` an app-neutral
   API name and contract?
2. Does the implementation avoid X-HD, Hausdorff, paper, author, or `hd_exec`
   semantics in the generic API window?
3. Does the test use a non-X-HD consumer scenario and prove all three categories
   (`inline_frontier`, `offload_frontier`, `pruned_frontier`) are behaviorally
   exercised?
4. Are the prune/offload rules stated clearly and implemented consistently?
5. Is the frontier row schema sufficient as the next handoff contract after
   Goal5138: query ids, cell ids, point spans/counts, min/max distances?
6. Does the result correctly avoid claiming native/OptiX execution, payload
   shader implementation, heavy-cell CUDA offload, X-HD performance, or paper
   figure reproduction?
7. Is it acceptable that this is a NumPy reference/front-door contract before a
   device/RT backend exists?
8. Is the recommended next goal correct: generic RT cell-MBR traversal ABI
   design, rather than app-specific X-HD implementation or larger exact pairwise
   scaling?

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
approve_goal5139_generic_nearest_state_frontier_reference
```
