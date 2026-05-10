# Goal1642 v1.6.x OptiX Collect-K Deferred Merge Event Breakdown

## Verdict

`deferred_merge_work_explains_final_wait`

CUDA event timing shows that the large final-pair pre-mark wait is primarily deferred merge GPU work becoming visible at the final synchronization point, not a slow final-pair mark/materialize kernel.

## Scope

- Code change: extend the opt-in event diagnostic to record merge-level CUDA event time without adding per-level synchronization.
- Runtime flag: `RTDL_OPTIX_COLLECT_K_FINAL_PAIR_MARK_EVENT_DIAGNOSTIC=1`.
- Production effect: none. The diagnostic remains opt-in and is not enabled by `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE`.
- GPU: `NVIDIA RTX A4500, 550.127.05, 20470 MiB`.
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`.
- Probe environment:
  - `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1`
  - `RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC=1`
  - `RTDL_OPTIX_COLLECT_K_DEFER_MERGE_SYNC_DIAGNOSTIC=1`
  - `RTDL_OPTIX_COLLECT_K_FINAL_PAIR_MARK_EVENT_DIAGNOSTIC=1`
- Artifact: `docs/reports/goal1642_merge_event_262144_repeats5.json`.

## Result

For `candidate_count=262144`, `tile_count=128`, and `merge_levels=7`, median stage fields were:

| field | median_ms |
| --- | ---: |
| merge_event_ms | 0.382368 |
| merge_launch_ms | 0.481166 |
| merge_sync_ms | 0.014681 |
| final_pair_pre_mark_wait_ms | 0.276271 |
| final_pair_materialize_event_ms | 0.035072 |
| final_pair_mark_event_ms | 0.015136 |
| final_pair_mark_sync_ms | 0.326620 |
| total_ms | 0.692272 |

The result preserved parity: `same_candidate_rows=true` and `same_valid_count=true`.

## Interpretation

Goal1641 showed the final-pair materialize and mark kernels are too small to explain the final-pair wait. Goal1642 adds the missing piece: deferred merge GPU work is large enough to account for the wait that becomes visible at the final mark synchronization.

This changes the next optimization target. The primary remaining cost is the merge chain itself: launch count, level structure, intermediate compacting, and dependency layout. The next useful candidate should reduce the amount of merge work or reduce the number of merge launches, rather than moving the same four final kernels into another graph wrapper or rewriting the final mark kernel.

## Claim Boundary

This is internal diagnostic evidence only. It does not authorize public speedup wording, true zero-copy wording, stable `COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording, whole-application speedup claims, release tags, or release action.
