# Goal 638 Claude Review — Embree Native Early-Exit Any-Hit

Date: 2026-04-19
Reviewer: Claude Sonnet 4.6

## Verdict: ACCEPT

## Findings

### C ABI (`rtdl_embree_prelude.h`)
`RtdlRayAnyHitRow { ray_id, any_hit }` is present. Both `rtdl_embree_run_ray_anyhit` (2D) and `rtdl_embree_run_ray_anyhit_3d` (3D) are declared correctly and match their implementations.

### Occluded callbacks (`rtdl_embree_scene.cpp`)
`triangle_occluded` and `triangle_occluded_3d` correctly:
- Guard on `QueryKind::kRayAnyHit` before touching state.
- Perform the exact `finite_ray_hits_triangle` / `finite_ray_hits_triangle_3d` intersection test (same geometry math used by the hit-count path).
- Set `*state->any_hit = 1u` and `ray->tfar = -std::numeric_limits<float>::infinity()` — the documented Embree early-exit convention for `rtcOccluded1`.

### API functions (`rtdl_embree_api.cpp`)
Both 2D and 3D functions:
- Register `triangle_occluded` / `triangle_occluded_3d` via `rtcSetGeometryOccludedFunction` (not intersect — correct for occlusion).
- Invoke `rtcOccluded1` (correct API).
- Set and clear `g_query_kind` / `g_query_state` per ray; no state leak across calls.

### Python runtime (`embree_runtime.py`)
- Optional symbol loading via `_require_optional_embree_symbol` at `prepare_embree` time (lines 2862–2888) — stale libraries load without error.
- Dictionary mode: falls back to hit-count projection (`_project_ray_hitcount_view_to_anyhit`) when native symbols absent; uses native path when present.
- Raw row-view mode: requires native symbols and returns `("ray_id", "any_hit")` field names — consistent with stated design.
- `_call_ray_anyhit_embree_packed` correctly dispatches 2D vs 3D by checking ray/triangle layout dimension.

### Tests (`goal638_embree_native_any_hit_test.py`)
- 2D test validates `run_embree` output against `run_cpu` oracle and separately verifies raw row-view field names and content.
- 3D test validates against CPU oracle.
- Both guarded with `skipUnless(embree_version)` — clean skip on platforms without Embree.

### No blocking issues
The implementation is narrow in scope (two new exported functions, two occluded callbacks, Python plumbing), the early-exit mechanism matches the Embree specification, and the test suite covers both dimensions with CPU cross-validation.
