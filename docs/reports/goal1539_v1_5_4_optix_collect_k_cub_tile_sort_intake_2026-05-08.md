# Goal 1539: OptiX COLLECT_K_BOUNDED CUB Tile-Sort Intake

## Verdict

Accepted as the strongest measured OptiX `COLLECT_K_BOUNDED` row-width-2 experimental path so far, behind explicit opt-in flags only:

`RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1`

The clean pod evidence at commit `fe92cebe3c3da35692e079b4bb76a3a008a96c71` preserved parity and improved all target counts versus the previous accepted Goal 1536 late-level compact evidence.

## Scope

- Pod: `root@213.173.110.196 -p 24309`
- Device: `NVIDIA RTX 2000 Ada Generation`
- Driver: `570.172.08`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`
- Probe command: `RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1 PYTHONPATH=src:. python3 scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py --library build/librtdl_optix.so --counts 4097 65537 131072 --repeats 5 ...`

## Artifacts

- `docs/reports/goal1539_v1_5_4_optix_collect_k_cub_tile_sort_probe_2026-05-08.json`
- `docs/reports/goal1539_v1_5_4_optix_collect_k_cub_tile_sort_probe_2026-05-08.md`
- `docs/reports/goal1539_v1_5_4_optix_collect_k_cub_tile_sort_profile_2026-05-08.jsonl`

## Result

Compared with Goal 1536 late-level compact evidence:

| candidates | Goal 1536 total ms | Goal 1539 total ms | total speedup | Goal 1536 sort ms | Goal 1539 sort ms | sort speedup | Goal 1536 merge ms | Goal 1539 merge ms |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 4097 | 1.645010 | 1.314240 | 1.252x | 0.884886 | 0.074492 | 11.879x | 0.268451 | 0.657455 |
| 65537 | 24.060700 | 12.166200 | 1.978x | 13.562300 | 0.906544 | 14.960x | 9.792510 | 10.493700 |
| 131072 | 32.583600 | 13.028600 | 2.501x | 23.395900 | 1.788600 | 13.081x | 8.518870 | 10.497500 |

The previous bottleneck, tile sort, is largely removed. The current bottleneck is again merge work, especially because the CUB path uses `2048`-row tiles to stay under the pod's shared-memory limit, increasing tile count and merge levels versus the `4096`-row bitonic path.

## Implementation Notes

- The path is env-gated by `RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT`.
- The default bitonic tile-sort path remains available and unchanged unless the env flag is set.
- The CUB tile-sort kernel uses `cub::BlockMergeSort<CollectKRow2, 256, 8>`, sorting `2048` `(int64,int64)` rows per tile.
- Padded rows use `(INT64_MAX, INT64_MAX)` as the sentinel. This preserves sorted order and exact final unique-row semantics because only the real `candidate_count` rows are emitted from each tile.
- Tile outputs are sorted but not pre-uniqued. The downstream merge path already suppresses adjacent duplicates, so correctness is preserved while avoiding an extra per-tile compact stage.

## Next Direction

The next useful optimization is merge-side, not sort-side:

- Reduce the added merge cost caused by `2048`-row CUB tiles.
- Consider a CUB path with a larger tile size only if shared-memory opt-in or a lower-storage CUB configuration proves viable.
- Consider parallelizing more merge levels or adding a CUB/device-wide merge/unique path for later levels.

## Claim Boundary

This is accepted internal experimental evidence for the Python OptiX `COLLECT_K_BOUNDED` device-pointer path only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, stable primitive promotion, or release action without the required review and consensus.
