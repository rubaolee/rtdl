# Goal1637 v1.6.x OptiX Collect-K Final-Pair Mark Event Probe

## Verdict

`final_pair_mark_wait_not_kernel_time`

CUDA event timing shows that the final-pair mark kernel itself is not the dominant cost. The host-visible `final_pair_mark_sync_ms` is mostly stream wait / queued dependency time.

## Scope

- Code change: opt-in profile-only CUDA event timing around the final-pair mark kernel.
- Runtime flag: `RTDL_OPTIX_COLLECT_K_FINAL_PAIR_MARK_EVENT_DIAGNOSTIC=1`.
- The flag is not enabled by `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE`.
- GPU: `NVIDIA RTX A4500, 550.127.05, 20470 MiB`.
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`.
- Probe environment:
  - `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1`
  - `RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC=1`
  - `RTDL_OPTIX_COLLECT_K_DEFER_MERGE_SYNC_DIAGNOSTIC=1`
  - `RTDL_OPTIX_COLLECT_K_FINAL_PAIR_MARK_EVENT_DIAGNOSTIC=1`
- Artifact: `docs/reports/goal1637_final_pair_mark_event_262144_repeats5.json`.

## Result

For `candidate_count=262144`, `tile_count=128`, `merge_levels=7`, median stage fields were:

| field | median_ms |
| --- | ---: |
| final_pair_mark_sync_ms | 0.328621 |
| final_pair_mark_event_ms | 0.014816 |
| final_pair_mark_host_wait_ms | 0.313645 |
| final_pair_prefix_host_ms | 0.016100 |
| final_pair_compact_launch_ms | 0.003791 |
| merge_launch_ms | 0.440395 |
| total_ms | 0.642961 |

The mark kernel event time is small. The expensive part is the host-observed wait around that point in the default stream pipeline.

## Interpretation

Do not optimize the mark kernel first. The evidence points to stream dependency / dispatch accounting as the next performance target. The next useful probe should investigate CUDA graph replay or stream-dependency structure for the final merge/mark/prefix/compact chain.

## Claim Boundary

This is internal profiling evidence only. It does not authorize public speedup wording, true zero-copy wording, stable `COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording, whole-application speedup claims, release tags, or release action.
