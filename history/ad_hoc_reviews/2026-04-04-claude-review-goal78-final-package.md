Now I have enough to write the review. Let me compile findings from the code.

---

## Goal 78 Technical Code-and-Report Review

---

### Verdict: APPROVE-WITH-NOTES

The redesign is sound, the report is honest, and acceptance without a hardware performance claim is justified. One real Vulkan spec violation in the sub-copy path must be fixed before first GPU run.

---

### Findings

**F1 — `kPipRint` `npolygons` read: confirmed non-issue**
The status doc flags the `{npoints, npolygons}` vs `{npoints, capacity}` naming asymmetry as a risk. Code inspection confirms the risk is zero. `kPipRint` (lines 1161–1202) never references `npolygons` in its body — it uses only `gl_PrimitiveID`, `gl_LaunchIDEXT.x`, `points.data[]`, `polyrefs.data[]`, and `vertices.data[]`. The UBO field exists in the declaration but is dead. The host correctly passes `{npoints=point_count, capacity=capacity}` and the rint shader reads only `npoints`. This should be downgraded from "risk" to "cosmetic naming inconsistency" in the final report.

**F2 — `d_sub` is missing `VK_BUFFER_USAGE_TRANSFER_DST_BIT` (real bug)**
At `rtdl_vulkan.cpp:2177–2179`:
```cpp
BufMem d_sub = alloc_buffer(ctx, sub_sz,
    VK_BUFFER_USAGE_STORAGE_BUFFER_BIT,
    VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
```
`d_sub` is the *destination* of `vkCmdCopyBuffer(cmd, d_cands.buffer, d_sub.buffer, 1, &copy)` at line 2189. The Vulkan spec (§20.3) requires `VK_BUFFER_USAGE_TRANSFER_DST_BIT` on any buffer used as the destination of a `vkCmdCopyBuffer`. It is absent. Validation layers will flag this and some drivers will silently fail the copy, producing garbage `candidates`. Additionally, `download_from_buf` is then called on `d_sub` (line 2196), which likely requires `TRANSFER_SRC_BIT` on device-local buffers — also absent. The report lists "shader compilation errors or binding issues" as first-run risks but misses this one.

*Fix:* Change line 2178 to:
```cpp
VK_BUFFER_USAGE_STORAGE_BUFFER_BIT |
VK_BUFFER_USAGE_TRANSFER_DST_BIT   |
VK_BUFFER_USAGE_TRANSFER_SRC_BIT,
```

**F3 — Sub-copy intermediate is unnecessary**
`d_cands` already has `TRANSFER_SRC_BIT` (line 2136–2137). `download_from_buf` can be called on `d_cands` directly with `n_cands * sizeof(GpuPipCandidate)` and the correct size. The intermediate `d_sub` adds a device→device copy + buffer allocation + command-buffer overhead, and introduced the bug above. Simplifying to a direct download is lower risk and fewer lines.

**F4 — `ignoreIntersectionEXT` in `kPipPosRahit` is correct**
The anyhit appends the candidate pair and then calls `ignoreIntersectionEXT`, which rejects the intersection so the ray continues intersecting further AABBs. This is the right idiom for "collect all hits, finalize on host." The `kPipRint` intersection shader only fires `reportIntersectionEXT` when the GPU PIP test passes, so candidates are already GPU-confirmed — host exact-finalize is the parity step, not a re-filter from scratch.

**F5 — Counter zeroing order is correct**
`zero_buf(ctx, d_counter)` at line 2146 precedes `dispatch_rt` at line 2165 with no intervening dispatch. Ordering is correct.

**F6 — Cleanup is complete**
Lines 2200–2203 free `ds.pool`, `d_pts`, `d_poly`, `d_vert`, `d_cands`, `d_counter`, `d_params`, `tlas`, and `blas`. All allocations made in the positive-hit branch are freed before returning. `d_sub` is freed inside its own conditional block at line 2197. No leaks identified.

**F7 — Tests are appropriately structured but will remain skipped until GPU hardware is available**
5 new tests cover: parity against CPU, all-ones invariant, row shape, full-matrix regression, no false positives. Test data is minimal but correctly exercises the contract. All 5 are inside `RtDslVulkanTest`, which skips on no-Vulkan machines. The `test_run_vulkan_pip_positive_hits_parity` test is the critical one; it will be the first to expose F2 on hardware.

**F8 — Full-matrix path verifiably untouched**
`kPipRahit` (uses `npolygons` correctly), `g_pip_pipe`, and `g_pip_init` are all unchanged. The `positive_only == 0` branch at line 2236 is identical to pre-Goal-78 code.

---

### Agreement and Disagreement

**Agreement with the report:**
- The old O(P×Q) CPU scan is gone; the replacement architecture is correct.
- `kPipRint` shared reuse is safe — the report's claim that the second UBO field is not read is confirmed by code.
- "Worst-case candidate allocation remains" is correctly stated and scoped out.
- No-deduplication and float-precision caveats are accurate and appropriately flagged.
- Accepting without a hardware performance claim is the right call; the implementation closure framing is honest.

**Disagreement with the report:**
- The Params naming asymmetry is listed as a meaningful first-run risk. It is not — it is confirmed dead code in `kPipRint`. The report overstates this risk and understates F2.
- The `d_sub` TRANSFER_DST_BIT omission is a real, concrete first-run failure mode that goes unmentioned in the risk section. It should be listed explicitly, as it will produce either a validation error or silent data corruption on the first GPU run.
- The sub-copy pattern is described as matching the LSI pipeline, but the LSI pipeline does not use an intermediate device-local buffer this way — the analogy is imprecise.

---

### Recommended next step

**Before merging or tagging Goal 78 closed:** fix the `d_sub` buffer usage flags at `rtdl_vulkan.cpp:2178` (add `TRANSFER_DST_BIT` and `TRANSFER_SRC_BIT`) or eliminate `d_sub` entirely and call `download_from_buf(ctx, candidates.data(), d_cands, sub_sz)` directly. Either fix is a 2-line change. The report can note the correction and the goal can be accepted once the fix is in. No new tests are needed — the 5 existing GPU tests will exercise the corrected path on first hardware run.
