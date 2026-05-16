# Goal2114: Hausdorff Pre-Pod Performance Tuning

Date: 2026-05-16

Status: implemented and locally smoke-tested.

## Question

Before starting an expensive RTX pod for serious Hausdorff performance testing,
should we do any more local tuning?

Answer: yes, one small but important orchestration cleanup was worth doing
first.

## Tuning applied

`rtdl_rt_nearest_witness` already used two generic RTDL/OptiX primitives:

- fixed-radius threshold decisions to find an upper-bound witness radius;
- fixed-radius nearest-witness rows to compute exact directed HD witnesses.

Before this goal, the exact RT witness method called threshold search as a
separate high-level function and then opened fresh prepared scenes for witness
traversal. This could measure Python orchestration overhead and prepared-scene
re-entry instead of the best current user-level v2 program.

This goal changes the user-level algorithm so each direction prepares the target
scene once, then runs threshold search and nearest-witness traversal on that
same prepared object.

This keeps the native engine app-agnostic. The engine still only exposes generic
fixed-radius decision and nearest-witness primitives; Hausdorff logic remains in
Python.

## Local result

Host: local Linux smoke machine `192.168.1.20`, GTX 1070, OptiX SDK
`/home/lestat/vendor/optix-dev`.

8192 x 8192 language lab:

| Method | Before | After prepare reuse | Correct? |
| --- | ---: | ---: | --- |
| `rtdl_rt_nearest_witness` | 1.125322 s | 1.084202 s | yes |
| `rtdl_rt_threshold_search` | 1.075866 s | 1.079058 s | interval matches |
| `rtdl_v2_user_cuda` | 0.009575 s | 0.009522 s | yes |
| `cuda_cpp` | 0.010110 s | 0.010054 s | yes |
| `openmp_cpu` | 0.065391 s | 0.065808 s | yes |

Artifact:

- `docs/reports/hausdorff_v2_language_lab_local_optix_8192_prepare_reuse.json`

## Threshold tolerance probe

The exact RT witness path can seed its witness radius with a threshold upper
bound. Coarser tolerance reduces threshold iterations but also makes the witness
radius looser, which can increase traversal candidates.

8192 x 8192, exact RT witness only:

| Threshold tolerance | Iterations | Witness radius | Exact match? | Elapsed |
| --- | ---: | ---: | --- | ---: |
| `1e-2` | 18 | 0.1238197929297542 | yes | 1.432654 s |
| `1e-3` | 24 | 0.12038035423726103 | yes | 1.500041 s |
| `1e-4` | 32 | 0.1200579068598398 | yes | 1.633700 s |

Artifacts:

- `docs/reports/hausdorff_v2_language_lab_local_optix_8192_rt_tol_1e-2.json`
- `docs/reports/hausdorff_v2_language_lab_local_optix_8192_rt_tol_1e-3.json`
- `docs/reports/hausdorff_v2_language_lab_local_optix_8192_rt_tol_1e-4.json`

These isolated tolerance timings include fresh process/setup effects and should
not replace the full matrix, but they show the design tradeoff clearly.

## Pre-pod conclusion

The repo is now ready for a serious pod run. More local tuning is unlikely to
change the main conclusion because the remaining performance gap is algorithmic:

- the current exact RT path still performs many fixed-radius decision launches;
- it still traverses point AABBs directly rather than X-HD-style grouped cells;
- it lacks estimator pruning and heavy-cell CUDA/CuPy fallback;
- the local GTX 1070 is only a smoke host.

The pod should measure:

- full language lab at larger sizes;
- exact RT witness with several threshold tolerances;
- explicit-radius/oracle-radius lower-bound traversal timing if we want to
  isolate traversal from threshold search;
- RTDL+CuPy exact path as the current best v2 exact HD baseline.

Do not claim broad RT-core HD speedup unless the pod plus algorithmic evidence
actually supports it.
