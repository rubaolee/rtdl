# Goal 1529: OptiX COLLECT_K_BOUNDED One-Pass Merge Intake

## Verdict

Accepted as measured implementation evidence for a narrow native OptiX merge-kernel optimization. The optimization keeps the existing `row_width2_bounded_multi_tile_sort_merge` path and parity shape, but changes the final two-way merge kernel from count-then-write to count-and-write in one pass.

This does not publish Goal 69/70-era speedup wording, true zero-copy wording, partner tensor handoff wording, stable primitive promotion, or release action.

## Source Change

- `src/native/optix/rtdl_optix_core.cpp` updates `collect_k_bounded_i64_row_width2_merge_two`.
- The previous kernel scanned the merged sorted streams once to count unique rows, then scanned them again to write unique rows.
- The new kernel writes each unique row while counting it, bounded by `row_capacity`, and still reports `overflowed` when the full unique count exceeds capacity.
- `src/native/optix/rtdl_optix_api.cpp` and `src/native/optix/rtdl_optix_prelude.h` were restored from the failed local Thrust experiment; no Thrust path is part of this accepted change.

## Pod Scope

- Pod: `root@213.173.110.196 -p 24309`
- Device: `NVIDIA RTX 2000 Ada Generation`
- Driver: `570.172.08`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- Baseline artifact commit: `0274ca32d3dd76d7dfc3f4214375db93b8838908`
- Measured path: `row_width2_bounded_multi_tile_sort_merge`
- Counts: `4097`, `65537`, `131072`
- Repeats: `5`

## Before/After

| Candidate rows | Baseline wrapper median ms | One-pass wrapper median ms | Baseline native total ms | One-pass native total ms | Native total improvement | Baseline merge sync ms | One-pass merge sync ms | Merge sync improvement |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 4097 | 1.778916 | 1.684815 | 1.526860 | 1.434290 | 6.06% | 0.339783 | 0.254980 | 24.96% |
| 65537 | 79.631049 | 49.188428 | 79.377400 | 48.881700 | 38.42% | 67.207700 | 36.684500 | 45.42% |
| 131072 | 180.659663 | 109.152097 | 180.287000 | 108.893000 | 39.60% | 156.370000 | 85.036100 | 45.62% |

## Interpretation

The accepted Goal1506 stage profile showed that long-count performance was dominated by merge synchronization time, not metadata download or final device-to-device copy. The one-pass merge validates that a large part of the measured bottleneck was avoidable duplicate serial work inside the final merge kernel.

The remaining long-count bottleneck is still merge synchronization time. This change improves the current generic path but does not solve the deeper issue that the merge kernel is still single-threaded. A future pod stage should target a genuinely parallel merge/compact design if we want another large step down.

## Artifacts

- `docs/reports/goal1529_v1_5_4_optix_collect_k_one_pass_merge_probe_2026-05-08.json`
- `docs/reports/goal1529_v1_5_4_optix_collect_k_one_pass_merge_probe_2026-05-08.jsonl`
- `docs/reports/goal1529_v1_5_4_optix_collect_k_one_pass_merge_probe_2026-05-08.md`
- `docs/reports/goal1529_v1_5_4_optix_collect_k_one_pass_merge_intake_2026-05-08.md`

