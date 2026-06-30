# Goal1641 v1.6.x OptiX Collect-K Final-Pair Event Breakdown

## Verdict

`pre_mark_wait_dominates_final_pair_sync`

The final-pair materialize and mark kernels are not the dominant cost. CUDA event timing shows that most of the host-visible final-pair mark synchronization time is queued pre-mark wait.

## Scope

- Code change: extend the opt-in `RTDL_OPTIX_COLLECT_K_FINAL_PAIR_MARK_EVENT_DIAGNOSTIC=1` path to also record materialize event timing and residual pre-mark wait.
- Production effect: none. The diagnostic remains opt-in and is not enabled by `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE`.
- GPU: `NVIDIA RTX A4500, 550.127.05, 20470 MiB`.
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`.
- Probe environment:
  - `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1`
  - `RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC=1`
  - `RTDL_OPTIX_COLLECT_K_DEFER_MERGE_SYNC_DIAGNOSTIC=1`
  - `RTDL_OPTIX_COLLECT_K_FINAL_PAIR_MARK_EVENT_DIAGNOSTIC=1`
- Artifact: `docs/reports/goal1641_final_pair_materialize_event_262144_repeats5.json`.

## Result

For `candidate_count=262144`, `tile_count=128`, and `merge_levels=7`, median stage fields were:

| field | median_ms |
| --- | ---: |
| final_pair_materialize_launch_ms | 0.006280 |
| final_pair_materialize_event_ms | 0.034656 |
| final_pair_mark_sync_ms | 0.323570 |
| final_pair_mark_event_ms | 0.014976 |
| final_pair_mark_host_wait_ms | 0.308242 |
| final_pair_pre_mark_wait_ms | 0.274066 |
| final_pair_prefix_host_ms | 0.016761 |
| final_pair_compact_launch_ms | 0.003650 |
| merge_launch_ms | 0.443994 |
| merge_sync_ms | 0.014621 |
| total_ms | 0.647400 |

The result preserved parity: `same_candidate_rows=true` and `same_valid_count=true`.

## Interpretation

The measured wait is not explained by the final materialize kernel or the final mark kernel. Together their CUDA event time is about `0.049632 ms`, while the residual pre-mark wait is about `0.274066 ms`.

This means the next useful optimization is not another mark/materialize kernel rewrite. The likely production target is the dependency structure leading into the final pair: reduce queued work that only becomes visible at the final mark synchronization point, or move the remaining final sequence to a measured dependency path that does not force this host-visible wait.

## Claim Boundary

This is internal diagnostic evidence only. It does not authorize public speedup wording, true zero-copy wording, stable `COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording, whole-application speedup claims, release tags, or release action.
