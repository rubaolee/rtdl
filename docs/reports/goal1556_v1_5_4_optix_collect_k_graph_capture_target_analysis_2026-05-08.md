# Goal 1556: OptiX COLLECT_K_BOUNDED Graph Capture Target Analysis

## Verdict

The next implementation target should be the batched compact-level merge window, not the single-command or final-prefix path.

Goal 1555 showed that CUDA graph replay is negative for one tiny command but positive when one replay covers a batch of small commands. The current collect-k profile still has a long-case merge sequence with `23` merge launches. The best candidate is therefore a fixed-topology graph replay path for the repeated `materialize -> mark -> device-prefix -> compact` level block.

## Current Evidence

- Pod: `root@157.157.221.29 -p 22942`
- SSH key used: `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod`
- Device: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.05`
- CUDA toolkit: `/usr/local/cuda-12.8`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- Commit: `39ebf79440809a4a62309719ae74f371308f3079`
- Profile JSON: `docs/reports/goal1556_v1_5_4_optix_collect_k_current_profile_2026-05-08.json`
- Profile Markdown: `docs/reports/goal1556_v1_5_4_optix_collect_k_current_profile_2026-05-08.md`
- Profile JSONL: `docs/reports/goal1556_v1_5_4_optix_collect_k_current_profile_2026-05-08.jsonl`

All profile runs used the accepted current stack:

`RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1 RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL=1 RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE=1 RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT=1 RTDL_OPTIX_COLLECT_K_DERIVED_LEVEL_DESCRIPTORS=1 RTDL_OPTIX_COLLECT_K_DEVICE_LEVEL_COUNTS=1 RTDL_OPTIX_COLLECT_K_DEVICE_FINAL_COUNTS=1`

## Current Profile Snapshot

| candidates | total ms | merge launch ms | merge sync ms | merge launches | merge levels | metadata fields |
|---:|---:|---:|---:|---:|---:|---:|
| 4097 | 0.112734 | 0.034717 | 0.008485 | 7 | 2 | 4 |
| 65537 | 0.283598 | 0.082367 | 0.084241 | 23 | 6 | 34 |
| 131072 | 0.312081 | 0.091844 | 0.120157 | 23 | 6 | 65 |

The `65537` and `131072` cases are the important long-workload cases. They still have `23` merge launches after the accepted metadata reductions.

## Graphable Window

The current device-count/device-prefix level path performs this no-host-sync block for non-final batched compact levels:

1. `collect_k_bounded_i64_row_width2_final_materialize_level_counts_derived`
2. `collect_k_bounded_i64_row_width2_final_mark_counts_level_counts`
3. `collect_k_bounded_i64_row_width2_final_prefix_offsets_level`
4. `collect_k_bounded_i64_row_width2_final_compact_level_derived`

This is the correct graph-capture target because the data dependency stays on device inside the block. It also matches the Goal 1555 positive condition: one replay would represent multiple small launches rather than one tiny command.

## Implementation Risk

The block is not immediately reusable as one static graph for every level. Each level changes parameters such as `pair_count`, `blocks_per_pair`, `segment_capacity`, `output_capacity`, `current_base`, `output_base`, and the active count-buffer pointers.

That means the next implementation must use one of these constrained approaches:

- Build one graph executable per fixed topology and reuse it only for matching levels.
- Capture per level and update kernel node parameters with CUDA graph update APIs before replay.
- Keep the graph path opt-in and fall back to the current direct-launch path whenever topology or parameter update support is not exact.

The path should not capture across host-visible steps such as tile overflow validation, final block-count download/upload, or final host count publication.

## Next Work

Prototype an opt-in graph path for the non-final batched compact-level block only. The first acceptance test should require parity with the current path and should report both `merge_launch_ms` and `merge_sync_ms` for `65537` and `131072`.

Do not implement graph replay around the rejected final-prefix idea from Goal 1554. Also do not claim collect-k speedup until a parity-preserving graph path beats the accepted Goal 1552 stack on the same measured package.

## Claim Boundary

This report is a target-selection and dependency analysis. It does not change runtime behavior, does not publish a user feature, and does not authorize public speedup wording.
