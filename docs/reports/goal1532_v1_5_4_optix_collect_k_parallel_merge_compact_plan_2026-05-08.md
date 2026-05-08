# Goal 1532: OptiX COLLECT_K_BOUNDED Parallel Merge/Compact Plan

## Verdict

The next implementation target should be a row-width-2 parallel merge/compact kernel for the late large merge levels of `COLLECT_K_BOUNDED`. Goal1531 shows that after one-pass merge and batched level launches, remaining long-count time is dominated by large pair merges, especially levels 3 and 4 for `131072` candidates.

This is an implementation plan only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.

## Evidence Base

- Goal1506 accepted baseline showed `131072` native total `180.287 ms`, merge sync `156.370 ms`.
- Goal1529 one-pass merge reduced `131072` native total to `108.893 ms`, merge sync `85.0361 ms`.
- Goal1530 batched merge-level launch reduced `131072` native total to `52.8348 ms`, merge sync `28.9300 ms`.
- Goal1531 per-level profiling at `fc24b7646d7526346b878b0394f3dd0802221d43` showed `131072` merge sync by level:
  `1.21596`, `2.42954`, `4.85709`, `9.71284`, `10.7143` ms.

The current bottleneck is therefore not launch count, metadata transfer, final copy, or duplicated serial scan. It is the remaining one-active-thread merge work for large pairs.

## Current Algorithm

The current tiled row-width-2 path is:

1. Split candidate rows into 4096-row tiles.
2. Sort and unique each tile in a block-local bitonic-style kernel.
3. Merge sorted unique tile outputs level by level.
4. Since Goal1530, each merge level is one grid launch where each block handles one pair.
5. Inside each block, only thread 0 performs the pair merge and unique write.

This is correct and generic for row-width-2 rows, but the late large pair merges remain serial within each pair.

## Target Design

Implement an opt-in internal replacement for `collect_k_bounded_i64_row_width2_merge_level` that parallelizes each pair merge.

The target kernel should keep the same external native path name and the same `COLLECT_K_BOUNDED` contract:

- Input rows are sorted unique per segment.
- Output rows are sorted unique per merged pair.
- `emitted_counts[pair_index]` reports the exact number of unique merged rows, even when overflow occurs.
- `overflowed[pair_index]` is set when unique count exceeds output capacity.
- Rows written to output are bounded by `output_capacity`.
- No app-specific assumptions, no knowledge of GIS or database workloads, and no public API change.

## Candidate Algorithm

Use a three-stage row-width-2 merge/compact pipeline per merge level:

1. Parallel merge materialization.
   Each thread computes one merged-rank position using binary-search merge-path logic across the two sorted input segments, then writes that candidate row into a temporary merged buffer.

2. Parallel duplicate marking.
   Each thread compares `merged[i]` with `merged[i - 1]`. It marks `1` for the first occurrence of each unique row and `0` for duplicates. Position 0 is always marked unique when total input count is nonzero.

3. Prefix/compact.
   A bounded scan computes compact output positions. Threads whose mark is `1` write to `rows_out[rank]` only when `rank < output_capacity`. The final unique count is written to `emitted_counts[pair_index]`, and overflow is `unique_count > output_capacity`.

## Implementation Constraints

- Keep row-width-2 specific first. Do not generalize prematurely to arbitrary row width.
- Avoid Thrust for the first accepted version; the earlier Thrust experiment failed to build cleanly in this repo/pod configuration.
- Prefer self-contained CUDA kernels compiled by the existing NVRTC flow.
- If using CUB, first prove it builds under the project NVRTC/native include flow on the pod before depending on it.
- Preserve the Goal1506/1530/1531 profile stream and extend it only if needed.
- Keep the current serial pair-merge as fallback until the parallel path passes parity and pod timing.

## Risks

- Prefix scan is the hard part. A correct per-pair compact requires either a reliable block/grid scan strategy or bounded assumptions about maximum pair size.
- Late levels can involve up to `131072` row capacity, too large for a single block-local scan if one thread maps one row.
- Multi-kernel per level may improve serial compute time but add synchronization overhead; measurements must decide.
- A partial implementation that only speeds the last level may still be worthwhile, but must keep topology and claim boundaries explicit.

## First Practical Step

Prototype a restricted row-width-2 parallel merge for the final level only, behind an internal environment variable such as `RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_MERGE=1`.

Acceptance for the prototype:

- Build succeeds on the NVIDIA pod with `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`.
- `4097`, `65537`, and `131072` cases preserve candidate rows, valid count, and overflow flag.
- Profile JSONL records whether the final-level parallel path was active.
- `131072` final-level sync drops materially below the Goal1531 final-level median of `10.7143 ms`.
- If the prototype regresses or becomes too complex, keep it uncommitted or commit only a negative result report.

## Claim Boundary

Goal1532 is a planning artifact. It does not promote `COLLECT_K_BOUNDED` to stable, does not claim a user-visible speedup, and does not change the Python+RTDL or Python+partner+RTDL roadmap.

