# Goal 1542: OptiX COLLECT_K_BOUNDED Batched Compact-Level Intake

## Verdict

Accepted as the next measured OptiX `COLLECT_K_BOUNDED` row-width-2 experimental improvement for long candidate lists. The new path batches the parallel compact kernels once per merge level instead of launching materialize, mark-count, and compact kernels once per merge pair.

The path remains opt-in behind:

`RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1 RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL=1`

The clean pod evidence at commit `3600b67343a93c08bda474c7d05e5115c6c9a77a` preserved parity and improved the long-count target cases versus Goal 1541. The smallest target case, `4097`, is recorded as a flat/slightly slower tradeoff and is not claimed as improved.

## Scope

- Pod: `root@213.173.110.196 -p 24309`
- Device: `NVIDIA RTX 2000 Ada Generation`
- Driver: `570.172.08`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`
- Probe command: `RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1 RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL=1 PYTHONPATH=src:. python3 scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py --library build/librtdl_optix.so --counts 4097 65537 131072 --repeats 5 ...`

## Artifacts

- `docs/reports/goal1542_v1_5_4_optix_collect_k_batched_compact_level_probe_2026-05-08.json`
- `docs/reports/goal1542_v1_5_4_optix_collect_k_batched_compact_level_probe_2026-05-08.md`
- `docs/reports/goal1542_v1_5_4_optix_collect_k_batched_compact_level_profile_2026-05-08.jsonl`

## Result

Compared with Goal 1541 batched CUB tile-sort evidence:

| candidates | Goal 1541 total ms | Goal 1542 total ms | total ratio | Goal 1541 merge launches | Goal 1542 merge launches | Goal 1541 merge-launch ms | Goal 1542 merge-launch ms |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 4097 | 0.497069 | 0.518460 | 0.959x | 6 | 6 | 0.038191 | 0.062992 |
| 65537 | 1.350490 | 0.918335 | 1.471x | 96 | 18 | 0.646825 | 0.286392 |
| 131072 | 1.854850 | 0.922655 | 2.010x | 189 | 18 | 1.291020 | 0.353044 |

The main win is not faster device work inside each compact kernel. It is lower host-side launch orchestration for long merge trees. At `131072`, merge launch overhead dropped from `1.291020 ms` to `0.353044 ms`, while parity stayed intact.

## Implementation Notes

- `RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL` enables the new path explicitly.
- Three level-wide kernels were added for final compact levels:
  `collect_k_bounded_i64_row_width2_final_materialize_level`,
  `collect_k_bounded_i64_row_width2_final_mark_counts_level`, and
  `collect_k_bounded_i64_row_width2_final_compact_level`.
- The batched path uploads per-pair row pointers, counts, and output pointers once per level, then launches the three compact kernels across all pairs in that level.
- The final two-segment merge still uses the existing pair compact path so it can write directly to the final output buffer.
- Non-CUB behavior and default behavior remain unchanged unless the explicit env flag is set.

## Current Bottleneck

At `131072`, measured median stage timing is now:

- total: `0.922655 ms`
- sort sync: `0.088593 ms`
- merge sync: `0.071061 ms`
- merge launch overhead: `0.353044 ms`
- allocation: `0.339968 ms`

The remaining dominant costs are fixed allocation overhead and residual host-side orchestration. Further progress should likely focus on workspace reuse or a more persistent merge workspace before attempting more small kernel rewrites.

## Claim Boundary

This is accepted internal experimental evidence for the Python OptiX `COLLECT_K_BOUNDED` device-pointer path only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, stable primitive promotion, or release action without the required review and consensus.
