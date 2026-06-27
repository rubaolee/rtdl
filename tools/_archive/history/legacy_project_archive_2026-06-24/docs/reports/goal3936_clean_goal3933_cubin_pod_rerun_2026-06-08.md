# Goal3936 Clean Goal3933 CUBIN Pod Rerun

Date: 2026-06-08

## Purpose

Goal3933 repaired the OptiX shape-pair active-count pod blocker by loading the direct CUDA helper as CUBIN instead of PTX, and by removing host `<math.h>` dependencies from the early closed-shape CUDA strings. The first pod evidence was valid but intentionally carried a local source label because the repair was tested before the commit existed.

Goal3936 reruns the same combined queue from a fresh clean checkout of pushed `main` at commit `cd7fa65f`, so the evidence has no local source-dirty caveat.

## Pod

- GPU: NVIDIA RTX 4000 Ada Generation
- Driver: 550.127.05
- Clean source commit: `cd7fa65f`
- Source dirty list: empty
- Artifact directory: `docs/reports/goal3936_clean_goal3933_cubin_pod_rerun_2026-06-08/`

## Result

| Check | Result |
| --- | --- |
| Goal3927 combined queue | `pass` |
| Goal3931 evaluator | `accept_with_boundary` |
| Evaluator errors | none |
| RayJoin counts | all match |
| RTDBSCAN modes | unblocked and blocked both present |
| Claim boundaries | all closed |

## Representative Hot-Path Evidence

| Workload | RTDL/OptiX Hot Median (s) | Numba Hot Median (s) | RTDL/OptiX vs Numba | Route Decision |
| --- | ---: | ---: | ---: | --- |
| RayJoin PIP one-shot | 0.001797274 | 0.000443250 | 0.247x | Prefer Numba for this bounded one-shot scalar count |
| RayJoin LSI scalar count | 0.000091493 | 0.023096137 | 252.436x | Prefer RTDL OptiX prepared segment-pair count |
| RayJoin overlay active count | 0.000195540 | 0.039571896 | 202.372x | Prefer RTDL OptiX prepared shape-pair active count |
| RayJoin PIP repeated requests | 0.155315 ms/request at 100 requests | n/a | 1.232x vs single RTDL request | Prepared OptiX batch route amortizes setup |

RTDBSCAN remains unchanged in direction: the unblocked grouped stream is faster than the blocked candidate.

| RTDBSCAN Mode | Elapsed (s) | Decision |
| --- | ---: | --- |
| Unblocked grouped stream | 0.089630436 | Keep default |
| Blocked grouped stream | 0.393740270 | Slower; do not promote |

## Boundary

This is internal engineering evidence only. It does not authorize a release, public speedup wording, broad RT-core claims, whole-app speedup claims, automatic partner selection claims, true-zero-copy claims, RayJoin paper reproduction claims, or RTDBSCAN paper reproduction claims.

The main value of this goal is evidence hygiene: the Goal3933 repair now has both external review and a clean post-commit pod rerun.
