# Goal2952: Hausdorff Target-8192 Default Tuning

Date: 2026-06-01
Status: pod sweep passed

## Purpose

The post-Goal2950 canonical packet passed, but its performance triage exposed a
fresh Hausdorff/X-HD weak row: RTDL/OptiX exact Hausdorff was `1.346x` slower
than the optimized CuPy grid baseline on the 8192 x 8192 canonical fixture.

Goal2952 tests whether this is a missing primitive or an app-level grouping
default issue. The answer is grouping: the existing reduced nearest-witness
path is faster when target groups are coarser.

## Pod Evidence

Pod target: `root@69.30.85.171 -p 22167`

Source commit for sweep: `17b477944a5c15087148c651227d498f506ec0f6`

Artifacts:

- `docs/reports/goal2952_hausdorff_target8192_sweep_pod/goal2952_hd_sweep.json`
- `docs/reports/goal2952_hausdorff_target8192_sweep_pod/goal2952_hd16384_target8192_repeat7.json`

8K sweep, exact 8192 x 8192 fixture:

| Method | Target points/group | Median sec | Ratio vs CuPy `0.008314s` |
| --- | ---: | ---: | ---: |
| reduced | `1024` | `0.007963` | `0.958x` |
| reduced | `2048` | `0.007830` | `0.942x` |
| reduced | `4096` | `0.007881` | `0.948x` |
| reduced | `8192` | `0.007006` | `0.843x` |
| seeded/pruned | `1024` | `0.013020` | `1.566x` |
| seeded/pruned | `2048` | `0.013182` | `1.586x` |
| seeded/pruned | `4096` | `0.013126` | `1.579x` |
| seeded/pruned | `8192` | `0.013116` | `1.578x` |

16K confirmation:

| Points | Target points/group | RTDL sec | CuPy sec | Ratio |
| ---: | ---: | ---: | ---: | ---: |
| `16384 x 16384` | `8192` | `0.013721` | `0.015722` | `0.873x` |

All measured RTDL rows matched the exact CuPy baseline with zero distance error
and used RTDL/OptiX RT traversal. The seeded/pruned variant is slower on this
dense canonical fixture and remains a workload-specific option, not the default.

## Change

`scripts/goal2801_hausdorff_xhd_v25_canonical_entrypoint.py` now defaults to:

```text
DEFAULT_REDUCED_TARGET_POINTS_PER_GROUP = 8192
GOAL2801_ENTRYPOINT_VERSION = rtdl.goal2801.hausdorff_xhd_v2_5_canonical_entrypoint.v3.reduced_target8192
```

## Boundary

This is an app-level parameter/default tuning change. It does not add
Hausdorff-specific native ABI names, does not customize the native engine, and
does not authorize public speedup, whole-app speedup, broad RT-core, X-HD
reproduction, or v2.5 release claims.
