# Goal583 External Review — Claude (claude-sonnet-4-6)

Date: 2026-04-18

## Verdict: ACCEPT

---

## Review Scope

- Is the `ray_triangle_hit_count` path genuinely native Apple MPS RT?
- Is the implementation correct?
- Is the documentation honest about scope and limitations?

---

## Native MPS RT — PASS

`rtdl_apple_rt_run_ray_hitcount_3d` (`src/native/rtdl_apple_rt.mm` lines 265–407) is
unambiguously real Metal/MPS GPU code. It:

- Creates an `MPSRayIntersector` with `MTLCreateSystemDefaultDevice`.
- For each triangle, builds a one-triangle `MPSTriangleAccelerationStructure` and calls
  `[accel rebuild]`.
- Encodes `MPSIntersectionTypeAny` into a `MTLCommandBuffer`, commits, and
  `waitUntilCompleted`.
- Reads `MPSIntersectionDistance.distance >= 0` as a hit indicator per ray.

This is not a CPU stub or a compile-time conditional around a no-op. Every GPU API call
is real.

---

## Correctness Design — PASS

MPS exposes nearest-hit and any-hit queries but has no "all-hits" or "count-hits" output
type. The per-triangle loop with `MPSIntersectionTypeAny` correctly avoids the
same-distance undercounting that would arise from a single `MPSIntersectionTypeNearest`
pass over all triangles. The design is correctness-oriented; the report correctly
identifies it as not the final throughput design.

Zero-hit rays are included in the output (all `ray_count` rows are always written), which
matches the `ray_triangle_hit_count` contract.

---

## Python Binding — PASS

`ray_triangle_hit_count_apple_rt` (`src/rtdsl/apple_rt_runtime.py` lines 281–312) maps
the C ABI correctly: argument types and result struct layout (`_RtdlRayHitCountRow`)
match the native struct `RtdlRayHitCountRow` in `.mm`.

`run_apple_rt` routes 3D hit-count to native at lines 371–374 before the `native_only`
guard, so `native_only=True` works as documented.

---

## Test Coverage — PASS

`test_ray_triangle_hit_count_native_matches_cpu_reference`
(`tests/goal578_apple_rt_backend_test.py` line 80) exercises:

- `run_apple_rt(native_only=True, ...)` matching CPU reference (3 rays, 2 triangles,
  including a ray that misses both triangles and a ray with a tmax that cuts off one hit).
- Direct `ray_triangle_hit_count_apple_rt(...)` helper matching CPU reference.

`test_native_only_rejects_compatibility_paths` confirms 2D hit-count is correctly refused
under `native_only=True`.

All 239 tests pass per the report.

---

## Honesty / Documentation — PASS

The report, `apple_rt_predicate_mode`, and `apple_rt_support_matrix` accurately describe
the coverage split:

- Native MPS RT: 3D `ray_triangle_closest_hit`, 3D `ray_triangle_hit_count`.
- CPU-reference compat: all other 16 predicates.

The honesty boundary section explicitly lists which public claims are true and which are
false. No overclaiming was found in the report or in the Python API docstrings.

---

## Minor Issues (non-blocking)

1. **Stale error message** — `run_apple_rt` line 375–379 still says "currently supports
   only 3D ray_triangle_closest_hit" in the `native_only` rejection message, which is
   now inaccurate since 3D hit-count is also native. The error fires only for predicates
   that are not in either native branch, so it does not affect correctness, but it will
   confuse a developer who hits it after Goal583. Recommend updating the message in a
   follow-up.

2. **Performance** — the per-triangle rebuild loop is O(T) command-buffer round-trips.
   This is correctly documented as a correctness-first design, not the final throughput
   path. No action required for this goal.

---

## Summary

The 3D `ray_triangle_hit_count` path is genuinely native Apple MPS RT, correctly
implemented, well-tested, and honestly documented. Accept as the second native MPS RT
primitive; does not constitute full native Apple RT parity.
