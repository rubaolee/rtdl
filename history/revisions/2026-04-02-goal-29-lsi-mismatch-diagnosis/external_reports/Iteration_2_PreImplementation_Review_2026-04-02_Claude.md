Now I have enough to give a thorough review.

---

## Goal 29 Pre-Implementation Review

### 1. Diagnosis Plan Assessment

The plan is technically sound. The approach of:
- freezing a k=5 slice
- doing pair-level CPU vs Embree diff
- classifying the mismatch pattern before touching code

is methodologically correct. The `goal29_inspect_lsi_pairs.py` script that re-runs `_segment_intersection` on the CPU-only pairs (using Python double precision) is well-chosen — it gives you the exact geometry of each missed intersection.

### 2. Flawed Assumptions / Missing Checks

**Pre-report assumption that may be wrong**: The report lists "endpoint-touch handling, duplicate/near-duplicate chain edges, ring-closure edge behavior" as the first likely failure families. These are plausible but the evidence already points more specifically. The actual failure mechanism is visible in the code without running the scripts. See §4 below.

**Missing check in the diagnosis**: The scripts do not verify that the Embree callback is even being called for the missing pairs. Without a printf in `segment_intersect`, you cannot distinguish two failure modes:
- BVH AABB test culling the primitive (callback never fires)
- AABB test passes, callback fires, but `segment_intersection` returns false

Both would produce the same external symptom. However, the analysis below makes the second mode very likely.

### 3. Is it Reasonable to Proceed with a Fix in `rtdl_embree.cpp`?

Yes. The evidence and code analysis are sufficient to identify the root cause precisely. Proceeding is reasonable, with regression required.

### 4. Likely Root Cause

**The determinant epsilon in `segment_intersection` (C++) is 10× too coarse relative to Python.**

`reference.py:193`:
```python
if abs(denom) < 1.0e-7:  # Python float64
    return None
```

`rtdl_embree.cpp:161,266`:
```cpp
constexpr float kEps = 1.0e-6f;
...
if (std::fabs(denom) < kEps) {  // C++ float32
    return false;
}
```

For the example missing pair:

- Left direction vector `r ≈ (0.000033, 0.007275)`
- Right direction vector `s ≈ (-0.000029, 0.0)` — horizontal segment
- Cross product: `|r × s| = |r.x * s.y - r.y * s.x| = |0 - 0.007275 * (-0.000029)| ≈ 2.11e-7`

The true cross product (`≈ 2.11e-7`) is:
- **Above** Python's threshold `1.0e-7` → Python correctly finds the intersection
- **Below** C++'s threshold `1.0e-6f` → C++ classifies these as "parallel/collinear" and returns `false`

This is not a collinearity false positive. The cross product is small because one segment is **short** (`|s| ≈ 2.9e-5`), not because the segments are nearly parallel. The absolute epsilon incorrectly penalizes short segments. All four missing pairs have `right_chain_id=4706`, and the right segments from that chain are apparently short and horizontal, keeping their cross products in `(1e-7, 1e-6)` — below the C++ threshold but above the Python threshold.

**Secondary concern** (may not be the primary cause): `bounds_for_segment` has no epsilon padding in X/Y (only in Z). The horizontal right segment (`y0 == y1`) gets a degenerate zero-height bounding box. In float32, the right segment's `y` value and the probe's endpoint `y` may round to the same float32 (`float32(42.210078) == float32(42.21008)` — they differ by `2e-6 < 3.81e-6 ULP`), making the AABB intersection happen at exactly `t = 1.0f = tfar`. This is a boundary case in Embree's AABB slab test. If Embree's SIMD arithmetic produces `t_near > 1.0f` by any epsilon, these primitives are culled before the callback fires. This concern merits adding X/Y epsilon padding to `segment_bounds` as a defensive measure alongside the primary fix.

**The targeted fix**: Change the determinant check in `segment_intersection` to use `1.0e-7f` instead of `kEps` (`1.0e-6f`). Do not change `kEps` globally — it is used correctly in `point_on_segment`, bounds padding, and other threshold contexts. Additionally, consider adding `kEps` padding to `bounds_o->lower_x/y` and `bounds_o->upper_x/y` in `segment_bounds` to guard against degenerate-AABB traversal misses.

---

`Consensus to begin implementation.`
