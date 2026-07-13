# Call For Review - Goal5146 Native 3-D AABB Point-Membership Row Producer

Please strictly review Goal5146.

## Files To Review

```text
src/native/optix/rtdl_optix_prelude.h
src/native/optix/rtdl_optix_core.cpp
src/native/optix/rtdl_optix_workloads.cpp
src/native/optix/rtdl_optix_api.cpp
src/rtdsl/optix_runtime.py
src/rtdsl/__init__.py
tests/goal5146_optix_aabb_index_3d_point_membership_test.py
Paper-reproduction-apps/x-hd-paper/scripts/run_aabb_index_3d_point_membership_gate.py
Paper-reproduction-apps/x-hd-paper/results/aabb_index_3d_point_membership_gate_pod.json
history/internal_docs/goal5146_native_3d_aabb_point_membership_result_2026-07-08.md
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
Paper-reproduction-apps/x-hd-paper/data/manifest.json
```

## Context

Goal5145 added a dimension-generic NumPy oracle for 2-D/3-D cell-MBR frontier
row tables. Goal5146 is the first native 3-D broadphase brick on that path: it
adds a generic OptiX 3-D AABB point-membership row producer returning
`{query_id, indexed_id}` rows.

This is intentionally narrower than a complete native Goal5140 cell-MBR
nearest-frontier backend.

## Review Questions

1. Are the new native symbols app-neutral (`aabb_index_3d` / point membership)
   rather than X-HD / Hausdorff / paper-specific?
2. Does the Python wrapper expose a generic 3-D AABB route and preserve object
   lifetimes safely through prepare/collect/destroy?
3. Does `pack_aabbs_3d` validate bounds and preserve all 3-D fields correctly?
4. Does the POD evidence prove a real OptiX run, not a CPU fallback?
5. Are the observed rows exactly equal to the expected overlapping-box fixture
   rows, including the multi-box point?
6. Does the implementation preserve fail-closed capacity behavior and sorted /
   deduplicated row semantics?
7. Does the result avoid overclaiming a complete Goal5140 native backend,
   X-HD RT-core reproduction, X-HD performance, or full paper reproduction?
8. Is this the right native 3-D broadphase brick before attempting a full
   cell-MBR nearest-frontier backend?

## Expected Verdict Labels

Approve:

```text
approve_goal5146_native_3d_aabb_point_membership_broadphase
```

Require revision:

```text
revise_goal5146_aabb3d_contract_or_claim_boundary
```

Block:

```text
block_goal5146_due_to_app_specific_or_unverified_native_backend
```
