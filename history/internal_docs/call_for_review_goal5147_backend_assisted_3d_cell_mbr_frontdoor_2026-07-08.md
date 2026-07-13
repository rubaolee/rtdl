# Call For Review - Goal5147 Backend-Assisted 3-D Cell-MBR Front Door

Please strictly review Goal5147.

## Files To Review

```text
src/rtdsl/partner_continuations.py
src/rtdsl/__init__.py
tests/goal5147_backend_assisted_3d_cell_mbr_frontdoor_test.py
Paper-reproduction-apps/x-hd-paper/scripts/run_cell_mbr_backend_assisted_3d_gate.py
Paper-reproduction-apps/x-hd-paper/results/backend_assisted_3d_cell_mbr_gate_cpu.json
Paper-reproduction-apps/x-hd-paper/results/backend_assisted_3d_cell_mbr_gate_pod_optix.json
history/internal_docs/goal5147_backend_assisted_3d_cell_mbr_frontdoor_result_2026-07-08.md
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
Paper-reproduction-apps/x-hd-paper/data/manifest.json
```

## Context

Goal5146 added a native OptiX 3-D AABB point-membership row producer. Goal5147
connects that native broadphase brick to the existing generic exact
point-to-cell-MBR distance filter, nearest-state frontier split, and Goal5140
row-table adapter.

This is a backend-assisted front door:

```text
3-D AABB broadphase rows from CPU/OptiX
-> generic NumPy exact filter/frontier classification
-> Goal5140 row table
```

It is not a complete native Goal5140 backend.

## Review Questions

1. Does `cell_mbr_nearest_frontier_aabb_membership_3d_numpy_columns` compose
   app-neutral broadphase rows with generic exact filtering and frontier
   lowering, rather than adding X-HD-specific logic?
2. Does the CPU gate prove row-table equality against the Goal5145
   dimension-generic oracle?
3. Does the POD OptiX gate actually use the native generic symbol
   `rtdl_optix_collect_prepared_aabb_index_3d_point_contains_rows`?
4. Do the CPU and OptiX gates produce the same Goal5140 row-table columns?
5. Does the exact filter remove expanded-AABB false positives?
6. Does overflow fail closed, without returning partial row-table results?
7. Is the public surface free of X-HD / Hausdorff / paper / author vocabulary?
8. Does the result avoid overclaiming complete native backend status, X-HD
   RT-core reproduction, X-HD performance, or full paper reproduction?
9. Is this a meaningful step toward the native 3-D cell-MBR backend while still
   honestly preserving the remaining in-traversal fusion gap?

## Expected Verdict Labels

Approve:

```text
approve_goal5147_backend_assisted_3d_cell_mbr_frontdoor
```

Require revision:

```text
revise_goal5147_backend_assisted_3d_contract_or_claim_boundary
```

Block:

```text
block_goal5147_due_to_app_specific_or_false_native_backend_claim
```
