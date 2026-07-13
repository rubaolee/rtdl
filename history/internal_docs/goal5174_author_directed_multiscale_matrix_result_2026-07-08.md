# Goal5174 Author-Directed Multiscale Matrix Result

Date: 2026-07-08

## Verdict

```text
completed_author_directed_multiscale_matrix__implemented_review_pending
```

Goal5174 records a same-POD multiscale matrix for the current X-HD Level B route:

```text
generic 3-D cell-MBR route
native OptiX frontier collector
native inline-nearest payload reduction
native-unsorted frontier row order
generic Numba seed and continuation executors
author-directed input1-to-input2 mode
```

All five representative Stanford graphics cases matched author `HDResult`.

This is implemented and POD-validated. It is not externally reviewed yet.

## Why This Goal Exists

Goal5173 proved and implemented the production route mode that matches the
author contract: directed input1-to-input2. Goal5174 checks that this current
route is stable across the representative scale ladder already used in the
X-HD Level B workstream:

```text
sample256
sample1024
sample2048
sample4096
res4full
```

This turns the current best route from a single res4full point into a
multiscale profile.

## POD Command

```text
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py \
  --author-bin /tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  --cases sample256,sample1024,sample2048,sample4096,res4full \
  --backend optix \
  --validation-mode author-only \
  --rtdl-repeat-count 5 \
  --frontier-nearest-executor numba_parallel \
  --frontier-row-order native \
  --frontier-inline-nearest \
  --direction-mode directed-a-to-b \
  --summary Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_goal5174_author_directed_multiscale_matrix_pod.json
```

## Evidence Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_goal5174_author_directed_multiscale_matrix_pod.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.seeded_performance_matrix.v1
```

## Result Table

All times below are medians from the artifact. RTDL route time is the in-process
route computation after loading/preprocessing. RTDL total time includes input
loading and route execution. Author `Running.AvgTime` is the author's internal
reported timing field and is not a denominator-aligned ratio target.

| Case | Points A | Points B | Matched | Author AvgTime | RTDL Route | RTDL Total | Load | Abs Diff |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| sample256 | 256 | 256 | true | 4.017 ms | 3.07 ms | 5.55 ms | 1.77 ms | 2.63e-09 |
| sample1024 | 1024 | 1024 | true | 5.001 ms | 5.82 ms | 19.02 ms | 12.35 ms | 3.72e-09 |
| sample2048 | 2048 | 2048 | true | 4.049 ms | 6.35 ms | 22.94 ms | 15.59 ms | 5.04e-09 |
| sample4096 | 4096 | 4096 | true | 4.276 ms | 10.63 ms | 36.50 ms | 23.70 ms | 6.27e-09 |
| res4full | 5205 | 7108 | true | 4.468 ms | 14.92 ms | 53.98 ms | 35.51 ms | 4.44e-09 |

Direction policy:

```text
direction_mode = directed-a-to-b
directed_b_to_a = null
```

Native symbol:

```text
rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3
```

Ratio policy:

```text
ratios_authorized = false
author_avg_vs_rtdl_route_ratio = null
author_wall_vs_rtdl_total_ratio = null
```

## Work Counts

The author-directed route performs only the A->B direction. Candidate-distance
evaluation counts in the RTDL route were:

| Case | Initial Candidate Distance Evaluations | Offload Continuation Evaluations | Frontier Rows |
|---|---:|---:|---:|
| sample256 | 566 | 0 | 0 |
| sample1024 | 6492 | 0 | 0 |
| sample2048 | 24111 | 0 | 0 |
| sample4096 | 92449 | 0 | 0 |
| res4full | 193317 | 7354 | 98 |

Interpretation: for the smaller samples, the native inline-nearest route fully
settles the nearest witnesses without offload rows. On full public res4, a small
offload frontier remains and is handled by the generic Numba continuation.

## What This Proves

- The current author-directed RTDL route matches author `HDResult` across five
  representative same-source Stanford graphics cases.
- The route remains stable from sample256 through the full public res4 pair.
- The route records a current multiscale profile for future regressions and
  reviews.
- The `directed-a-to-b` production mode stays consistent across the scale
  ladder.

## What This Does Not Prove

- It does not prove full X-HD paper reproduction.
- It does not prove exact paper dataset reproduction.
- It does not authorize an author-vs-RTDL speedup or parity ratio.
- It does not align author `Running.AvgTime` with RTDL route time.
- It does not claim the RTDL route is the author's fused X-HD RT-core algorithm.
- It does not claim exact X-HD paper Figure reproduction.

## Boundary

This is Level B same-source representative evidence:

```text
public Stanford graphics PLYs
deterministic samples and full public res4 pair
author hd_exec used as the value oracle
RTDL route uses generic system primitives
```

It is not Level C exact paper dataset evidence because the original paper input
files/hashes are still unavailable.

## Updated Artifacts

Manifest updated:

```text
Paper-reproduction-apps/x-hd-paper/data/manifest.json
```

New result artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_goal5174_author_directed_multiscale_matrix_pod.json
```

Review register updated:

```text
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
```

Status:

```text
Goal5174 implemented; review pending
```
