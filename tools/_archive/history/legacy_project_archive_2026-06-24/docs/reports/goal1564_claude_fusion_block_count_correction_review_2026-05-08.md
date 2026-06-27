---

## Verdict

**Real additional caveat, and it is more fundamental than Caveat 4 in the previous review.**

Caveat 4 addressed only the partial-final-block edge case inside a shared-memory reduction. It did not identify that the entire shared-memory reduction strategy breaks structurally when threads are input-indexed: a single input thread block's output positions can fan out across multiple output-position blocks, so `block_counts[blockIdx.x]` would accumulate marks for the wrong output range regardless of padding or clamping.

---

## Correction

In the original mark kernel, `global_index = blockIdx.x * blockDim.x + threadIdx.x` is an **output position**, so `blockIdx.x` directly identifies the output block and the shared-memory reduction writes the correct `block_counts[blockIdx.x]`.

In the proposed input-row fused kernel, `blockIdx.x` is an **input-row block**. A thread at input position `i` computes `output_index` by binary search; that output index belongs to output block `output_index / blockDim.x`, which is generally **not equal to** `blockIdx.x`. Accumulating marks into shared memory keyed by `blockIdx.x` and writing `block_counts[blockIdx.x]` is therefore structurally wrong — it misattributes marks to input-block-indexed counts instead of output-block-indexed counts. This is a correctness defect independent of block size or partial-block handling.

---

## Safer First Diagnostic

**Option (a): input-row fused kernel + `atomicAdd` on `block_counts` + `cudaMemsetAsync` reset.**

- Zero `block_counts` (and `marks` if not fully covered) with `cudaMemsetAsync` on the same stream before the fused launch — operations on the same stream serialize in order, so no extra synchronization primitive is needed.
- Each fused thread, after computing `output_index` and `mark`, executes `if (mark) atomicAdd(&block_counts[output_index / blockDim.x], 1)`.
- `merged_rows[output_index]` and `marks[output_index]` are written as in the original plan.

This is strictly less code than a merge-path kernel, and the atomic contention is bounded: threads within one input block that happen to fall into the same output block contend on one counter, but the `block_counts` array is small (one entry per output-position block) and distinct output blocks never contend. Contention is tolerable at diagnostic scale.

The `prefix_offsets_level` kernel downstream reads `block_counts` and is otherwise unchanged.

---

## Risks

**Option (a) risks:**
- The `cudaMemsetAsync` is an additional stream operation; its cost must be included in the timing comparison against the four-kernel baseline, not hidden.
- If `marks` is not fully covered (e.g., a pair's output range has no matching input thread), un-zeroed slots produce wrong mark values. Verify that total input rows for a pair equals total output rows before treating marks as fully covered without a reset.
- Atomic contention is not a correctness risk but does affect occupancy on heavy pairs; measure it in the skewed-pair case, not only the 65537/131072 balanced case.

**Option (b) risks (reason to defer):**
- Merge-path partitioning requires a per-block-boundary binary search that must correctly identify the split point across two input segments simultaneously. Implementation errors are subtle and hard to distinguish from mark-logic errors during parity testing.
- Any bug in the partitioning produces systematically wrong output-position ownership, making parity failures difficult to localize.
- The additional complexity is not justified for a diagnostic whose primary goal is correctness parity before timing is interpreted.
