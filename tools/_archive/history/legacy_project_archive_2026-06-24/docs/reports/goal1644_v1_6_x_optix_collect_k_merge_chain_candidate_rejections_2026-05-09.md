# Goal1644 v1.6.x OptiX Collect-K Merge-Chain Candidate Rejections

## Verdict

`no_good_candidate_yet`

Two attempted merge-chain shortcuts did not meet the v1.6.x good-win target. Neither candidate is accepted for production use.

## Scope

- GPU: `NVIDIA RTX A4500, 550.127.05, 20470 MiB`.
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`.
- Baseline environment:
  - `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1`
  - `RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC=1`
  - `RTDL_OPTIX_COLLECT_K_DEFER_MERGE_SYNC_DIAGNOSTIC=1`
- Baseline artifact on pod: `docs/reports/goal1645_countsfix_baseline_262144_repeats5.json`.

## Rejected Candidates

### Larger CUB Tile Sort

The attempted larger CUB tile variants were meant to reduce tile count and merge work:

- `4096` rows/tile using `256 threads * 16 items/thread`: compiled but failed at runtime with `CUDA driver error: invalid argument`.
- `4096` rows/tile using `512 threads * 8 items/thread`: compiled but failed at runtime with `CUDA driver error: invalid argument`.
- `3072` rows/tile using `256 threads * 12 items/thread`: compiled but failed at runtime with `CUDA driver error: invalid argument`.

No larger CUB tile diagnostic flag is retained in the runtime.

### Raised Parallel-Compact Minimum Capacity

The min-capacity sweep tried to reduce early merge launch count by routing small merge levels through the older single-kernel merge path. After fixing the fallback path to preserve the device-counts contract, parity progressed, but the first fallback merge level showed about `1.08 ms` synchronization time for `RTDL_OPTIX_COLLECT_K_PARALLEL_COMPACT_MIN_CAPACITY=8192`. That is far slower than the current fastest baseline and not a viable good-win candidate.

The fallback counts fix is retained because it preserves correctness for opt-in min-capacity experiments that combine the fallback merge path with device-resident counts. It is not enabled by default and does not change the fastest default path.

## Baseline Reference

The same-pod fastest baseline for `candidate_count=262144`, `row_width=2`, and `repeats=5` recorded:

| field | value |
| --- | ---: |
| median_ms | 0.686459 |
| tile_count | 128 |
| merge_levels | 7 |
| merge_launches | 27 |
| total_ms | 0.639800 |
| merge_launch_ms | 0.433014 |

## Next Direction

The good target remains open. The rejected candidates show that simply using larger CUB tiles or falling back to the old merge kernel is not enough. The next candidate should focus on a genuinely production-shaped merge-chain reduction, such as a safe no-duplicate fast path, a better compact-level fusion, or a prepared multi-level merge graph that is measured against the accepted path before promotion.

## Claim Boundary

This is internal diagnostic evidence only. It does not authorize public speedup wording, true zero-copy wording, stable `COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording, whole-application speedup claims, release tags, or release action.
