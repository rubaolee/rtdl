# Goal3643 Segment-Pair Prepacked-Left Sparse Diagnostic

Date: 2026-06-06

Verdict: `accept-with-boundary`

## Purpose

Goal3639 showed that the generic OptiX segment-pair count route has a credible
sparse-index advantage once the possible pair product is large and true hits
remain sparse. Goal3643 isolates the next bottleneck: left-side Python packing
and native upload.

The runner now supports `--prepack-left-for-optix`. With this flag, the left
segment records are packed once before timing the OptiX dense-count call. This
does not change the contract or the native engine. It measures the hot route a
user can reach when the left input is already in RTDL's packed segment format.

## Artifact

Machine artifact:

- `docs/reports/goal3643_segment_pair_prepacked_left_sparse_a5000/summary.json`

Pod source state:

- source commit: `c4a1a3e0`
- GPU: `NVIDIA RTX A5000, 8.6, 580.126.09`
- tracked source status: clean (`git_tracked_status_short == ""`)
- runner flag: `prepack_left_for_optix == true`
- output cap: `max_counts_output == 4096`

## Correctness

All same-contract counts match the analytic sparse-grid reference and the CuPy
dense baseline.

| Case | Pair Count | Expected Hits | OptiX Hits | Match |
| --- | ---: | ---: | ---: | --- |
| sparse_diagonal_grid_8192 | 67,108,864 | 8,192 | 8,192 | yes |
| sparse_diagonal_grid_16384 | 268,435,456 | 16,384 | 16,384 | yes |
| sparse_diagonal_grid_32768 | 1,073,741,824 | 32,768 | 32,768 | yes |

## Diagnostic Timings

These timings are diagnostic only. The comparison is the same sparse-grid
same-contract comparison used in Goal3639: the runner's CuPy dense all-pairs
strict-v0 kernel versus RTDL/OptiX's prepared segment-pair count route.

| Case | CuPy Dense Kernel Sec | CuPy Total Sec | OptiX Packed-Left Count Sec | Left Prepack Sec | CuPy Kernel / OptiX Packed-Left Count |
| --- | ---: | ---: | ---: | ---: | ---: |
| sparse_diagonal_grid_8192 | 0.011594 | 0.018744 | 0.000385 | 0.008813 | 30.111x |
| sparse_diagonal_grid_16384 | 0.046418 | 0.048938 | 0.000604 | 0.017123 | 76.899x |
| sparse_diagonal_grid_32768 | 0.181169 | 0.187096 | 0.000654 | 0.034416 | 276.897x |

## Interpretation

The result is sharper than Goal3639:

- the RTDL/OptiX counted route is no longer the large cost center for sparse
  segment-pair count once the left side is already packed;
- left-side packing dominates one-shot calls, so adding the prepack cost back
  brings the route close to the old one-shot timing;
- this strongly motivates first-class packed/prepared left segment inputs, or a
  reusable device-resident left-side segment-set handle, before making stronger
  RayJoin-style performance claims.

In plain language: the engine-side RT traversal/count path is good in the sparse
regime, but the user-facing route still needs a better way to keep both sides
resident and reusable.

## Boundary

This goal does not authorize:

- release readiness;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app benchmark claims;
- true zero-copy claims;
- RayJoin paper reproduction claims;
- treating prepacked-left timing as one-shot app-wall timing.

The accepted claim is narrower: packed-left sparse segment-pair count is a
strong hot-route diagnostic, and it identifies reusable/prepared left inputs as
the next high-leverage generic runtime target.
