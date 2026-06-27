# Goal 1531: OptiX COLLECT_K_BOUNDED Merge-Level Profile Intake

## Verdict

Accepted as profiling evidence for the current batched merge-level OptiX `COLLECT_K_BOUNDED` path. This goal does not change parity semantics, public API, or release status. It adds per-merge-level timing to the opt-in `RTDL_OPTIX_COLLECT_K_PROFILE_JSONL` profile stream and records a clean-pod measurement from the pushed source.

This does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.

## Pod Scope

- Pod: `root@213.173.110.196 -p 24309`
- Device: `NVIDIA RTX 2000 Ada Generation`
- Driver: `570.172.08`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- Git commit: `fc24b7646d7526346b878b0394f3dd0802221d43`
- Counts: `4097`, `65537`, `131072`
- Repeats: `5`
- Measured path: `row_width2_bounded_multi_tile_sort_merge`

## Per-Level Median Sync

| Candidate rows | Level | Input segments | Pair count | Output capacity | Median sync ms |
|---:|---:|---:|---:|---:|---:|
| 4097 | 0 | 2 | 1 | 8192 | 0.268480 |
| 65537 | 0 | 17 | 8 | 8192 | 1.398470 |
| 65537 | 1 | 9 | 4 | 16384 | 2.794410 |
| 65537 | 2 | 5 | 2 | 32768 | 5.586570 |
| 65537 | 3 | 3 | 1 | 65536 | 6.148900 |
| 65537 | 4 | 2 | 1 | 131072 | 4.248330 |
| 131072 | 0 | 32 | 16 | 8192 | 1.215960 |
| 131072 | 1 | 16 | 8 | 16384 | 2.429540 |
| 131072 | 2 | 8 | 4 | 32768 | 4.857090 |
| 131072 | 3 | 4 | 2 | 65536 | 9.712840 |
| 131072 | 4 | 2 | 1 | 131072 | 10.714300 |

## Interpretation

The remaining long-count merge cost is not launch overhead or metadata overhead. Launch and metadata medians are around hundredths of a millisecond per level, while merge synchronization is measured in milliseconds.

For `131072` candidates, levels 3 and 4 account for roughly `20.43 ms` of the `28.93 ms` aggregate merge sync. The final level alone is about `10.71 ms`, and level 3 is about `9.71 ms`. This confirms the next optimization should be a true parallel merge/compact kernel for each pair, especially for the late large-segment levels.

For `65537` candidates, levels 2, 3, and 4 dominate. The odd carry shape makes the final level smaller than level 3, but the conclusion is the same: late large pair merges dominate.

## Next Work

The next implementation should avoid one-active-thread pair merges. A good candidate is a row-width-2 specific parallel merge/compact design that:

- Finds merged output positions in parallel using binary-search merge-path partitions.
- Marks duplicate adjacent rows after merge.
- Uses a bounded prefix/compact step to write unique rows and emit exact counts.
- Preserves fail-closed overflow behavior and existing `row_width2_bounded_multi_tile_sort_merge` parity checks.
- Keeps public claims narrow until measured on a clean NVIDIA pod and reviewed.

## Artifacts

- `docs/reports/goal1531_v1_5_4_optix_collect_k_merge_level_profile_probe_2026-05-08.json`
- `docs/reports/goal1531_v1_5_4_optix_collect_k_merge_level_profile_probe_2026-05-08.jsonl`
- `docs/reports/goal1531_v1_5_4_optix_collect_k_merge_level_profile_probe_2026-05-08.md`
- `docs/reports/goal1531_v1_5_4_optix_collect_k_merge_level_profile_intake_2026-05-08.md`

