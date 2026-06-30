# Goal1655 v1.6.x OptiX Collect-K Skip Tile Overflow Probe

## Verdict

`skip_tile_overflow_check_candidate_rejected`

This records a rejected opt-in diagnostic candidate that skipped downloading
per-tile overflow flags in the CUB tile-sort path.

## Question

The accepted fastest CUB path downloads `tile_overflowed` metadata for every
tile. At `candidate_count=262144`, this contributes 128 metadata fields even
though each CUB tile has capacity equal to its tile input size. The diagnostic
asked whether skipping that safety metadata download would reduce total time.

## Measured Scope

- Host: pod `root@213.173.98.25 -p 17374`.
- GPU: NVIDIA RTX A4500.
- Base commit: `8c740ae8...` plus a local diagnostic patch.
- OptiX SDK: `/root/vendor/optix-sdk`.
- CUDA prefix: `/usr/local/cuda`.
- Candidate count: `262144`.
- Repeats: `9`.

## Results

Baseline `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1`:

- Accepted evidence: `true`.
- Parity: `true`.
- `total_ms=0.637297`.
- `tile_metadata_download_ms=0.00868`.
- `merge_sync_ms=0.334689`.
- `metadata_fields_downloaded=129`.

Skip tile overflow diagnostic:

- Environment:
  `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1`,
  `RTDL_OPTIX_COLLECT_K_SKIP_TILE_OVERFLOW_CHECK_DIAGNOSTIC=1`.
- Accepted Goal1506 evidence: `false` because this was an explicit diagnostic
  topology outside the expected metadata shape.
- Parity: `true`.
- Smoke classification: `local_fallback_smoke_only=true`.
- `total_ms=0.677178`.
- `tile_metadata_download_ms=0.00021`.
- `merge_sync_ms=0.316788`.
- `metadata_fields_downloaded=1`.

Artifacts:

- `docs/reports/goal1655_baseline_262144.json`
- `docs/reports/goal1655_baseline_262144.jsonl`
- `docs/reports/goal1655_baseline_262144.md`
- `docs/reports/goal1655_skip_tile_overflow_262144.json`
- `docs/reports/goal1655_skip_tile_overflow_262144.jsonl`
- `docs/reports/goal1655_skip_tile_overflow_262144.md`

## Decision

`do_not_promote`

The diagnostic reduced the targeted metadata download, but the end-to-end
median total time did not improve. The candidate code is not retained.

## Claim Boundary

This report records a rejected diagnostic candidate only. It does not authorize
public speedup wording, stable `COLLECT_K_BOUNDED` promotion, fastest-candidate
promotion, release tags, or release action.
