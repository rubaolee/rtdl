# Goal 1544: OptiX COLLECT_K_BOUNDED Launch-Orchestration Negative Results

## Verdict

No new accepted performance improvement is recorded in this round. Goal 1543 remains the strongest measured OptiX `COLLECT_K_BOUNDED` row-width-2 experimental path:

`RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1 RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1 RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL=1 RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE=1`

Two launch-orchestration follow-ups were tested on the same RTX 2000 Ada pod and rejected.

## Scope

- Pod: `root@213.173.110.196 -p 24309`
- Device: `NVIDIA RTX 2000 Ada Generation`
- Base accepted commit before experiments: `9062aa774a33e2857facf90411e4da8911fa2b0a`
- OptiX SDK: `/root/vendor/optix-sdk`
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`
- These were exploratory working-tree probes, not accepted clean Git evidence.

## Rejected: Higher Parallel-Compact Thresholds

The existing threshold knob `RTDL_OPTIX_COLLECT_K_PARALLEL_COMPACT_MIN_CAPACITY` was swept to see whether the old one-launch serial merge became attractive after workspace reuse removed allocation overhead.

It did not. Raising the threshold forces broad merge levels onto the single-thread serial merge kernel and quickly dominates runtime.

Representative median totals:

| min capacity | candidates 4097 | candidates 65537 | candidates 131072 |
|---:|---:|---:|---:|
| 4096 | 0.154116 ms | 0.432537 ms | 0.600233 ms |
| 8192 | 0.526240 ms | 1.106860 ms | 1.215550 ms |
| 16384 | 0.814602 ms | 2.546930 ms | 2.612480 ms |
| 32768 | 0.785550 ms | 5.295120 ms | 5.356400 ms |
| 65536 | 0.785231 ms | 10.809800 ms | 10.944300 ms |
| 131072 | 0.783541 ms | 16.921100 ms | 19.868400 ms |
| 262144 | 0.785310 ms | 21.224600 ms | 33.552600 ms |

Conclusion: keep the Goal 1543 compact threshold behavior. The serial merge kernel is useful as a simple fallback, not as a long-count performance path.

## Rejected: Serial Final Merge

An opt-in working-tree experiment reduced the final two-segment merge from three compact launches to one serial merge launch.

The launch count improved, but device work exploded because the final serial merge is single-threaded over the largest segment.

Measured exploratory medians:

| candidates | total ms | merge sync ms | merge launches |
|---:|---:|---:|---:|
| 4097 | 0.376225 | 0.258461 | 4 |
| 65537 | 4.471440 | 4.072320 | 16 |
| 131072 | 12.413200 | 11.956400 | 16 |

Conclusion: do not replace the final parallel compact with the serial merge kernel.

## Inconclusive: Remove Pre-Download Synchronize

Another working-tree experiment removed the explicit `cuStreamSynchronize` before the synchronous `cuMemcpyDtoH` block-count download in the compact path.

Measured exploratory medians:

| candidates | total ms |
|---:|---:|
| 4097 | 0.135685 |
| 65537 | 0.431997 |
| 131072 | 0.561612 |

This was not accepted because it did not improve the largest target count versus Goal 1543's clean `0.545801 ms` result.

## Next Direction

The remaining bottleneck is not allocation and not simple threshold tuning. It is the structural dependency in the compact path:

1. materialize sorted merged rows,
2. mark/count unique rows per block,
3. compute per-block and per-pair offsets,
4. compact into the next segment.

Useful next work likely requires a real algorithmic change, such as a deterministic device-side segmented prefix/compact design, a prepared execution model that amortizes host orchestration across repeated calls, or a CUDA graph design that can preserve parity while handling per-level counts.

## Claim Boundary

This report records rejected internal experiments only. It does not authorize public speedup wording, true zero-copy wording, whole-app claims, stable primitive promotion, or release action.
