# Goal1630 v1.6.x OptiX Collect-K Extended 128-Tile Diagnostic

## Verdict

`extended_128_tile_diagnostic_candidate_recorded`

An opt-in diagnostic gate was added for the experimental OptiX
`COLLECT_K_BOUNDED` row-width-2 tiled path:
`RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC=1`.

The default tiled boundary remains `131072` candidates. With the diagnostic
enabled, the tiled path extends to `262144` candidates by expanding the native
workspace and descriptor capacity from 64 tile segments to 128 tile segments and
from 512 prefix blocks to 1024 prefix blocks.

## Scope

- GPU: `NVIDIA RTX A4500`, driver `550.127.05`, `20470 MiB`.
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`.
- Runner: `scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py`.
- Candidate count: `262144`.
- Diagnostic environment:
  - `RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC=1`
  - `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1`
  - optional comparison row also uses
    `RTDL_OPTIX_COLLECT_K_DEFER_MERGE_SYNC_DIAGNOSTIC=1`
- Artifacts:
  - `docs/reports/goal1630_extended_128_tile_262144_probe.json`
  - `docs/reports/goal1630_extended_128_tile_262144_nodefer_repeats5.json`
  - `docs/reports/goal1630_extended_128_tile_262144_defer_repeats5.json`

## Results

The single-run acceptance probe completed in 4 seconds and recorded:

- accepted Goal1506 evidence: `true`
- native path: `row_width2_bounded_multi_tile_sort_merge`
- tile count: `128`
- merge levels: `7`
- merge launches: `27`
- median stage total: `0.613750 ms`

The repeats=5 comparison kept parity and measured:

| Count | No-defer total ms | Defer total ms | Delta ms | No-defer merge sync ms | Defer merge sync ms | No-defer merge launch ms | Defer merge launch ms | Tile count | Parity |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 262144 | 0.682102 | 0.629871 | -0.052231 | 0.316548 | 0.015261 | 0.174938 | 0.434384 | 128 | true |

## Interpretation

The original large-count timeout was caused by leaving the optimized tiled path,
not by a deferred-merge-sync regression. This diagnostic extends the optimized
tiled path one scale tier further, from 64 to 128 tile segments, and the A4500
evidence confirms that `262144` candidates no longer fall back to
`dynamic_row_width_single_thread_fallback` when the diagnostic is enabled.

The deferred merge-sync diagnostic remains useful at this larger tile count,
but the measurement is still internal and narrow: one GPU model, one extended
scale point, and the experimental collect-k path only.

The diagnostic should not be interpreted as a dynamic memory reclamation
feature. If a long-lived process enables the extended workspace first and later
disables the environment variable, the reusable workspace can remain at the
larger 128-tile capacity for that process. This is safe for correctness because
later writes stay within the requested bounds, but it is another reason to keep
the path internal and opt-in.

## Next Work

1. Keep `RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC` opt-in.
2. Run focused collect-k regression with the extended diagnostic enabled before
   considering it for any candidate bundle.
3. Ask Claude and Gemini to review the native workspace-growth and descriptor
   capacity changes before promotion beyond internal measurement.

## Claim Boundary

This report is internal v1.6.x performance diagnostic evidence only. It does
not authorize public speedup wording, true zero-copy wording, stable
`COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording, whole-application speedup
claims, release tags, or release action.
