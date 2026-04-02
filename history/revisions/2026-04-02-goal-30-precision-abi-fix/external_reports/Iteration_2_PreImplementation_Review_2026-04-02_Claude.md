I now have a complete picture. Here is my assessment.

---

## Technical Review: Goal 30 Pre-Implementation

### 1. Is the scope technically sound?

Yes. The float truncation problem is confirmed and mechanically clear. Every path that loses precision is visible in the two files:

- `embree_runtime.py`: all coordinate fields in `_RtdlSegment`, `_RtdlPoint`, `_RtdlTriangle`, `_RtdlRay2D`, `_RtdlLsiRow`, and the polygon vertex arrays are `ctypes.c_float`.
- `rtdl_embree.cpp`: the matching C structs, the internal `Vec2` / `Bounds2D` / `Segment2D` types, and the arithmetic in `segment_intersection` / `point_on_segment` are all `float`. `kEps` is `1.0e-6f`.

A float-to-double widening throughout both files is a self-contained change. The change surface is bounded and all pieces are visible.

One inherent constraint that the plan should acknowledge but cannot change: Embree's `RTCBounds` and `RTCRay` structs use `float` fields. When the code assigns double-precision `Vec2` coordinates to `args->bounds_o->lower_x` or `rayhit->ray.org_x`, those values will be narrowed back to float by the Embree API. This means the BVH candidate-selection pass will remain float-precision even after the fix. The fix improves the analytic refinement step (`segment_intersection` in the callback), not the broad-phase candidate generation. That is consistent with the Goal 30 stated intent and does not break the plan, but it should be in the final result report so it isn't rediscovered later.

### 2. Is fixing the geometry ABI first the right next step?

Yes. The minimal 4-segment reproducer proved that float truncation alone drops at least one intersection on the CPU reference path, independent of Embree. That is a confirmed, isolated cause. Removing it before investigating the broad-phase gives Goal 31 a clean baseline. If the precision fix is not enough, the failure after the fix is a sharper signal than the failure before it.

### 3. Missing files or compatibility surfaces

**Named explicitly in the plan:** `embree_runtime.py`, `rtdl_embree.cpp`, "native comparison apps." That last category needs two named files:

- **`apps/embree_remote_validation.cpp`** — defines its own `RtdlSegment` with `float` coordinates. It will silently break (struct layout mismatch) if `rtdl_embree.cpp` is widened without updating this app. This file must be in the change list.

- **`apps/goal15_lsi_native.cpp`** — already declares `RtdlSegment` and `RtdlLsiRow` with `double` coordinates. This is a **pre-existing ABI mismatch** with the current float-based library. The app is currently broken against the live library. After Goal 30 widens the library, this app will be accidentally consistent for the segment fields. The implementation pass should verify its full struct layout explicitly rather than assuming it will come out correct.

These are not blockers. Gemini's Iteration 2 review already flagged the synchronicity requirement. The plan's phrase "native comparison apps that share the ABI" implicitly covers them. Naming them explicitly in the implementation checklist removes ambiguity.

No other compatibility surfaces are missing. `goal15_pip_native.cpp` does not define `RtdlSegment`. The test infrastructure and Python DSL surface are unchanged.

---

`Consensus to begin implementation.`
