# Handoff: Claude Review Goal3447 Shape-Pair Active Relation Device Columns

Please review Goal3447 on current `main`.

## Required Output

Write your review to:

`docs/reviews/goal3448_claude_review_goal3447_shape_pair_relation_device_columns_2026-06-05.md`

Use one verdict only: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

## Scope

Goal3447 adds a generic resident relation-column stream for prepared OptiX shape-pair relation flags:

- Native ABI:
  - `RtdlNativeShapePairRelationDeviceColumns`
  - `rtdl_optix_prepared_shape_pair_relation_active_device_columns`
  - `rtdl_optix_release_shape_pair_relation_active_device_columns`
  - `shape_pair_relation_active_relation_device_columns_kernel`
- Python runtime:
  - `OptixShapePairRelationDeviceColumnOutput`
  - `PreparedOptixShapePairRelation.active_relation_device_columns(...)`
  - generic schema `shape_pair_relation_flags_2d_device_columns`
- App layer:
  - `PreparedRayJoinOptixShapePairActiveCount.active_relation_device_columns(...)`
  - `run_packed_left_active_relation_device_columns(...)`
- Evidence:
  - `docs/reports/goal3447_shape_pair_active_relation_device_columns_2026-06-05.md`
  - `docs/reports/goal3447_shape_pair_active_relation_device_columns_pod_2026-06-05.json`
  - `docs/reports/goal3447_shape_pair_active_relation_device_columns_pod_2026-06-05.stdout`
  - `tests/goal3447_shape_pair_active_relation_device_columns_test.py`

## Review Questions

1. Does the native OptiX implementation remain app-agnostic, or does it leak RayJoin/CDB/overlay app behavior into the engine?
2. Is the new typed-stream schema generic and reusable, not a RayJoin-only API under another name?
3. Is the fail-closed capacity behavior correct and sufficiently visible to users/reviewers?
4. Does the Python lifetime/owner handling look safe enough for CuPy partner use, given that true-zero-copy release wording remains explicitly unauthorized?
5. Does the pod evidence prove the intended narrow claim: host active count equals scalar device active count equals resident relation-column row count, with CuPy wrapping available?
6. What still remains before full RayJoin overlay relation-row or richer grouped continuation can be claimed?

## Boundaries To Enforce

Do not authorize release, broad speedup wording, RTDL-beats-RayJoin wording, RayJoin paper reproduction wording, true-zero-copy wording, or full overlay relation-row completion. If accepted, this goal should be framed as a generic runtime primitive that narrows the RayJoin overlay gap.
