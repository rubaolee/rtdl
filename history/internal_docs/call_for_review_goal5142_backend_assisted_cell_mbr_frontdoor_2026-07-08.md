# Call For Review - Goal5142 Backend-Assisted Cell-MBR Front Door

Please strictly review Goal5142.

## Files To Review

```text
src/rtdsl/partner_continuations.py
src/rtdsl/__init__.py
tests/goal5142_generic_cell_mbr_backend_assisted_frontdoor_test.py
history/internal_docs/goal5142_backend_assisted_cell_mbr_frontdoor_result_2026-07-08.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5142_backend_assisted_cell_mbr_frontdoor_2026-07-08.json
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
Paper-reproduction-apps/x-hd-paper/data/manifest.json
```

## Context

Goal5140 specified the generic native ABI for cell-MBR nearest frontiers but did
not implement a backend. Goal5141 audited existing native assets and concluded
that a true OptiX native symbol is still missing.

Goal5142 implements a narrower executable front door:

```text
generic 2-D AABB membership backend
-> exact point-to-cell-MBR distance filter
-> generic nearest-state split
-> Goal5140 row table
```

The route can request `backend="optix"` on a POD, but local validation used the
CPU backend. It is not a complete native backend.

## Questions

1. Does the new API remain app-neutral and avoid X-HD/Hausdorff/paper/author
   identity in the generic source window?
2. Does it correctly connect generic AABB membership rows to the Goal5140 row
   table without changing the native ABI?
3. Do the tests prove row-table equality against the Goal5140 NumPy reference?
4. Do the tests prove that expanded-AABB broadphase false positives are filtered
   by exact point-to-MBR distance before frontier classification?
5. Does row-capacity overflow fail closed without returning partial success?
6. Does `plan_cell_mbr_traversal_lowering` correctly distinguish:
   - executable NumPy reference;
   - executable 2-D AABB-membership-assisted route;
   - non-executable native/OptiX ABI-only route?
7. Does the report correctly avoid claiming a complete native backend, 3-D
   backend, X-HD performance improvement, or author parity?
8. Is Goal5143 correctly scoped as POD OptiX validation plus a decision gate,
   rather than a paper-performance goal?

## Expected Verdict Labels

Approve:

```text
approve_goal5142_backend_assisted_cell_mbr_frontdoor__pod_optix_gate_next
```

Require revision:

```text
revise_goal5142_before_pod_optix_gate
```

Block:

```text
block_goal5142_due_to_native_backend_overclaim_or_app_identity_leak
```
