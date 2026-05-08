# Goal 1530: OptiX COLLECT_K_BOUNDED Batched Merge-Level Intake

## Verdict

Accepted as measured implementation evidence for a second narrow OptiX `COLLECT_K_BOUNDED` merge optimization. The change keeps the same `row_width2_bounded_multi_tile_sort_merge` public path and parity shape, but replaces one merge-kernel launch per pair with one merge-kernel launch per merge level.

This is still experimental `COLLECT_K_BOUNDED` evidence. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.

## Source Change

- `src/native/optix/rtdl_optix_core.cpp` adds `collect_k_bounded_i64_row_width2_merge_level`.
- `src/native/optix/rtdl_optix_api.cpp` uploads a small per-level metadata packet of device pointers and counts, then launches one grid where each block merges one independent pair.
- `scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py` updates expected topology for the tiled row-width-2 path from one merge launch per pair to one merge launch per level.
- The one-pass merge behavior from Goal1529 is preserved inside each pair merge.

## Pod Scope

- Pod: `root@213.173.110.196 -p 24309`
- Device: `NVIDIA RTX 2000 Ada Generation`
- Driver: `570.172.08`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- Git commit used for clean pod checkout: `bc934dfb604e9996b2bcc692729d8f98e8a8e64e`
- Measured path: `row_width2_bounded_multi_tile_sort_merge`
- Counts: `4097`, `65537`, `131072`
- Repeats: `5`

## Before/After

| Candidate rows | Baseline native total ms | One-pass native total ms | Batched-level native total ms | Batched improvement vs baseline | Batched improvement vs one-pass | Baseline merge sync ms | One-pass merge sync ms | Batched merge sync ms | Batched merge improvement vs baseline |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 4097 | 1.526860 | 1.434290 | 1.482630 | 2.90% | -3.37% | 0.339783 | 0.254980 | 0.268560 | 20.96% |
| 65537 | 79.377400 | 48.881700 | 34.238100 | 56.87% | 29.96% | 67.207700 | 36.684500 | 20.177500 | 69.98% |
| 131072 | 180.287000 | 108.893000 | 52.834800 | 70.69% | 51.48% | 156.370000 | 85.036100 | 28.930000 | 81.50% |

## Interpretation

The batched-level change confirms that a major remaining cost after Goal1529 was not only the single-thread merge loop itself, but also serializing independent pair merges in the default stream. Running all pair merges within a level as one grid cuts the long-count merge synchronization time sharply.

The small `4097` case is slightly slower than the one-pass-only path because the batched path adds per-level metadata upload/setup. This is acceptable for the current long-workload priority and should not be marketed as a short-workload speedup.

The remaining performance limit is the final large pair merge, which is still one block with one active thread. The next engineering target is a true parallel merge/compact kernel for each pair, not more launch batching.

## Artifacts

- `docs/reports/goal1530_v1_5_4_optix_collect_k_batched_merge_level_probe_2026-05-08.json`
- `docs/reports/goal1530_v1_5_4_optix_collect_k_batched_merge_level_probe_2026-05-08.jsonl`
- `docs/reports/goal1530_v1_5_4_optix_collect_k_batched_merge_level_probe_2026-05-08.md`
- `docs/reports/goal1530_v1_5_4_optix_collect_k_batched_merge_level_intake_2026-05-08.md`
