# Goal651 Claude Review — Apple RT 3D Any-Hit Native-Assisted Path

Date: 2026-04-20 (re-reviewed post-cleanup patch: 2026-04-20)
Reviewer: Claude Sonnet 4.6  
Verdict: **ACCEPT**

---

## Evidence

### Correctness — Native Function

`rtdl_apple_rt_run_ray_anyhit_3d` (mps_geometry.mm:262–419) is correctly
implemented:

- Builds `MPSTriangleAccelerationStructure` from caller-supplied triangles.
- Runs `MPSIntersectionTypeNearest` — one pass, one result per ray.
- Maps `distance >= 0 && primitive_index < triangle_count` to `any_hit = 1`;
  otherwise `any_hit = 0`. Nearest-intersection existence is a correct proxy for
  any-hit truth.
- Invalid rays (zero direction, non-finite components) are submitted with
  INFINITY origin / negative maxDistance; MPS returns distance < 0, so they
  correctly yield `any_hit = 0`.
- Zero-ray or zero-triangle short-circuit paths are both handled without
  entering the Metal path.

### Correctness — Python Dispatch

`ray_triangle_any_hit_apple_rt` (apple_rt_runtime.py:1311–1358) dispatches
correctly:

- 3D all-input case: uses `rtdl_apple_rt_run_ray_anyhit_3d` when the loaded
  library exports it; stale/non-exporting libs fall through to projection.
- 2D or mixed case: falls through to `ray_triangle_hit_count_apple_rt` +
  `hit_count > 0` projection. This is the existing compatibility path and the
  behavior is unchanged.
- `AppleRtRowView.close()` frees the malloc'd rows via
  `rtdl_apple_rt_free_rows`. The `try/finally` block in both the native and
  fallback paths prevents leaks of Python-visible memory.

### Honest Scoping in Docs

`current_architecture.md:78–81` correctly states current main has "Apple MPS RT
3D any-hit based on nearest-intersection existence" while Apple RT 2D "is real
backend execution but not a native early-exit Apple 2D speedup claim."
`backend_maturity.md:52–53` echoes this split. The table cell at line 111
accurately describes the v0.9.5 *released tag* (compatibility dispatch) as
distinct from current-main behavior. No false performance claim is made.

### Test Coverage

`tests/goal651_apple_rt_3d_anyhit_native_test.py`:

- Symbol-presence assertion gates on the actual loaded library.
- `run_apple_rt(..., native_only=True)` 3D result is asserted equal to
  `run_cpu(...)` reference.
- Skip guard is correct: non-Darwin or missing symbol → test skips cleanly.

### Metal Object Lifecycle — Resolved by Cleanup Patch

The earlier review flagged that `new*`/`alloc-init` Metal objects were not
released under manual reference counting (no `-fobjc-arc`). The cleanup patch
addresses this: all seven Metal objects now carry an explicit `autorelease` call
inside the `@autoreleasepool` block (mps_geometry.mm:302, 307, 322–324, 330,
355–357, 363–365, 370). The `command_buffer` at line 381 is obtained via a
non-`new` factory method (`commandBuffer`) and is already implicitly autoreleased
per Cocoa convention. The pool drains on block exit (line 408), releasing all
objects correctly. No per-call Metal memory leak remains.

---

## Re-review Note (2026-04-20 — post-cleanup patch)

Re-examined `rtdl_apple_rt_run_ray_anyhit_3d` (mps_geometry.mm:262–419) and
`tests/goal651_apple_rt_3d_anyhit_native_test.py` after the Objective-C object
cleanup patch. All previously identified issues are resolved. No new concerns
introduced.

## Summary

Apple RT 3D any-hit is genuinely MPS RT-backed via nearest-intersection
existence. Apple RT 2D remains honestly scoped as compatibility dispatch.
Python fallback and memory management are correct. Metal object lifecycle is
clean after the cleanup patch. **ACCEPT.**
