## Candidate

**Cooperative-kernel fused merge chain** — replace the multi-pass kernel-launch chain with a single `cudaLaunchCooperativeKernel` that performs all merge passes in a loop, using `cooperative_groups::grid_group::sync()` as the inter-pass barrier.

---

## Why It Could Reach 1.3x

The 0.274 ms `pre_mark_wait` is nearly 40% of total time and is almost entirely overhead rather than compute. The four-kernel graph replay gave only 1.11x because CUDA graphs eliminate CPU launch latency (~microseconds) but do **not** eliminate the inter-kernel synchronization cost — each kernel in the graph still requires a hardware-level fence and re-fill of the dispatch pipeline. A cooperative kernel replaces all of that with a single grid-wide `grid.sync()` barrier, which is substantially cheaper than a full kernel termination/re-issue cycle.

Additionally, intermediate merge buffers written in pass _i_ and read in pass _i+1_ are more likely to reside in L2 when control never leaves the kernel. For a row_width=2 schema the working set is narrow enough that L2 residency across passes is plausible on Ada/Ampere, potentially reducing global memory bandwidth per pass by 20–40%.

Combined, the merge event itself could shrink from ~0.382 ms to ~0.28 ms, and `pre_mark_wait` could drop from ~0.274 ms to ~0.04 ms, yielding ~0.37 ms total vs. ~0.69 ms — approximately 1.35x–1.4x, within the target band.

---

## Implementation Sketch

```cpp
// Replace: chain of merge_pass_kernel<<<...>>>() calls
// With:    one cooperative launch

__global__ void fused_merge_chain_kernel(
    KeyT* __restrict__ buf_a,
    KeyT* __restrict__ buf_b,
    int* segment_offsets,   // input segment boundaries
    int  n_segments,
    int  n_total)
{
    namespace cg = cooperative_groups;
    auto grid = cg::this_grid();

    // Ping-pong: same algorithm as before, just looped
    KeyT* src = buf_a;
    KeyT* dst = buf_b;
    int active_segments = n_segments;

    while (active_segments > 1) {
        // Each CTA handles one merge pair (existing merge kernel body, inlined)
        int pair = blockIdx.x;  // assign pairs statically or via atomic counter
        if (pair < active_segments / 2) {
            merge_two_sorted_runs(src, dst, segment_offsets, pair);
        }
        // Barrier replaces kernel boundary
        grid.sync();

        // Update bookkeeping in-place (single thread or warp 0)
        if (threadIdx.x == 0 && blockIdx.x == 0)
            compact_segment_offsets(segment_offsets, &active_segments);
        grid.sync();

        KeyT* tmp = src; src = dst; dst = tmp;
    }
}
```

Launch requirements:
- Query `cudaOccupancyMaxActiveBlocksPerMultiprocessor` and cap grid to that maximum (cooperative constraint).
- Pass both `buf_a`/`buf_b` pointers in a `void*` args array as required by `cudaLaunchCooperativeKernel`.
- The existing mark and materialize kernels stay separate — they are already fast and have no merge-internal dependencies.

---

## First Probe

Instrument with two CUDA events: one wrapping the full cooperative launch (`coop_merge_event`), one measuring the gap to the mark kernel start (`post_coop_pre_mark_gap`). A successful probe should show:

- `coop_merge_event` ≤ 0.32 ms (vs. 0.382 ms)
- `post_coop_pre_mark_gap` ≤ 0.06 ms (vs. 0.274 ms)
- Output row counts and hash of output keys identical to baseline (parity check)

If `coop_merge_event` drops but `post_coop_pre_mark_gap` stays large, the pre-mark wait is a CPU-side pipeline stall unrelated to kernel-boundary synchronization, and the candidate needs to be paired with a stream-ordered event signal to the host.

---

## Risks

- **Occupancy ceiling**: cooperative kernels must fit all CTAs concurrently. If the merge chain normally uses more blocks than the SM count × max resident blocks, you must reduce threads-per-block or tile size to comply — this can reduce per-pass throughput and eat the savings. Measure occupancy before commit.
- **Segment count mismatch**: if `active_segments` is odd, the lone tail segment must be copied rather than merged; ensure the in-kernel bookkeeping handles this identically to the current chain (it already must, but the in-kernel compact path is new code).
- **Architecture portability**: `cudaLaunchCooperativeKernel` is supported from Pascal onward but the efficiency of `grid.sync()` varies; on Turing/Ampere the barrier cost is well-characterized, but verify on your target SKU.
- **Debuggability regression**: losing kernel boundaries makes Nsight Compute per-pass profiling harder; keep the original chain selectable via a compile flag until the probe confirms the win.
