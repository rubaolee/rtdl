# Goal 1534: OptiX COLLECT_K_BOUNDED Parallel Compact Reference

## Verdict

Accepted as a local correctness reference for the next `COLLECT_K_BOUNDED` parallel merge attempt. It does not change native code and does not claim performance. Its purpose is to define what a correct GPU parallel merge/compact must compute after the Goal1533 rank-only failure.

## Core Lesson

For sorted unique row-width-2 segments, independent lower-bound rank formulas are not enough when duplicates are skipped. The output must be compacted after duplicate removal.

A correct parallel implementation needs the logical equivalent of:

1. Materialize the sorted merged stream, including duplicates, or otherwise assign every merged item a total-order position.
2. Mark the first item and every item that differs from its predecessor.
3. Prefix-sum the marks to compute compact unique output ranks.
4. Write marked rows into the bounded output buffer.
5. Emit exact unique count and overflow state.

## Reference Semantics

Given two sorted unique row-width-2 inputs:

- Output rows must equal `sorted(set(first_rows) | set(second_rows))`.
- Output rows must be lexicographically sorted.
- `emitted_count` is the exact unique row count, even when output capacity is too small.
- `overflowed` is true only when `emitted_count > row_capacity`.
- At most `row_capacity` rows may be written.

## Why This Matters

Goal1533 showed that final-level rank-only union made the final kernel very fast but failed row parity because duplicate skips left holes. Goal1534 keeps that failure from becoming a recurring trap by pinning the compacted semantics in a small, deterministic test.

## CUDA Direction

The GPU implementation should map this reference into kernels:

- Merge-path partitioning can materialize or partition the merged stream.
- Duplicate marking can be one thread per merged position.
- Prefix/compact can use a bounded block/grid scan or a proven local scan primitive.
- The serial one-thread merge remains the safe fallback until parity and pod timing are accepted.

## Claim Boundary

This is a correctness/specification artifact only. It does not authorize public speedup wording, stable primitive promotion, partner tensor handoff, true zero-copy wording, whole-app claims, or release action.

