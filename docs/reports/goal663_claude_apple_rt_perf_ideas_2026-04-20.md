# Goal663: Apple RT Performance Review and Next-Step Ideas

Date: 2026-04-20

Reviewer: Claude Sonnet 4.6

---

## 1. Is the Current Apple RT Path Genuinely Metal/MPS RT-Backed?

**Yes, confirmed.**

The implementation uses `MPSTriangleAccelerationStructure` to build a GPU BVH and `MPSRayIntersector` to encode ray intersection dispatches into Metal command buffers. Specifically:

- `append_anyhit_2d_chunk` in `rtdl_apple_rt_prelude.mm` allocates Metal vertex buffers, builds a `MPSTriangleAccelerationStructure` via `[accel rebuild]`, and stores the result in the prepared handle.
- `run_anyhit_2d_prepared` encodes with `[intersector encodeIntersectionToCommandBuffer:... intersectionType:MPSIntersectionTypeAny ...]` and issues the work to the GPU via `[command_buffer commit]`.
- The one-shot 3D closest-hit path in `rtdl_apple_rt_mps_geometry.mm` does the same with `MPSIntersectionTypeNearest`.

There is no CPU fallback hidden inside these hot paths. This is real GPU traversal.

---

## 2. Is the Performance Claim Honest?

**Yes, confirmed.**

The Goal662 benchmark on Apple M4 (macOS 26.3, Embree 4.4.0) measured:

| Backend | Per-query median |
| --- | ---: |
| Apple RT prepared-query | 0.006613661 s |
| Embree | 0.003396472 s |
| Shapely/GEOS STRtree | 0.072708116 s |

- Apple RT is **~1.95x slower than Embree**.
- Apple RT is **~11x faster than Shapely/GEOS**.

The Goal661 long-run data (prior to Goal662's optimization) shows the pre-optimization Apple RT was ~10.6x slower than Embree per-query and ~0.5x of Shapely — at the time barely beating Shapely. Goal662's `MPSIntersectionTypeAny` + buffer-reuse changes gave a real **5.65x improvement** over that baseline.

The honest claim is:

> Apple RT prepared any-hit is faster than Shapely/GEOS STRtree on the measured Mac visibility/collision benchmark, but Embree remains the fastest measured backend on this Mac. Apple RT does not beat Embree.

Do not claim Apple RT beats Embree.

---

## 3. Performance Ideas in Priority Order

### Part A: Low-Risk / Implement Now

**A1. Switch intersection data type from `MPSIntersectionDataTypeDistancePrimitiveIndex` to `MPSIntersectionDataTypeDistance` for any-hit**

The current any-hit path uses `MPSIntersectionDistancePrimitiveIndex` (8 bytes per ray: 4-byte float distance + 4-byte uint primitive index). For any-hit semantics, the primitive index is never used — the code only checks `distance >= 0.0f`. Switching to `MPSIntersectionDataTypeDistance` (4 bytes per ray, distance only) would:

- Halve the intersection buffer footprint.
- Reduce the GPU → CPU data transfer volume.
- Potentially allow faster GPU writes (smaller result struct).

Change locations: `run_anyhit_2d_prepared` in `rtdl_apple_rt_prelude.mm` — the `intersector.intersectionDataType` assignment, the buffer size calculation, and the result readback struct.

**Correctness risk: Low.** The any-hit result interpretation only checks `distance >= 0.0f && distance <= 1.000001f`. As long as the distance field semantics are preserved (negative = miss for MPS), the boolean outcome is identical.

---

**A2. Eliminate redundant `valid_ray_2d` re-check in the per-chunk mask update loop**

In `run_anyhit_2d_prepared`, before each chunk dispatch, there is a CPU loop (prelude.mm ~line 610):

```cpp
for (size_t ray_index = 0; ray_index < ray_count; ++ray_index) {
    gpu_rays[ray_index].mask = (valid_ray_2d(rays[ray_index]) && any_hits[ray_index] == 0u) ? 0xFFFFFFFFu : 0u;
}
```

`valid_ray_2d` is called again here even though validity was already determined when building `mps_rays` earlier in the same function. With the current single-chunk design, this runs once per query. A precomputed `bool valid[ray_count]` array (or a bitmask) built during the initial mps_rays encoding pass would eliminate the redundant validation on every chunk pass — important if multi-chunk paths return in future work.

**Correctness risk: Low.** Same logic, precomputed.

---

**A3. Pre-allocate and pool the output `RtdlRayAnyHitRow` result buffer in the prepared struct**

Each call to `run_anyhit_2d_prepared` ends with a `malloc(ray_count * sizeof(RtdlRayAnyHitRow))`. For a high-frequency app-style query workload (the prepared path's intended use), this is a per-query heap allocation. Adding a `RtdlRayAnyHitRow* output_buffer` + `size_t output_capacity` field to `AppleRtAnyHit2DPrepared` (growing on demand, never shrinking) would eliminate this allocation on repeated calls.

**Correctness risk: Low.** The Python/ctypes caller must be aware the buffer lifetime is tied to the prepared handle, not the individual call. This is already how `ray_buffer` and `intersection_buffer` work.

---

**A4. Reuse `any_hits` working array across calls**

`run_anyhit_2d_prepared` stack-allocates `std::vector<uint32_t> any_hits(ray_count, 0)` and `std::vector<MPSRayOriginMaskDirectionMaxDistance> mps_rays(ray_count)` on every call. For 8192-ray workloads these are ~64 KB allocations per call. Store them in the prepared struct as grow-only buffers (same pattern as A3).

**Correctness risk: Low.** Must zero `any_hits` at the start of each call (memset), which is cheaper than reallocation.

---

### Part B: Medium Risk / Some Design Work

**B1. Profile and isolate the `waitUntilCompleted` blocking cost**

The current path calls `[command_buffer waitUntilCompleted]` after each GPU dispatch. On a unified-memory M-series chip, the GPU and CPU share memory, so this synchronization may be shorter than on discrete GPUs — but it is still a round-trip to the GPU scheduler. Profiling with Metal System Trace (Instruments → Metal Application) would reveal what fraction of the 6.6 ms per-query is:

- Ray packing (CPU memcpy to MTLBuffer)
- Command buffer creation and encoding
- GPU traversal
- `waitUntilCompleted` stall
- Result readback loop

If GPU traversal is a small fraction of 6.6 ms and the stall dominates, then command-buffer batching (B2) is the highest-leverage next step. If GPU traversal dominates, then BVH quality or traversal configuration should be examined.

**Correctness risk: None.** This is measurement-only.

---

**B2. Batch multiple `prepared.run(rays)` calls into a single Metal command buffer**

Each call creates one command buffer, encodes one intersection pass, commits, and waits. For apps that call `prepared.run` in a loop, command buffer creation and scheduler overhead is paid every iteration. A batching API — where N ray sets are encoded into one command buffer with N intersection encodes, submitted once, and results read in one pass — would amortize this overhead.

**Correctness risk: Medium.** Requires API surface changes and careful buffer layout for multiple ray sets. Result ordering and per-set output demultiplexing adds complexity.

---

**B3. Investigate whether the prism tessellation (8 triangles per 2D triangle) can be reduced**

The 2D→3D prism encoding in `append_anyhit_2d_chunk` expands each 2D input triangle into 8 Metal triangles (two caps + six side panels). For a triangle with no thin edges, 4 triangles (two caps + four sides) may be geometrically sufficient. Reducing prism complexity shrinks the BVH, lowers build time, and may improve traversal throughput.

**Correctness risk: Medium.** Must verify that all horizontal ray directions (dy=0 component) and all valid 2D configurations still yield correct any-hit results. The current 8-triangle prism is conservative; a 4-triangle prism would need proof that no edge case is missed, particularly for rays that graze prism edges at z=±1.

---

### Part C: Speculative / Research-Heavy

**C1. Port to Metal 3 `MTLAccelerationStructure` + `MTLIntersectionFunctionTable` (hardware RT on M2+)**

The current path uses `MPSRayIntersector`, which is the older MPS-based ray intersection API. Apple M2 and later support a dedicated hardware ray-tracing unit exposed through `MTLAccelerationStructure` (the Metal 3 RT API). This API:

- Uses hardware-accelerated BVH traversal distinct from the MPS compute path.
- Supports intersection function tables for custom any-hit logic.
- Is what modern game engines use on Apple Silicon.

On M4 (which has dedicated RT hardware), this could plausibly close the gap with Embree or exceed it.

**Correctness risk: High.** Full API rewrite. New BVH format, different build/compaction flow, different intersection semantics, different shader language surface (intersection functions in Metal Shading Language). Requires macOS 13+ / M2+ at minimum.

---

**C2. Move result post-processing into a Metal compute shader**

The current result readback loop (CPU, O(ray_count) per chunk) reads GPU intersection distances and sets `any_hits[ray_index]`. This could be encoded as a Metal compute kernel that runs in the same command buffer: the kernel writes a `uint32_t any_hit` result per ray directly, avoiding the GPU→CPU→GPU round-trip that comes from reading back intersections, updating masks, and re-encoding.

**Correctness risk: Medium.** Requires Metal Shading Language code, a new pipeline state object, and careful synchronization. The early-exit optimization (stop once all rays resolved) is hard to express efficiently in a compute shader without atomic counters.

---

## 4. Correctness Risk Summary

| Idea | Risk | Key Concern |
| --- | --- | --- |
| A1 — distance-only intersection type | Low | Verify MPS distance semantics for `MPSIntersectionTypeAny` |
| A2 — precompute valid-ray bitmask | Low | Precomputed result must match inline logic exactly |
| A3 — pool output buffer | Low | Buffer lifetime tied to prepared handle, not call |
| A4 — pool working arrays | Low | Must zero `any_hits` on each call entry |
| B1 — profiling only | None | — |
| B2 — multi-call batching | Medium | Result ordering, API surface complexity |
| B3 — reduce prism triangulation | Medium | Grazing-ray and edge-case correctness at prism boundary |
| C1 — Metal 3 RT API | High | Full API rewrite, hardware availability, semantic differences |
| C2 — compute shader post-process | Medium | Metal shader correctness, early-exit loss |

---

## 5. Recommended Next Implementation Step

**Implement A1: switch the prepared any-hit intersector to `MPSIntersectionDataTypeDistance`.**

This is the single highest-confidence improvement that does not require behavioral or API changes. It halves the intersection result buffer, reduces the GPU-write footprint, and eliminates a field that is provably unused in the any-hit path. The change is confined to three lines in `run_anyhit_2d_prepared`: the intersector `intersectionDataType` assignment, the buffer length calculation, and the result struct type. It can be verified correct by re-running the existing correctness suite (`tests.goal578_apple_rt_backend_test`, `tests.goal651_apple_rt_3d_anyhit_native_test`, `tests.goal652_apple_rt_2d_anyhit_native_test`, `tests.goal659_mac_visibility_collision_perf_test`) with no test changes, and the performance effect can be measured immediately with the Goal659 benchmark script.
