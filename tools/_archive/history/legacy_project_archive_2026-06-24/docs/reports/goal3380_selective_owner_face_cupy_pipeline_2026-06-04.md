# Goal3380: Selective Owner-Face CuPy Pipeline

Date: 2026-06-04

## Status

Goal3378 showed that filtering every candidate row through a broad owner-face policy is too aggressive. Goal3380 adds a narrower generic continuation helper:

- `run_selective_closed_shape_owner_face_priority_membership_pipeline_cupy(...)`

The caller supplies `selected_point_ids` as the explicit ambiguity set. Only candidates for those points run through owner-face selection/filtering. Candidates for all other points pass through unchanged with `owner_face_id = -1`.

## Boundary

This helper does not infer which points are ambiguous. That remains caller/data policy.

This does not authorize release, public speedup, RayJoin paper reproduction, RTDL-beats-RayJoin, broad RT-core speedup, true-zero-copy, or native default route claims.

## Why This Helps

Goal3376 proved that the owner-face CuPy continuation fixes the known seven boundary-extra points when applied selectively. Goal3378 proved that applying a naive policy to all points breaks exactness. Goal3380 preserves the useful part as a reusable primitive:

- live candidate rows can pass through unchanged by default;
- an explicit ambiguity set can be reconciled through owner-face filtering;
- the engine remains app-agnostic because the ambiguity-set decision stays outside native code.

## Validation

The focused test validates:

- selected candidates are filtered by explicit owner-face selection;
- unselected candidates pass through unchanged;
- pass-through rows use `owner_face_id = -1`;
- the priority pipeline contract lists the selective helper;
- claim and default-route boundaries remain blocked.

