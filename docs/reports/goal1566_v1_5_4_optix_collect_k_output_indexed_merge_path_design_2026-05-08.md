# Goal 1566: output-indexed merge-path fusion design

## Verdict

Goal 1565 closed the input-row fused materialize+mark design: it preserved
parity but lost performance because reset plus atomic block-count accumulation
cost more than the saved mark launch.

The remaining compact-level fusion candidate is output-indexed merge-path
materialize+mark. It should be treated as a diagnostic-only kernel until parity
and pod timing prove otherwise.

## Current Boundary

The current compact-level block is:

1. `collect_k_bounded_i64_row_width2_final_materialize_level_counts_derived`
2. `collect_k_bounded_i64_row_width2_final_mark_counts_level_counts`
3. `collect_k_bounded_i64_row_width2_final_prefix_offsets_level`
4. `collect_k_bounded_i64_row_width2_final_compact_level_derived`

Goal 1565 replaced the first two kernels with one input-row-owned fused kernel,
but it needed:

- stream reset of `marks`;
- stream reset of `block_counts`;
- `atomicAdd` into output-position block counts.

That design was correct but slower.

## Output-Indexed Merge-Path Idea

The next diagnostic should assign each thread to a merged output position
`local_index`, not an input row. For each pair, the thread finds the stable
merge partition:

```text
k = local_index
i = number of first-segment rows before merged position k
j = k - i
```

where `i` satisfies:

```text
0 <= i <= first_count
0 <= j <= second_count
i + j = k
first_rows[i - 1] <= second_rows[j] when both exist
second_rows[j - 1] < first_rows[i] when both exist
```

The strict second condition preserves the existing stable merge behavior:
first-segment rows come before equal second-segment rows. This matches the
current materialize kernels, which use:

- `lower_bound(second_rows, first_value)` for first-segment rows;
- `upper_bound(first_rows, second_value)` for second-segment rows.

After the partition is found, the thread selects the next tagged row:

```text
if first row exists and (second row absent or first_value <= second_value):
    output = first_rows[i]
else:
    output = second_rows[j]
```

Then `mark` is computed against `local_index - 1`. Since the kernel is already
output-indexed, it can either:

- compute the previous output row with a second merge-path partition for
  `local_index - 1`; or
- use a block-local neighbor from shared memory when `threadIdx.x > 0` and use
  one extra merge-path lookup only at block boundaries.

The first version is simpler and safer for the diagnostic. The optimized
shared-memory boundary version can wait until parity is proven.

## Why This Avoids Goal 1565's Cost

Because thread ownership matches output positions, each CUDA block owns one
output-position block. It can compute `block_counts[blockIdx.x]` with the same
shared-memory reduction pattern as the current mark kernel.

That means the diagnostic can avoid:

- `cuMemsetD32Async(marks, ...)`;
- `cuMemsetD32Async(block_counts, ...)`;
- `atomicAdd(...)`.

The candidate block becomes:

1. fused output-indexed materialize+mark+block-count kernel;
2. `prefix_offsets_level`;
3. `compact_level_derived`.

## Correctness Cases

The diagnostic must include parity coverage for:

- empty predecessor at `local_index = 0`;
- boundary partitions where `i = 0` or `j = 0`;
- equal values across first and second segments;
- row selection using the same `first_value <= second_value` ordering as the
  partition condition;
- duplicate runs longer than one block;
- odd pair sizes and partial final blocks;
- skewed pair sizes where one segment is much shorter than the other;
- balanced long cases matching Goal 1565 timing scope.

## Risk

Merge-path partition logic is more complex than the atomic/reset diagnostic.
A partition bug can produce output rows that are sorted but not stable, which
may only appear when equal values cross segment boundaries. Therefore the next
implementation must prioritize parity and deterministic small cases before any
timing interpretation.

## Next Action

Implement a diagnostic-only output-indexed fused materialize+mark kernel and
probe. Keep production unchanged. First prove parity on targeted duplicate and
boundary cases, then measure the accepted RTX pod cases. Do not publish speedup
wording unless the diagnostic becomes a reviewed production candidate.

## External Review

Claude reviewed this design on 2026-05-08 and agreed that the asymmetric
partition condition is correct for the current stable merge behavior. The
review also agreed that computing the previous output row with a second
merge-path lookup is the safe first diagnostic choice. Review artifact:
`docs/reports/goal1566_claude_output_indexed_merge_path_review_2026-05-08.md`.
