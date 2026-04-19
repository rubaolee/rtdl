# Goal604 External Review: Apple RT 2D Ray/Triangle Hit-Count Native

Date: 2026-04-19
Reviewer: external (Claude Sonnet 4.6)
Verdict: **ACCEPT**

---

## Scope Check

Goal604 claims one thing: extend `ray_triangle_hit_count` from 3D-only Apple MPS
execution to also cover `Ray2D/Triangle2D` via a prism lowering.  No unrelated
geometry, nearest-neighbor, graph, or DB predicates are touched.  The claim is
narrow and accurate.

---

## Native Function (`rtdl_apple_rt_run_ray_hitcount_2d`)

**Prism geometry (mm:917–953)**

Each 2D triangle is lifted into 8 MPS triangles — two z-caps at z=−1 / z=+1 and
three pairs of rectangular side faces (each rect split into two triangles).  The
tessellation is complete: cap-face + all three lateral walls are present.  No face
is missing, so a ray that enters the prism from any direction will intersect at
least one MPS triangle.

**Ray mapping (mm:866–876)**

```
origin    = (ox, oy, −1.0)
direction = (dx·tmax, dy·tmax, 2.0)
maxDist   = 1.000001f
```

At parameter t = 0 the 3D ray is at the start of the 2D segment; at t ≈ 1 it is
at the end.  The z-component sweeps from −1 to +1, covering the full prism
height.  The slight over-extension (1.000001) guards against float boundary
rejection at t = 1.0 exactly.

**Containment** (`ray_hits_triangle_2d`, mm:208–220) checks whether the ray
origin or endpoint lies inside the triangle before testing edge intersections.
When the 3D ray's origin is already inside the prism, MPS still delivers a hit
(the ray starts inside the acceleration structure and the prism walls are
double-sided due to `cullMode = MTLCullModeNone`), so those cases are correctly
passed to exact refinement.

**Exact refinement gate (mm:1017–1025)**

A candidate returned by MPS increments the count only after `ray_hits_triangle_2d`
returns true.  This means MPS false-positives (geometry adjacent to the prism that
clips the bounding box but not the actual triangle edge) are rejected before
count accumulation.  CPU work is bounded to MPS candidates, satisfying the
Goal602/603 hardware-backed definition.

**Mask-and-advance loop (mm:984–1036)**

Mirrors the proven 3D pattern: chunk of 32 triangles, `MPSIntersectionTypeNearest`
per pass, bit-clear after each candidate is processed, early exit when no active
masks remain.  Functionally identical structure to the 3D hit-count loop; no new
loop-logic risk is introduced.

---

## Python Dispatch (`apple_rt_runtime.py`)

`ray_triangle_hit_count_apple_rt` (py:540–597) detects all-Ray2D + all-Triangle2D
and routes to the 2D native path; otherwise falls through to 3D.  The mixed-type
guard (py:571–574) raises `ValueError` for incoherent inputs.

`run_apple_rt` (py:661–668) correctly dispatches the 2D kernel branch through the
native path.  `native_only=True` no longer raises for 2D inputs, which is the
intended Goal604 outcome.

`_APPLE_RT_SUPPORT_NOTES` (py:58–65) correctly reports
`native_candidate_discovery = "shape_dependent"` and
`native_shapes = ("Ray2D/Triangle2D", "Ray3D/Triangle3D")`.

**Minor nit — stale mode label (py:607–608)**

`apple_rt_predicate_mode("ray_triangle_hit_count")` still returns
`"native_mps_rt_3d_else_cpu_reference_compat"`.  The 2D path is now also native,
so this string is misleading (though it does not affect dispatch correctness).
Suggest updating to `"native_mps_rt_2d_and_3d"` in a follow-up; it is not a
blocker for this goal.

---

## Test Coverage (`goal604_apple_rt_ray_hitcount_2d_native_test.py`)

| Test | What it exercises |
| --- | --- |
| `test_run_apple_rt_2d_hitcount_native_only_matches_cpu` | `native_only=True` kernel dispatch; CPU oracle parity |
| `test_direct_2d_hitcount_helper_matches_cpu` | Direct helper bypass; same oracle parity |

The fixture covers: a ray that crosses two distinct triangles, a ray whose origin
is inside a triangle (containment case), a ray entirely outside all triangles,
and a short-range ray near a triangle that should miss.  Oracle comparison via
`run_cpu_python_reference` provides ground truth.

---

## Honesty Boundary

The report states this is a correctness-first step, not a speedup claim, and
defers performance characterisation to a later v0.9.3 full-surface goal.  The
code is consistent with that framing: MPS calls are synchronous
(`waitUntilCompleted`), scalar around the GPU, and no throughput numbers are
published.

---

## Summary

The implementation is geometrically correct, the candidate/refinement split is
genuine, dispatch is accurate, and the scope is confined to the claimed predicate
and shapes.  The stale `apple_rt_predicate_mode` label string is the only
finding, and it is cosmetic.

**ACCEPT.**
