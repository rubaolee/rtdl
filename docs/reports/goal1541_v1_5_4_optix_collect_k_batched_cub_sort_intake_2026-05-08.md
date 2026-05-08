# Goal 1541: OptiX COLLECT_K_BOUNDED Batched CUB Tile-Sort Intake

## Verdict

Accepted as the strongest measured OptiX `COLLECT_K_BOUNDED` row-width-2 experimental path so far. The CUB tile-sort path now launches one CUDA grid for all tiles instead of one kernel launch per tile, while remaining opt-in behind:

`RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1`

The clean pod evidence at commit `d876074f0681125fbb1631bb080ac2cc838a391a` preserved parity and improved all target counts versus Goal 1540.

## Scope

- Pod: `root@213.173.110.196 -p 24309`
- Device: `NVIDIA RTX 2000 Ada Generation`
- Driver: `570.172.08`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`
- Probe command: `RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1 PYTHONPATH=src:. python3 scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py --library build/librtdl_optix.so --counts 4097 65537 131072 --repeats 5 ...`

## Artifacts

- `docs/reports/goal1541_v1_5_4_optix_collect_k_batched_cub_sort_probe_2026-05-08.json`
- `docs/reports/goal1541_v1_5_4_optix_collect_k_batched_cub_sort_probe_2026-05-08.md`
- `docs/reports/goal1541_v1_5_4_optix_collect_k_batched_cub_sort_profile_2026-05-08.jsonl`

## Result

Compared with Goal 1540 CUB early-compact evidence:

| candidates | Goal 1540 total ms | Goal 1541 total ms | total speedup | Goal 1540 sort ms | Goal 1541 sort ms |
|---:|---:|---:|---:|---:|---:|
| 4097 | 0.901295 | 0.497069 | 1.813x | 0.072273 | 0.028881 |
| 65537 | 2.140650 | 1.350490 | 1.585x | 0.907305 | 0.053423 |
| 131072 | 3.585420 | 1.854850 | 1.933x | 1.792420 | 0.089113 |

Compared with Goal 1536 late-level compact evidence:

| candidates | Goal 1536 total ms | Goal 1541 total ms | total speedup |
|---:|---:|---:|---:|
| 4097 | 1.645010 | 0.497069 | 3.309x |
| 65537 | 24.060700 | 1.350490 | 17.816x |
| 131072 | 32.583600 | 1.854850 | 17.567x |

## Implementation Notes

- The new kernel `collect_k_bounded_i64_row_width2_cub_sort_tiles` launches one block per `2048`-row tile.
- Each block still uses `cub::BlockMergeSort<CollectKRow2, 256, 8>`.
- The existing one-tile CUB kernel remains in source but the CUB path now uses the batched grid.
- Non-CUB behavior remains unchanged.

## Current Bottleneck

At `131072`, measured median stage timing is now:

- total: `1.854850 ms`
- sort sync: `0.089113 ms`
- merge sync: `0.036822 ms`
- merge launch overhead: `1.242840 ms`
- allocation: `0.340623 ms`

The next bottleneck is host-side launch orchestration for many compact kernels, plus fixed allocation overhead.

## Claim Boundary

This is accepted internal experimental evidence for the Python OptiX `COLLECT_K_BOUNDED` device-pointer path only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, stable primitive promotion, or release action without the required review and consensus.
