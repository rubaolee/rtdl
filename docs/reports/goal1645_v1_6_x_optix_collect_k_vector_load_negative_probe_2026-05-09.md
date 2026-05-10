# Goal1645 v1.6.x OptiX Collect-K Vector-Load Negative Probe

## Verdict

`vector_load_candidate_rejected`

The 16-byte row-load candidate preserved parity but regressed the measured long `COLLECT_K_BOUNDED` path. The candidate code is not retained.

## Scope

- Candidate: replace final merge binary-search row loads with a `struct __align__(16)` row load helper.
- GPU: `NVIDIA RTX A4500, 550.127.05, 20470 MiB`.
- Baseline commit: `51c19ea1`.
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`.
- Environment:
  - `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1`
  - `RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC=1`
  - `RTDL_OPTIX_COLLECT_K_DEFER_MERGE_SYNC_DIAGNOSTIC=1`
  - `RTDL_OPTIX_COLLECT_K_FINAL_PAIR_MARK_EVENT_DIAGNOSTIC=1`
- Baseline artifact: `docs/reports/goal1645_ab_baseline_262144_repeats9.json`.
- Candidate artifact: `docs/reports/goal1645_ab_vector_load_262144_repeats9.json`.

## Result

| case | wrapper median ms | profile total ms | merge event ms | merge launch ms | parity |
| --- | ---: | ---: | ---: | ---: | --- |
| baseline | 0.681050 | 0.650591 | 0.380224 | 0.470255 | true |
| vector-load candidate | 0.735424 | 0.687792 | 0.378240 | 0.478145 | true |

Computed speedups:

- Wrapper median speedup: `0.926064x`.
- Profile total speedup: `0.945912x`.

## Interpretation

The aligned row-load helper did not reduce the merge-chain bottleneck. It slightly reduced the measured merge event field, but total and wrapper timings regressed. The compiler or memory path likely did not benefit enough from the explicit 16-byte row type to offset added register pressure or instruction scheduling changes.

## Next Direction

The good-win target remains open. The next candidate should not be another small load-shape rewrite. The remaining plausible path is a larger merge-chain restructuring, most likely a measured cooperative-kernel or multi-level dependency-chain probe that reduces actual merge pass overhead while preserving generic semantics.

## Claim Boundary

This is internal diagnostic evidence only. It does not authorize public speedup wording, true zero-copy wording, stable `COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording, whole-application speedup claims, release tags, or release action.
