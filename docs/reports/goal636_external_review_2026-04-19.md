# Goal 636: External Review — Backend Any-Hit Compatibility Dispatch

Date: 2026-04-19
Reviewer: Claude Sonnet 4.6 (external AI review)

## Verdict: ACCEPT

---

## Review Scope

The following were read for this review:

- `docs/reports/goal636_v0_9_5_backend_anyhit_compatibility_and_user_doubt_log_2026-04-19.md`
- `src/rtdsl/embree_runtime.py` (any-hit dispatch path)
- `src/rtdsl/optix_runtime.py` (any-hit dispatch path)
- `src/rtdsl/vulkan_runtime.py` (any-hit dispatch path)
- `src/rtdsl/hiprt_runtime.py` (any-hit dispatch path)
- `src/rtdsl/apple_rt_runtime.py` (any-hit dispatch path)
- `src/rtdsl/visibility_runtime.py` (full)
- `src/rtdsl/lowering.py` (ray_triangle_any_hit path)
- `tests/goal636_backend_any_hit_dispatch_test.py` (full)
- `docs/rtdl/dsl_reference.md` (any_hit section)

---

## Honesty Boundary Assessment

The primary review criterion is whether the backend hit-count projection is honestly
documented as compatibility rather than native early-exit performance. **It is.**

### Source code

Every backend uses an explicit projection function. The pattern is uniform:

```python
"any_hit": 1 if int(row["hit_count"]) else 0
```

- Embree: `_project_ray_hitcount_view_to_anyhit` — projects from `EmbreeRowView.hit_count`
- OptiX: `_project_ray_hitcount_view_to_anyhit` — projects from `OptixRowView.hit_count`
- Vulkan: `_project_ray_hitcount_view_to_anyhit` — projects from `VulkanRowView.hit_count`
- HIPRT: `_project_ray_hitcount_rows_to_anyhit` — wraps `ray_triangle_hit_count_{2d,3d}_hiprt`
- Apple RT: inline projection from `ray_triangle_hit_count_apple_rt`

The HIPRT compatibility notes field is explicit:
`"ray_triangle_any_hit": "Goal 636 hit-count projection for 2D/3D"`

The Apple RT predicate capability record states:
> "Uses the Apple Metal/MPS ray-triangle hit-count traversal and projects hit_count > 0
> to any_hit; this is backend-backed compatibility, not a specialized early-exit shader."

`raw_mode` is blocked with honest error messages across Embree, OptiX, and Vulkan:
> "raw mode is not supported for ray_triangle_any_hit while it is projected from the
> backend hit-count row view"

### Documentation

`docs/rtdl/dsl_reference.md` explicitly warns:
> "backend compatibility dispatch may implement this by running `ray_triangle_hit_count`
> and projecting `hit_count > 0`; that is backend execution, but not a native early-exit
> performance claim"

`visibility_runtime.py` docstring states:
> "Non-CPU backends currently execute `ray_triangle_any_hit` through the backend
> compatibility dispatch. That proves backend execution and row parity; it is not a
> native early-exit performance claim."

### Tests

Test names use the word "compatibility_dispatch" explicitly:
- `test_embree_any_hit_matches_cpu_and_rejects_raw_mode`
- `test_visibility_rows_can_use_embree_backend_compatibility_dispatch`
- `test_visibility_rows_can_use_apple_rt_backend_compatibility_dispatch`

Tests assert correctness against CPU reference only — no performance assertions exist.

### User Doubt

The user's challenge ("You are just using existing way to know the hit count, then judge
it is >0 or not?") is correct and is recorded in the goal report. The implementation is
exactly that. No attempt was made to obscure or re-frame it.

---

## Test Evidence

Local Mac (5 tests, OK, skipped=3 — OptiX/Vulkan/HIPRT absent):
- Embree and Apple RT any-hit compatibility dispatch match CPU.
- `visibility_rows(backend="embree")` and `visibility_rows(backend="apple_rt",
  native_only=True)` match CPU.

Linux lestat-lx1 / GTX 1070 (7 tests, OK, skipped=2 — Apple RT absent):
- Embree, OptiX, Vulkan, HIPRT any-hit compatibility dispatch each match CPU.
- Combined v0.9.5 suite (Goals 632+633+636): 16 tests, OK, skipped=2.

---

## What Goal 636 Is and Is Not

**Is:** Backend dispatcher surface compatibility for `ray_triangle_any_hit` across all 5
RTDL backends, proven correct against CPU reference, with a correctness gate for future
native early-exit work.

**Is not:** Native early-exit any-hit traversal. No backend-specific first-hit shader or
kernel termination is implemented. There is no performance benefit over
`ray_triangle_hit_count` on the same backend.

**Next step correctly deferred:** Goal 637 (native early-exit any-hit kernels) is the
appropriate place for backend-specific first-hit termination and performance comparison.

---

## Issues Found

None that require blocking. The honesty boundary is enforced at every layer: source code
projections, raw-mode guards, capability notes, API docstrings, DSL reference
documentation, and test naming. No overclaim was found anywhere.

---

## Conclusion

Goal 636 closes the stated criteria:

1. Docs clearly distinguish compatibility projection from real early-exit — **confirmed**.
2. At least one external AI review accepts the honesty boundary — **this review**.

**ACCEPT.**
