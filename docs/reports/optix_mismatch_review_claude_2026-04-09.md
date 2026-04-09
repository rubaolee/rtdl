## Verdict

**Expected duplicate-hit artifact** — not a backend correctness bug and not a comparison/reporting bug. The one extra 3D OptiX hit is the well-known OptiX custom-geometry BVH re-visitation behavior. The renderer is not broken; the backend hit-count value is inflated by one for that ray.

## Findings

1. **Root asymmetry in the two rayhit paths.** The 2D rayhit path in `rtdl_optix.cpp` performs a CPU brute-force exact-count pass after the GPU launch and overwrites `hit_count` with that result. The 3D path has no such correction and writes raw GPU counts directly.

2. **Why OptiX over-counts.** The 3D kernel uses a custom-geometry AABB acceleration structure with `OPTIX_RAY_FLAG_NONE` and `optixIgnoreIntersection()` in the anyhit path. OptiX can revisit the same custom primitive's AABB from multiple BVH nodes during traversal, so the same seam triangle can be counted twice.

3. **The debugging evidence fits.** Exactly one ray differed, with exactly one extra hit (`2 -> 3`), while visible hit/miss status stayed unchanged. That is the expected signature of a duplicate seam hit, not a broad backend drift.

4. **Rendering is unaffected today.** The demo layer now reports visible-hit parity separately from strict exact-count parity. Since `2 > 0` and `3 > 0` are both visible hits, the rendered movie remains visually correct even though the strict hit count is inflated for one ray.

## Summary

The current repo posture is rendering-correct but backend-imprecise for this narrow OptiX 3D hit-count case. The right next fix is to port the existing CPU exact-count correction pattern from the 2D OptiX rayhit path into the 3D OptiX rayhit path, so the final reported `hit_count` matches the CPU reference exactly even when the OptiX traversal revisits a seam triangle.
