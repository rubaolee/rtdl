# Goal3639 Segment-Pair Sparse-Grid RT Index Diagnostic

Date: 2026-06-06

Verdict: `accept-with-boundary`

## Purpose

Goal3635 showed that an all-hit crossing grid is a poor performance regime for
RT traversal: every possible pair hits, so a dense CuPy arithmetic kernel can be
faster. Goal3639 adds and measures sparse diagonal segment-pair cases where the
possible pair product is large but only one right segment intersects each left
segment.

This is the useful RT-index regime for the generic
`segment_pair_left_id_dense_count` contract:

- total possible pairs: `n * n`;
- actual hits: `n`;
- no hit-row materialization;
- default hot route only, with no optional ambiguity scan;
- validation downloads only.

## Artifacts

Machine artifacts:

- `docs/reports/goal3639_segment_pair_sparse_grid_a5000/summary.json`
- `docs/reports/goal3639_segment_pair_sparse_grid_a5000/large_summary.json`

Pod source state:

- source commit: `89bae35b`
- GPU: `NVIDIA RTX A5000, 8.6, 580.126.09`
- tracked source status: clean (`git_tracked_status_short == ""`)

## Correctness

All same-contract counts matched the analytic sparse-grid reference and the
CuPy dense baseline.

| Case | Pair Count | Expected Hits | OptiX Hits | Match |
| --- | ---: | ---: | ---: | --- |
| sparse_diagonal_grid_1024 | 1,048,576 | 1,024 | 1,024 | yes |
| sparse_diagonal_grid_2048 | 4,194,304 | 2,048 | 2,048 | yes |
| sparse_diagonal_grid_4096 | 16,777,216 | 4,096 | 4,096 | yes |
| sparse_diagonal_grid_8192 | 67,108,864 | 8,192 | 8,192 | yes |
| sparse_diagonal_grid_16384 | 268,435,456 | 16,384 | 16,384 | yes |
| sparse_diagonal_grid_32768 | 1,073,741,824 | 32,768 | 32,768 | yes |

## Diagnostic Timings

These timings are diagnostic only. The comparison is against the runner's CuPy
dense all-pairs strict-v0 kernel, not against a RayJoin paper implementation.

| Case | CuPy Dense Kernel Sec | CuPy Kernel+Validation Sec | OptiX Dense Wall Sec | OptiX Native Reduction Sec | CuPy Kernel / OptiX Wall |
| --- | ---: | ---: | ---: | ---: | ---: |
| sparse_diagonal_grid_1024 | 0.000225 | 0.006189 | 0.001376 | 0.000047 | 0.164x |
| sparse_diagonal_grid_2048 | 0.000755 | 0.006900 | 0.002425 | 0.000049 | 0.311x |
| sparse_diagonal_grid_4096 | 0.002918 | 0.003087 | 0.004571 | 0.000056 | 0.639x |
| sparse_diagonal_grid_8192 | 0.011601 | 0.011920 | 0.008880 | 0.000066 | 1.306x |
| sparse_diagonal_grid_16384 | 0.046351 | 0.053217 | 0.019356 | 0.000071 | 2.395x |
| sparse_diagonal_grid_32768 | 0.185518 | 0.189052 | 0.036127 | 0.000089 | 5.135x |

The crossover is clear: dense CuPy is better on small sparse grids once Python
wrapping and OptiX setup are included, but the prepared OptiX dense-count route
wins as the possible pair product grows while actual hits remain sparse.

## Interpretation

This explains the difference between Goal3635 and Goal3639:

- all-hit grids punish RT traversal because there is little spatial rejection;
- sparse grids reward the RT index because most potential pairs never become
  exact segment-pair work;
- the native counted phase remains tiny because the route counts accepted
  segment-pair hits by left id directly without materializing hit rows.

This is the performance direction that matters for RayJoin-like workloads, but
it is still not a RayJoin reproduction and not a public broad speedup claim.

## Boundary

This goal does not authorize:

- release readiness;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app benchmark claims;
- true zero-copy claims;
- RayJoin paper reproduction claims;
- making this route the native default for every segment-pair workload.

The result is a strong internal diagnostic: RTDL's generic segment-pair count
route has a credible sparse-index win over a dense CuPy baseline at large scale.
External claims still require representative datasets, agreed baselines, and
the required multi-AI release/claim consensus.
