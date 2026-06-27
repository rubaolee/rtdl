# Goal1652 v1.6.x OptiX Collect-K Non-CUB Tile Shape Probe

## Verdict

`noncub_4096_tile_shape_rejected`

This records a rejected OptiX `COLLECT_K_BOUNDED` performance candidate for the
v1.6.x performance lane.

## Question

After Goal1650, the fastest accepted A4500 path for `candidate_count=262144`
uses CUB tile sort with `tile_count=128`, `merge_levels=7`, and
`merge_launches=27`.

The candidate tested here asked whether a non-CUB `4096` row tile shape could
win by cutting the tile count to `64`, reducing the merge tree to
`merge_levels=6` and `merge_launches=14`.

## Measured Scope

- Host: pod `root@213.173.98.25 -p 17374`.
- GPU: NVIDIA RTX A4500.
- Commit: `04549531b46455287911fcf5b21f6145247c2c16`.
- OptiX SDK: `/root/vendor/optix-sdk`.
- CUDA prefix: `/usr/local/cuda`.
- Candidate count: `262144`.
- Repeats: `5`.

## Results

Baseline `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1`:

- Accepted evidence: `true`.
- Parity: `true`.
- `tile_count=128`.
- `sort_launches=1`.
- `merge_levels=7`.
- `merge_launches=27`.
- `total_ms=0.675769`.
- `sort_sync_ms=0.105973`.
- `merge_sync_ms=0.323371`.

Non-CUB `4096` tile candidate:

- Accepted Goal1506 evidence: `false` because this was an explicit
  diagnostic shape outside Goal1506's expected topology.
- Parity: `true`.
- Smoke classification: `local_fallback_smoke_only=true`.
- `tile_count=64`.
- `sort_launches=64`.
- `merge_levels=6`.
- `merge_launches=14`.
- `total_ms=73.3285`.
- `sort_sync_ms=57.8657`.
- `merge_sync_ms=14.988`.

Artifacts:

- `docs/reports/goal1652_fastest_cub_262144.json`
- `docs/reports/goal1652_fastest_cub_262144.jsonl`
- `docs/reports/goal1652_fastest_cub_262144.md`
- `docs/reports/goal1652_noncub_4096_262144.json`
- `docs/reports/goal1652_noncub_4096_262144.jsonl`
- `docs/reports/goal1652_noncub_4096_262144.md`

## Decision

`do_not_promote`

The non-CUB `4096` tile shape reduced tile count and merge launches, but it
replaced one CUB sort launch with 64 slower per-tile sort launches. The result
was roughly two orders of magnitude slower at this measured size. Future
v1.6.x work should preserve the CUB tile sort path for this count class and
look for improvements after CUB sorting, especially merge synchronization,
metadata handling, and final compact work.

## Claim Boundary

This report records a rejected diagnostic candidate only. It does not authorize
public speedup wording, stable `COLLECT_K_BOUNDED` promotion, fastest-candidate
promotion, release tags, or release action.
