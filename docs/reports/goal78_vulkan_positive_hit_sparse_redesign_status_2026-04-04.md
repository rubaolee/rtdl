# Goal 78 Status: Vulkan Positive-Hit Sparse Redesign

**Date:** 2026-04-04  
**Status:** Accepted redesign; hardware-backed validation still pending

---

## What Changed

### Problem

The `positive_only` branch inside `run_pip_vulkan` in `src/native/rtdl_vulkan.cpp` was a
pure CPU nested-loop scan — no GPU involved:

```
for every point pi:
    for every polygon qi:
        if geos.covers or exact_pip:
            emit row
```

This is O(P×Q) on the host, a dense full-scan regardless of actual hit count.

### New Design

Replaced with a two-stage sparse path:

**Stage 1 — GPU candidate generation**

- Fires one ray per point (reuses existing `kPipRgen`)
- Ray tracing hits polygon AABBs; `kPipRint` runs the full exact PIP test in GLSL
- New `kPipPosRahit` shader uses an atomic counter to append `(point_index, poly_index)`
  pairs to a compact candidate list instead of a dense indexed slot
- GPU output is sparse: only pairs where the GPU confirms the point is inside

**Stage 2 — Host exact-finalize on candidates only**

- Downloads the candidate count (1 uint), then downloads only the valid pairs (sub-copy
  pattern mirroring the LSI pipeline)
- Exact-finalizes only those pairs using GEOS (if available) or `exact_point_in_polygon`
- Returns only confirmed positive rows

**What improved:**
- Dense host full-scan O(P×Q) is gone from the positive-hit path
- Host exact-finalization is O(candidates), not O(P×Q)
- Only `n_cands * 8` bytes transferred instead of `P×Q * 12` bytes (worst case same,
  but typical workloads see sparse candidates)
- Full parity preserved: GPU positives are re-validated on host

**Full-matrix path (`positive_only == 0`) is unchanged.**

---

## Why It Changed

The old positive-hit path defeated the point of the positive-hit contract by doing a
complete CPU scan. Goal 78 required GPU candidate generation + host exact-finalize on
candidates only. The new design follows the LSI atomic-counter pattern already in the
codebase.

---

## Exact Files Changed

### Primary code

- `src/native/rtdl_vulkan.cpp`
  - Added `GpuPipCandidate { uint32_t point_index, poly_index; }` struct (~line 774)
  - Added `kPipPosRahit` GLSL shader (sparse atomic candidate output, ~line 1233)
  - Added `g_pip_pos_pipe` and `g_pip_pos_init` pipeline singletons (~line 1931)
  - Replaced the `positive_only != 0u` branch in `run_pip_vulkan` with the
    two-stage GPU-sparse + host-exact path (~line 2073)

### Tests

- `tests/rtdsl_vulkan_test.py`
  - Added 5 focused tests inside `RtDslVulkanTest`:
    1. `test_run_vulkan_pip_positive_hits_parity`
    2. `test_run_vulkan_pip_positive_hits_only_contains_ones`
    3. `test_run_vulkan_pip_positive_hits_row_shape`
    4. `test_run_vulkan_pip_full_matrix_unchanged_after_redesign`
    5. `test_run_vulkan_pip_positive_hits_no_false_positives`

---

## Tests Run

```
python3 -m py_compile src/rtdsl/vulkan_runtime.py tests/rtdsl_vulkan_test.py
# → no errors

PYTHONPATH=src:. python3 -m unittest tests.rtdsl_vulkan_test
# → Ran 3 tests in 0.004s  OK (skipped=1)
```

The 3 Python-layer loader tests passed. The `RtDslVulkanTest` class (including the 5 new
tests) is skipped because no Vulkan runtime is present on this machine. GPU-side
validation requires a host with the compiled RTDL Vulkan library.

---

## What Still Remains Risky

1. **GPU validation not run locally.** The 5 new positive-hit tests require Vulkan
   hardware. The first run with hardware may surface shader compilation errors or binding
   issues.

2. **`kPipPosRahit` Params struct layout.** The new anyhit shader declares
   `Params { uint npoints; uint capacity; }` while the reused `kPipRint` declares
   `Params { uint npoints; uint npolygons; }`. The second field is never read in
   `kPipRint`, so layouts are compatible in practice. This is a naming asymmetry to
   verify on first GPU run.

3. **Candidate buffer pre-allocation is worst-case.** The buffer is still
   `point_count × poly_count` entries. Memory footprint at worst case is the same as
   before. Only the download and exact-finalize are now sparse. A two-pass approach
   (count then allocate) could improve this but is out of scope for Goal 78.

4. **No deduplication.** Each ray hits each AABB at most once (one primitive per BLAS
   geometry). Duplicate `(point_index, poly_index)` pairs are not expected. If a future
   geometry representation uses multiple AABBs per polygon, deduplication would be needed.

5. **Float precision gap.** `kPipRint` uses float arithmetic. Edge-case points near
   polygon boundaries may be included or excluded differently by GPU vs host. Host
   exact-finalize on candidates is the parity guarantee for interior cases. This is the
   same precision caveat as the full-matrix path.

---

## Key Code Diff Summary

### New GLSL shader — `kPipPosRahit` (`src/native/rtdl_vulkan.cpp` ~line 1233)

```glsl
// Sparse anyhit: atomically append (point_index, poly_index) to compact list.
// Replaces the dense indexed write in kPipRahit.
layout(set=0, binding=1, std430) buffer CandBuf    { uvec2 data[]; } cand_buf;
layout(set=0, binding=2, std430) buffer CounterBuf { uint count; };
layout(set=0, binding=3, std140) uniform Params    { uint npoints; uint capacity; };
void main() {
    uint point_index = gl_LaunchIDEXT.x;
    uint poly_index  = gl_PrimitiveID;
    uint slot = atomicAdd(count, 1u);
    if (slot < capacity) {
        cand_buf.data[slot] = uvec2(point_index, poly_index);
    }
    ignoreIntersectionEXT;
}
```

### Old positive-hit path (removed)

```cpp
// Was: pure CPU O(P×Q) nested loop, no GPU
for (size_t pi = 0; pi < point_count; ++pi)
    for (size_t qi = 0; qi < poly_count; ++qi)
        if (geos.covers(qi, ...) || exact_point_in_polygon(...))
            rows.push_back({...});
```

### New positive-hit path (Stage 2 excerpt)

```cpp
// Stage 2: host exact-finalize on candidates only (O(candidates), not O(P×Q))
for (uint32_t ci = 0; ci < n_cands; ++ci) {
    size_t pi = candidates[ci].point_index;
    size_t qi = candidates[ci].poly_index;
    if (pi >= point_count || qi >= poly_count) continue;
    if (!geos.covers(qi, points[pi].x, points[pi].y)) continue;
    rows.push_back({points[pi].id, polys[qi].id, 1u});
}
```

---

## Review Checklist

For the next reviewer:

- [ ] **Shader correctness** — `kPipPosRahit` binding layout matches the descriptor set
      bindings set up in the C++ positive-hit path (bindings 0–6)
- [ ] **Params struct compatibility** — `kPipRint` reused with `{npoints, capacity}` params;
      confirm the second field is truly not read in `kPipRint`
- [ ] **Counter zeroed before dispatch** — `zero_buf(ctx, d_counter)` appears before
      `dispatch_rt`; confirm ordering is correct
- [ ] **Sub-copy pattern** — candidate sub-copy uses `d_cands.buffer` (has `TRANSFER_SRC_BIT`);
      `d_sub` used as intermediate; `download_from_buf` called on `d_sub`
- [ ] **Cleanup completeness** — `d_cands`, `d_counter`, `d_params`, `d_pts`, `d_poly`,
      `d_vert`, `tlas`, `blas`, and `ds.pool` are all freed before returning
- [ ] **Full-matrix path untouched** — `g_pip_pipe` / `g_pip_init` / `kPipRahit` are
      unchanged; the `positive_only == 0` branch is identical to pre-Goal-78 code
- [ ] **Parity tests** — 5 new tests in `RtDslVulkanTest` cover positive-hit parity,
      no-false-positives, field shape, full-matrix regression, and all-contains-ones
- [ ] **GPU run** — run `PYTHONPATH=src:. python3 -m unittest tests.rtdsl_vulkan_test`
      on a host with the compiled Vulkan library to exercise the new GPU path

---

## Decision Points for Reviewer

1. **Accepted design/code closure** for the bounded Goal 78 claim:
   the Vulkan positive-hit path is now sparse on the GPU and exact-finalized on the
   host, replacing the old pure CPU full scan.
2. **Future hardware goal**:
   run the GPU smoke tests and then measure on a Vulkan-capable host before making any
   runtime or performance claim.
3. **Future cleanup**:
   optional Params naming cleanup and any later work on worst-case candidate allocation.
