# Goal1653 v1.6.x OptiX Collect-K Deferred Merge Sync Remeasure

## Verdict

`defer_merge_sync_candidate_rejected_for_262144`

This remeasures `RTDL_OPTIX_COLLECT_K_DEFER_MERGE_SYNC_DIAGNOSTIC=1` after the
Goal1650 fastest-capacity fix made `candidate_count=262144` use the accepted
CUB tiled path under `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1`.

## Measured Scope

- Host: pod `root@213.173.98.25 -p 17374`.
- GPU: NVIDIA RTX A4500.
- Commit: `ad57f8193c5452ff0036a4c853860ea656d44a3d`.
- OptiX SDK: `/root/vendor/optix-sdk`.
- CUDA prefix: `/usr/local/cuda`.
- Candidate count: `262144`.
- Repeats: `5`.

## Results

Baseline `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1`:

- Accepted evidence: `true`.
- Parity: `true`.
- `total_ms=0.680568`.
- `sort_sync_ms=0.105803`.
- `merge_launch_ms=0.164694`.
- `merge_sync_ms=0.322667`.
- `final_pair_mark_sync_ms=0.048651`.

Deferred merge sync:

- Environment:
  `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1`,
  `RTDL_OPTIX_COLLECT_K_DEFER_MERGE_SYNC_DIAGNOSTIC=1`,
  `RTDL_OPTIX_COLLECT_K_FINAL_PAIR_MARK_EVENT_DIAGNOSTIC=1`.
- Accepted evidence: `true`.
- Parity: `true`.
- `total_ms=0.687409`.
- `sort_sync_ms=0.105922`.
- `merge_launch_ms=0.478683`.
- `merge_sync_ms=0.01464`.
- `merge_event_ms=0.379552`.
- `final_pair_pre_mark_wait_ms=0.257194`.
- `final_pair_mark_host_wait_ms=0.292234`.
- `final_pair_mark_sync_ms=0.307338`.

Artifacts:

- `docs/reports/goal1653_fastest_262144.json`
- `docs/reports/goal1653_fastest_262144.jsonl`
- `docs/reports/goal1653_fastest_262144.md`
- `docs/reports/goal1653_defer_merge_sync_262144.json`
- `docs/reports/goal1653_defer_merge_sync_262144.jsonl`
- `docs/reports/goal1653_defer_merge_sync_262144.md`

## Decision

`do_not_promote_for_262144`

Deferred merge synchronization changes where waiting is charged, but it does
not reduce end-to-end time for the corrected `262144` fastest path. It moves
the merge wait out of `merge_sync_ms` and into later final-pair waits, while
the median total time is slightly worse than the baseline.

## Claim Boundary

This report records a rejected diagnostic candidate for this measured count and
device. It does not authorize public speedup wording, stable
`COLLECT_K_BOUNDED` promotion, fastest-candidate promotion, release tags, or
release action.
