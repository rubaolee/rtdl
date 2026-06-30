# Goal 638: v0.9.5 Embree Native Early-Exit Any-Hit

Date: 2026-04-19

## Goal

Add an Embree-native `ray_triangle_any_hit` path after the OptiX-native Goal637
closure.

## Reason

Under the engine implementation priority policy, Embree is second priority
after OptiX. Goal636 provided correctness-compatible backend dispatch by
projecting hit-count rows. Goal638 replaces that path for Embree with Embree's
native occlusion traversal API.

## Implementation

- Added `RtdlRayAnyHitRow { ray_id, any_hit }` to the Embree C ABI.
- Added native Embree C ABI functions:
  - `rtdl_embree_run_ray_anyhit`
  - `rtdl_embree_run_ray_anyhit_3d`
- Added 2-D and 3-D user-geometry occlusion callbacks:
  - `triangle_occluded`
  - `triangle_occluded_3d`
- The native path uses `rtcOccluded1` and sets `ray.tfar = -infinity` after the
  first accepted triangle hit, which is Embree's occlusion/any-hit early-exit
  convention.
- Python `run_embree` / `prepare_embree` now use the native any-hit symbols when
  present and retain dictionary-mode fallback to hit-count projection for stale
  libraries.
- Raw Embree row-view mode now requires the native symbols and returns
  `("ray_id", "any_hit")`.

## Non-Scope

- HIPRT, Vulkan, and Apple RT remain compatibility paths for this predicate.
- No broad speedup claim is made.

## Validation

Local macOS after Embree rebuild:

```text
make build-embree
Embree 4.4.0
```

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal638_embree_native_any_hit_test \
  tests.goal636_backend_any_hit_dispatch_test -v

Ran 9 tests in 0.029s
OK (skipped=3)
```

Linux validation on `lestat-lx1`:

```text
RTDL_FORCE_EMBREE_REBUILD=1 PYTHONPATH=src:. python3 -c \
  "import rtdsl as rt; print('Embree', '.'.join(map(str, rt.embree_version())))"

Embree 4.3.0

PYTHONPATH=src:. python3 -m unittest \
  tests.goal638_embree_native_any_hit_test \
  tests.goal636_backend_any_hit_dispatch_test -v

Ran 9 tests in 4.926s
OK (skipped=5)
```

## Verdict

Codex verdict: ACCEPT for the Embree-native early-exit slice.

External consensus:

- Gemini Flash review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal638_gemini_flash_review_2026-04-19.md`
  - Verdict: ACCEPT
  - Note: the review says "other backends" while listing OptiX; the intended
    boundary after Goal637/Goal638 is OptiX and Embree native, with HIPRT,
    Vulkan, and Apple RT still compatibility paths.
- Claude review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal638_claude_review_2026-04-19.md`
  - Verdict: ACCEPT

Goal638 closure status: ACCEPTED with 3-AI consensus.
