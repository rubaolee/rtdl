---

## External Review: Goals 1632–1635 Collect-K Final-Pair Direction

### Verdict

Direction is coherent. No error has been made in the experimental sequence. Goal 1635's null result is structurally informative — it eliminates one theory but reveals a phase-accounting artifact that reframes the actual bottleneck.

---

### Interpretation

**Goal 1635 is a phase-accounting artifact, not a true regression.**

In the control path the compact kernel is launched asynchronously — its ~0.044 ms GPU execution time is never charged to the final-pair timing window and runs "for free" behind subsequent work. The Goal 1635 device-prefix prototype added a terminal `cuStreamSynchronize` after the full device pipeline (mark → device_prefix → compact), which made compact's execution visible for the first time. The +0.027 ms total_ms increase is almost entirely explained by compact's execution appearing on the measured critical path rather than being hidden.

Consequence: **the host-prefix step (0.017 ms) was not on the critical path at all.** Goal 1635 confirms it was already overlapping with GPU execution. Eliminating it did not improve total_ms.

**The actual bottleneck is the mark kernel's GPU execution time (~0.323 ms for 262144 rows) — but it may not be what it looks like.**

Theoretical memory-bandwidth bound for 4 MB of row data on A4500 (~384 GB/s) is ~0.011 ms. The measured 0.323 ms is ~29× above that bound. A kernel that slow is almost certainly not bandwidth-saturated. The most likely cause: the mark kernel is queued behind the merge kernel on the default stream and the majority of its 0.323 ms window is **idle stream-wait time**, not GPU computation. The merge kernel itself takes 0.434 ms (Goal 1634 `merge_launch_ms`), and if both run on the default stream, the mark kernel cannot begin executing until merge completes. A fraction of the merge execution may be "inside" the mark-sync measurement window.

---

### Next Candidate

**CUDA event bracket on the mark kernel — isolate GPU execution time from stream-wait time.**

Wrap only the `cuLaunchKernel` for the mark kernel with a pair of CUDA events (`cuEventRecord` before and after, `cuEventElapsedTime` post-hoc). This decomposes `final_pair_mark_sync_ms` into:

- `mark_kernel_gpu_ms` — actual device execution time
- Implicit stream-wait — time queued waiting for merge to release the stream

**Decision table from the result:**

| mark_kernel_gpu_ms | Diagnosis | Next step |
|---|---|---|
| < 0.050 ms | Mark is fast; 0.323 ms is merge blocking the stream | Multi-stream overlap probe (merge on stream A, final-pair on stream B) |
| 0.100–0.200 ms | Mark has occupancy/launch-config inefficiency | Tune block size or replace with CUB DeviceSelect::If |
| > 0.250 ms | Mark is genuinely compute/memory bottlenecked | CUB DeviceSelect or fused mark-compact probe |

This requires no algorithmic change, no new code path, and no parity risk — only two `cuEventRecord` calls around an existing launch. It is the lowest-cost diagnostic available and gates all three distinct remediation paths.

**File location:** `src/native/optix/rtdl_optix_api.cpp` lines ~1347–1355 (variant 1) and ~1425–1433 (variant 2).

---

### Risks

1. **Merge may be the dominant phase regardless.** Goal 1634 shows merge at 0.448 ms vs. final-pair at 0.345 ms. If stream overlap is the remedy and it succeeds, total latency is bounded by merge (~0.448 ms). Further final-pair optimization past that point yields near-zero marginal gain unless merge is targeted in parallel.

2. **CUB DeviceSelect reproduces Goal 1635's accounting issue.** Any device-side compaction primitive that ends with a stream sync will charge compact execution into the measured window. A "slower" measurement may simply mean compact is now visible. Comparisons against the control must account for this explicitly.

3. **Row layout unknown.** The 29× gap vs. bandwidth bound may indicate that `merged_rows` are stored in a non-contiguous or strided layout, making the mark kernel's effective access pattern far worse than assumed. Verify before investing in kernel-level optimization.

4. **Stream-overlap path is higher complexity.** Merge output feeds into final-pair materialize; compact output feeds downstream. Dependencies must be fully mapped before separating streams or silent data races become possible.

5. **No claim boundary change.** None of the evidence to date authorizes public speedup claims, `COLLECT_K_BOUNDED` promotion, or release action. The next probe should be filed as internal diagnostic evidence only.
