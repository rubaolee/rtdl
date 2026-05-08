# Goal 1564: collect-k fusion block-count correction

## Verdict

Goal 1563 correctly rejected naive materialize+mark fusion, but it was still
incomplete about the first safe diagnostic design. The current compact path
consumes `marks` and `block_counts` by merged-output position. Therefore an
input-row-owned fused kernel cannot reuse the old shared-memory `block_counts`
reduction directly.

The safer first diagnostic is:

- assign fused threads by input row;
- compute each row's merged `output_index`;
- write `merged_rows[output_index]` and `marks[output_index]`;
- reset `marks` and `block_counts` on the stream before the fused launch;
- use `atomicAdd(&block_counts[output_index / blockDim.x], 1)` for marked rows;
- leave `prefix_offsets_level` and `compact_level_derived` unchanged.

The reset and atomic costs must be included in timing.

## Why The Correction Matters

The current mark kernel is output-position-owned:

```text
global_index = blockIdx.x * blockDim.x + threadIdx.x
mark = marks[global_index]
block_counts[blockIdx.x] = sum(marks in this output-position block)
```

In an input-row-owned fused kernel, `blockIdx.x` describes an input-position
block. After binary search, a thread can write to a different merged
`output_index`, whose output-position block is `output_index / blockDim.x`.
Those two block IDs are not guaranteed to match.

So a shared-memory reduction that writes `block_counts[blockIdx.x]` would count
the wrong output range. This is not just a partial-block bug; it is a structural
ownership mismatch.

## Rejected Shortcut

Do not implement the fused diagnostic as:

```text
input thread block -> shared reduction -> block_counts[input block]
```

That would preserve launch count but break the downstream prefix/compact
contract.

## Accepted Diagnostic Shape

The first diagnostic should use output-indexed mark writes and output-indexed
block-count atomics:

```text
input row -> binary search -> output_index
merged_rows[output_index] = row
marks[output_index] = mark
if mark:
    atomicAdd(block_counts[output_index / 256], 1)
```

Before this fused launch, the stream must reset both arrays used by downstream
prefix/compact:

```text
cuMemsetD32Async(marks, 0, total_blocks * 256, stream)
cuMemsetD32Async(block_counts, 0, total_blocks, stream)
```

These reset calls are part of the diagnostic cost and must not be hidden.

## Deferred Alternative

An output-indexed merge-path fused kernel could avoid atomics and keep
block-local reductions, but it is a larger algorithmic change. It requires
correctly mapping each merged output position back to the responsible input row
or merge partition. That is a better second diagnostic only if the simpler
atomic/reset diagnostic preserves parity but loses performance.

## External Review

Claude reviewed this correction on 2026-05-08 and agreed it is a real
additional caveat. Review artifact:
`docs/reports/goal1564_claude_fusion_block_count_correction_review_2026-05-08.md`.

## Next Action

Implement the atomic/reset diagnostic only, keep production unchanged by
default, and test parity cases before timing:

- boundary first row;
- equal values across segments;
- odd pair sizes and partial final blocks;
- skewed pair sizes;
- measured long cases 65537 and 131072.
