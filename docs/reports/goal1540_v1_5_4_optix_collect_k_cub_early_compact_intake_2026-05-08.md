# Goal 1540: OptiX COLLECT_K_BOUNDED CUB Early-Compact Intake

## Verdict

Accepted as the strongest measured OptiX `COLLECT_K_BOUNDED` row-width-2 experimental path so far. With the CUB tile-sort path enabled, parallel compact now starts from the first merge level by default, keeping the public behavior opt-in behind:

`RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1`

The clean pod evidence at commit `e2fdde4bb1366275fb8e3d33209f40ed121bf16c` preserved parity and improved all target counts versus both Goal 1539 and Goal 1536.

## Scope

- Pod: `root@213.173.110.196 -p 24309`
- Device: `NVIDIA RTX 2000 Ada Generation`
- Driver: `570.172.08`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`
- Probe command: `RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1 PYTHONPATH=src:. python3 scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py --library build/librtdl_optix.so --counts 4097 65537 131072 --repeats 5 ...`

## Artifacts

- `docs/reports/goal1540_v1_5_4_optix_collect_k_cub_early_compact_probe_2026-05-08.json`
- `docs/reports/goal1540_v1_5_4_optix_collect_k_cub_early_compact_probe_2026-05-08.md`
- `docs/reports/goal1540_v1_5_4_optix_collect_k_cub_early_compact_profile_2026-05-08.jsonl`

## Result

Compared with Goal 1539 CUB tile-sort evidence:

| candidates | Goal 1539 total ms | Goal 1540 total ms | total speedup | Goal 1539 merge ms | Goal 1540 merge ms |
|---:|---:|---:|---:|---:|---:|
| 4097 | 1.314240 | 0.901295 | 1.458x | 0.657455 | 0.008181 |
| 65537 | 12.166200 | 2.140650 | 5.683x | 10.493700 | 0.031022 |
| 131072 | 13.028600 | 3.585420 | 3.634x | 10.497500 | 0.037172 |

Compared with Goal 1536 late-level compact evidence:

| candidates | Goal 1536 total ms | Goal 1540 total ms | total speedup |
|---:|---:|---:|---:|
| 4097 | 1.645010 | 0.901295 | 1.825x |
| 65537 | 24.060700 | 2.140650 | 11.240x |
| 131072 | 32.583600 | 3.585420 | 9.088x |

## Implementation Notes

- Non-CUB behavior keeps the previous default parallel compact threshold of `65536`.
- When `RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1`, the default compact threshold is `4096`, so every merge level uses the parallel materialize/mark/compact path.
- `RTDL_OPTIX_COLLECT_K_PARALLEL_COMPACT_MIN_CAPACITY` can still override the threshold for controlled experiments.
- The CUB path still uses `2048`-row tiles to stay under the observed shared-memory limit.

## Current Bottleneck

The prior merge bottleneck is largely removed. At `131072`, measured median stage timing is now:

- total: `3.585420 ms`
- sort sync: `1.792420 ms`
- merge sync: `0.037172 ms`

The next bottleneck is again sort and launch/allocation overhead, not merge.

## Claim Boundary

This is accepted internal experimental evidence for the Python OptiX `COLLECT_K_BOUNDED` device-pointer path only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, stable primitive promotion, or release action without the required review and consensus.
