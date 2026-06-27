# Goal 1543: OptiX COLLECT_K_BOUNDED Reusable Workspace Intake

## Verdict

Accepted as an opt-in experimental improvement for repeated OptiX `COLLECT_K_BOUNDED` row-width-2 calls. The new path reuses the temporary device workspace across calls instead of allocating all scratch buffers on every Python wrapper invocation.

The path remains opt-in behind:

`RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1 RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL=1 RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE=1`

The clean pod evidence at commit `ddf7d20e737799e6eab527d61afc412ce5fbab1f` preserved parity and improved all measured target counts versus Goal 1542. This is workspace reuse, not true zero-copy.

## Scope

- Pod: `root@213.173.110.196 -p 24309`
- Device: `NVIDIA RTX 2000 Ada Generation`
- Driver: `570.172.08`
- OptiX SDK: `/root/vendor/optix-sdk`, NVIDIA `optix-sdk` tag `v8.0.0`
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`
- Probe command: `RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1 RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL=1 RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE=1 PYTHONPATH=src:. python3 scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py --library build/librtdl_optix.so --counts 4097 65537 131072 --repeats 5 ...`

## Artifacts

- `docs/reports/goal1543_v1_5_4_optix_collect_k_reuse_workspace_probe_2026-05-08.json`
- `docs/reports/goal1543_v1_5_4_optix_collect_k_reuse_workspace_probe_2026-05-08.md`
- `docs/reports/goal1543_v1_5_4_optix_collect_k_reuse_workspace_profile_2026-05-08.jsonl`

## Result

Compared with Goal 1542 batched compact-level evidence:

| candidates | Goal 1542 total ms | Goal 1543 total ms | total speedup | Goal 1542 allocation ms | Goal 1543 allocation ms |
|---:|---:|---:|---:|---:|---:|
| 4097 | 0.518460 | 0.138536 | 3.742x | 0.370974 | 0.000230 |
| 65537 | 0.918335 | 0.447407 | 2.053x | 0.472878 | 0.000290 |
| 131072 | 0.922655 | 0.545801 | 1.690x | 0.357943 | 0.000190 |

The main win is eliminating repeated `cuMemAlloc` scratch allocation from the measured steady-state wrapper call. At `131072`, allocation dropped from `0.357943 ms` to `0.000190 ms`. Merge launch overhead stayed in the same range, so the next bottleneck is no longer allocation; it is residual host launch orchestration and synchronization.

## Implementation Notes

- `RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE` enables the path explicitly.
- `CollectKRowWidth2Workspace` owns one process-local row-width-2 workspace sized for the current bounded tiled path.
- A mutex guards the reusable workspace for the duration of each native call so concurrent users cannot race on the same scratch buffers.
- Default behavior remains per-call allocation unless the env flag is set.
- The implementation intentionally does not claim cross-process persistence, partner tensor ownership, or true zero-copy.

## Current Bottleneck

At `131072`, measured median stage timing is now:

- total: `0.545801 ms`
- sort sync: `0.089183 ms`
- merge sync: `0.071134 ms`
- merge launch overhead: `0.346833 ms`
- allocation: `0.000190 ms`

Further improvement should focus on reducing the remaining launch/synchronization structure, or on a larger API-level prepared execution model that can amortize Python and host orchestration across many calls.

## Claim Boundary

This is accepted internal experimental evidence for the Python OptiX `COLLECT_K_BOUNDED` device-pointer path only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, stable primitive promotion, or release action without the required review and consensus.
