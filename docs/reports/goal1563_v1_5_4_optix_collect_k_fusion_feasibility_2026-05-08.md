# Goal 1563: OptiX collect-k fusion feasibility

## Verdict

Do not implement a naive `materialize_level_counts_derived` plus
`mark_counts_level_counts` fusion by having one kernel write `merged_rows` and
then immediately read neighboring `merged_rows` entries to produce marks. The
current two-kernel split is not accidental: the mark kernel depends on a fully
materialized, globally ordered merged row buffer.

The first safe fusion candidate is still materialize+mark, but only if the
fused kernel computes each output row's predecessor directly from the two
sorted input segments. That avoids relying on writes from other blocks or
threads in the same kernel launch.

## Current Hot Block

The accepted long-case collect-k path still has a four-kernel compact-level
block:

1. `collect_k_bounded_i64_row_width2_final_materialize_level_counts_derived`
2. `collect_k_bounded_i64_row_width2_final_mark_counts_level_counts`
3. `collect_k_bounded_i64_row_width2_final_prefix_offsets_level`
4. `collect_k_bounded_i64_row_width2_final_compact_level_derived`

Goal 1557 and Goal 1559 proved this block is graph-replayable, but Goal 1560
proved per-call/per-level graph update overhead loses in the real production
path. Goal 1561 therefore redirected the next work toward kernel launch
reduction by fusion.

## Dependency Hazard

The materialize kernel writes each candidate row into its globally ordered
merged position:

- first segment row: `output_index = first_index + lower_bound(second_rows, row)`
- second segment row: `output_index = second_index + upper_bound(first_rows, row)`

The mark kernel then reads:

- `pair_merged_rows[local_index]`
- `pair_merged_rows[local_index - 1]`

to decide whether this row starts a new deduplicated output row.

If both operations are simply placed in one kernel, a thread computing mark
`local_index` can read `local_index - 1` before the producing thread for that
previous row has written it. CUDA has no grid-wide synchronization inside a
normal kernel, and this path spans multiple blocks per pair on the measured
long cases. `__syncthreads()` is insufficient because it only synchronizes
threads within one block.

## Safe Fusion Shape

A safe fused diagnostic kernel must compute `mark` without reading
just-written neighboring entries from `merged_rows`.

For a row from the first sorted segment:

- `less_second = lower_bound(second_rows, value)`
- `output_index = first_index + less_second`
- the predecessor, if any, is the lexicographic max of
  `first_rows[first_index - 1]` and `second_rows[less_second - 1]`

For a row from the second sorted segment:

- `le_first = upper_bound(first_rows, value)`
- `output_index = second_index + le_first`
- the predecessor, if any, is the lexicographic max of
  `second_rows[second_index - 1]` and `first_rows[le_first - 1]`

The fused kernel can write both `merged_rows[output_index]` and
`marks[output_index]` from the same thread once that predecessor is derived from
input segments. It can also accumulate `block_counts` from the derived mark in
shared memory, preserving the next `prefix_offsets_level` kernel unchanged.

## Required Correctness Cases

The diagnostic implementation must explicitly cover these cases before timing
is interpreted:

- Boundary rows where both predecessor candidates are absent must produce
  `mark = 1` without dereferencing either input segment at `-1`.
- Equal-valued candidates crossing the two input segments must preserve the
  existing lower-bound/upper-bound stable merge behavior and deduplicate to the
  same marks as the four-kernel path.
- Threads must be assigned by input row, not by output position, because output
  ownership is exactly what the materialize phase is computing.
- Partial final blocks must zero unused lanes before reducing `block_counts`.
- Skewed or short pairs must be measured separately because the extra
  predecessor binary-search work can outweigh one saved launch.

## Expected Tradeoff

This fusion would reduce the compact-level block from four launches to three
launches per merge level. It should reduce launch overhead without CUDA graph
update overhead, but it adds extra predecessor logic and binary-search work to
the materialize stage. The correct next step is a diagnostic-only fused kernel
behind an opt-in probe, measured against the accepted 65537 and 131072 long
cases before any production flag is considered.

## Next Action

Implement a diagnostic-only fused materialize+mark kernel that:

- keeps the existing production path unchanged by default;
- writes `merged_rows`, `marks`, and `block_counts`;
- derives predecessor rows from input segments, not from newly written
  `merged_rows`;
- validates parity against the existing four-kernel block;
- measures total time and `merge_launch_ms` on the RTX pod for 65537 and
  131072.

Do not publish a speedup claim until the diagnostic has parity, measured timing,
and external review.

## External Review

Claude reviewed this feasibility report on 2026-05-08 and agreed that the
naive fusion hazard is real and that predecessor derivation from the input
segments is the plausible safe shape. The review also required the five
correctness cases listed above before any diagnostic timing is treated as
meaningful. Review artifact:
`docs/reports/goal1563_claude_fusion_feasibility_review_2026-05-08.md`.
