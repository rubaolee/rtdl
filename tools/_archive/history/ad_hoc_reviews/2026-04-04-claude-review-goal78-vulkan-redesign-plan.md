Now I have everything needed to write the report. Let me produce it.

---

# Goal 78 Engineering Report: Vulkan Positive-Hit Sparse Redesign

**Date:** 2026-04-04  
**File under review:** `src/native/rtdl_vulkan.cpp`, function `run_pip_vulkan` (line 2040)

---

## 1. Current Bottleneck

There are **two separate waste sites**, not one:

### 1a. Positive-hit path bypasses the GPU entirely (lines 2047–2077)

```cpp
if (positive_only != 0u) {
    // Pure CPU double loop: O(N × M) exact tests, no GPU
    for (size_t pi = 0; pi < point_count; ++pi)
        for (size_t qi = 0; qi < poly_count; ++qi)
            if (!geos.covers(qi, ...) / !exact_point_in_polygon(...))
                rows.push_back(...);
    return;
}
```

The GPU RT pipeline is **never dispatched** for positive-hit workloads. For `county_zipcode` (large N and M), this is a full O(N×M) CPU scan — the most expensive possible path.

### 1b. Full-matrix path runs GPU then discards the result (lines 2126–2210)

For `positive_only == 0`, the GPU allocates and fills a dense `N × M` `GpuPipRecord` buffer, downloads it, then immediately overwrites every entry with another full `N × M` host exact-finalization loop. The GPU work buys nothing because the host scan is unconditional.

**Measured consequence:** Vulkan took **112s** vs PostGIS **3s** on `county_zipcode` (Goal 72). The 39 073 actual hits represent a tiny fraction of the `N × M` pairs being processed.

---

## 2. Exact Redesign

The redesign targets **1a** (positive-hit path). The fix for **1b** is a separate cleanup concern; it does not affect the positive-hit contract and should not be conflated.

### New data structure

Add a sparse candidate pair type (line ~774 alongside other Gpu structs):

```cpp
struct GpuCandidatePair { uint32_t point_id, polygon_id; };  // 8 bytes
```

### New pipeline: `pip_sparse`

Introduce a second RT pipeline `g_pip_sparse_pipe` (separate `std::call_once` flag) with three new inline GLSL strings. Binding layout reuses binding 2 as an atomic counter — already scaffolded but currently a dummy.

**`kPipSparseRgen`** — identical to `kPipRgen` (dispatches one ray per point).

**`kPipSparseRint`** — identical to `kPipRint` (AABB intersection, GPU PIP test in shader).

**`kPipSparseRahit`** — replaces `kPipRahit`. Instead of writing to a dense slot, atomically appends a candidate pair:

```glsl
#version 460
#extension GL_EXT_ray_tracing : require
#extension GL_EXT_shader_atomic_int64 : enable
layout(set=0, binding=1, std430) buffer CandBuf { uint data[]; } cands; // GpuCandidatePair[]
layout(set=0, binding=2, std430) buffer CounterBuf { uint count; };
layout(set=0, binding=3, std140) uniform Params { uint npoints; uint npolygons; uint max_cands; uint _pad; };
layout(set=0, binding=4, std430) readonly buffer PointBuf   { float data[]; } points;
layout(set=0, binding=5, std430) readonly buffer PolyRefBuf { uint  data[]; } polyrefs;
layout(location=0) rayPayloadInEXT uint dummy;
void main() {
    uint probeIdx = gl_LaunchIDEXT.x;
    uint primIdx  = gl_PrimitiveID;
    uint slot = atomicAdd(count, 1u);
    if (slot >= max_cands) { ignoreIntersectionEXT; return; }
    uint pbase = probeIdx * 3u;
    uint rbase = primIdx  * 3u;
    uint obase = slot * 2u;
    cands.data[obase+0u] = floatBitsToUint(points.data[pbase+2u]);  // point_id
    cands.data[obase+1u] = polyrefs.data[rbase+0u];                 // polygon_id
    ignoreIntersectionEXT;
}
```

### New host-side positive-hit path (replaces lines 2047–2077)

```
positive_only branch:
  1. Build AABB BLAS/TLAS (same as full-matrix path).
  2. Allocate d_counter (4 bytes, host-visible, zeroed).
  3. Allocate d_cands (max_cands * sizeof(GpuCandidatePair), device-local).
     max_cands = min(point_count * poly_count, SPARSE_CAP)
     where SPARSE_CAP is a compile-time ceiling, e.g. 4 × expected_hits.
     Safe upper bound: point_count * poly_count (same as dense, but only
     allocated — not initialized, so no O(N×M) CPU init loop).
  4. Bind: binding 0 = tlas, 1 = d_cands, 2 = d_counter, 3 = params,
           4 = d_pts, 5 = d_poly, 6 = d_vert.
  5. dispatch_rt(..., point_count).
  6. Download d_counter → cand_count (4 bytes).
  7. Download first cand_count * sizeof(GpuCandidatePair) bytes from d_cands.
  8. Host exact-finalize only those cand_count pairs (GEOS or exact_pip).
  9. Emit only confirmed hits as RtdlPipRow with contains=1.
```

Key invariant: allocation is `O(N×M)` in the worst case but **only for memory**, not for CPU initialization. Step 7 downloads only the sparse K pairs. Step 8 does only K exact checks. For county_zipcode, K ≈ 39 073 vs N×M ≈ millions.

### Params struct extension

The existing `params` struct must grow to carry `max_cands`:

```cpp
struct { uint32_t npoints, npolygons, max_cands, _pad; } params{
    (uint32_t)point_count, (uint32_t)poly_count,
    (uint32_t)max_cands_val, 0u };
```

---

## 3. Files to Change

| File | Change |
|------|--------|
| `src/native/rtdl_vulkan.cpp:773` | Add `struct GpuCandidatePair` |
| `src/native/rtdl_vulkan.cpp:~1203` | Add `kPipSparseRahit` GLSL string (new inline shader) |
| `src/native/rtdl_vulkan.cpp:~1136` | Add `kPipSparseRgen` (can alias `kPipRgen` or duplicate), `kPipSparseRint` (alias `kPipRint`) |
| `src/native/rtdl_vulkan.cpp:~2079` | Add `g_pip_sparse_pipe` and `g_pip_sparse_init` (new `std::once_flag` + `RtPipeline*`) |
| `src/native/rtdl_vulkan.cpp:2047–2077` | Replace CPU-only positive-hit branch with GPU sparse path |
| `tests/goal71_prepared_backend_positive_hit_county_test.py` | Add timing assert: Vulkan positive-hit on county_zipcode must complete under a threshold (e.g., 30s) and preserve parity |

No changes needed to the full-matrix `positive_only == 0` path in this goal (that is a separate cleanup).

---

## 4. Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Counter overflow** — if GPU emits more candidates than `max_cands`, the `slot >= max_cands` guard in the shader silently drops pairs, breaking parity | **Critical** | After download, verify `cand_count <= max_cands`; if equal, re-run with larger cap or fall back to CPU path. Log a warning. |
| **Atomic ordering** — GLSL `atomicAdd` on the counter and the subsequent `cands.data` write are not guaranteed to be visible in order without a barrier | **High** | The host download is after `vkQueueWaitIdle`/fence, so device-to-host visibility is fine. Within the shader, the slot is reserved before writing, which is correct for append-only. No additional barrier needed. |
| **`ignoreIntersectionEXT` discard** — calling it in `rahit` prevents the intersection from being committed. This is the correct pattern for candidate collection (we never want accepted intersections driving payload writes). Confirm this matches the existing behavior in `kPipRahit` (line 1222: it already calls `ignoreIntersectionEXT`). | Low | Verified in existing code. |
| **Float-to-int point_id encoding** — `floatBitsToUint(points.data[pbase+2u])` copies the bit pattern, not a numeric cast. This matches how `GpuPoint.id` was packed in `gpu_pts[i] = {(float)points[i].x, ..., points[i].id}` only if `points[i].id` was stored as a `float` bit pattern. Check `GpuPoint` definition (line 767): `float x, y; uint32_t id` — the upload cast `(float)points[i].x` is fine, but `id` is `uint32_t`. GLSL reads it as `float data[]`, so `floatBitsToUint` reinterprets correctly. Same pattern as existing `kPipRahit` line 1219. | Low | Cross-check at unit test time. |
| **`max_cands` sizing** — setting cap too low causes silent miss; too high wastes VRAM | Medium | Start with `min(point_count * poly_count, 8 * expected_result_count)`. Add assertion in debug builds. |

---

## 5. Needed Tests

1. **Parity test (existing, extend):** `tests/goal71_prepared_backend_positive_hit_county_test.py` — already verifies digest `0d12ece5...`. Ensure the sparse path produces the same digest (39 073 rows, same content) with `vulkan` backend.

2. **Counter-overflow guard test (new):** set `max_cands = 1` artificially, confirm the function either raises or falls back rather than silently missing rows.

3. **Small synthetic test (new):** 3 points, 2 polygons, hand-verified expected hits — run with `vulkan` positive-hit backend, check exact row set. Prevents regression on ID encoding.

4. **Timing regression test (new, advisory):** on `lestat-lx1`, positive-hit `county_zipcode` Vulkan must complete under 30s (vs current 112s). Not a hard CI gate on machines without a GPU, but required before claiming Goal 78 as a performance win.

---

## 6. What This Does NOT Change

- The full-matrix (`positive_only == 0`) path — still dense, still redundant. That is a separate goal.
- The public Python-side API and the `RtdlPipRow` struct.
- The BLAS/TLAS build logic — reused unchanged.
- The parity oracle contract — exact parity with PostGIS is preserved because host exact-finalization still runs on every GPU candidate.
