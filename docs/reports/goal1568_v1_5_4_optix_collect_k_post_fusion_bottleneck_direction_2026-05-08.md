# Goal 1568: post-fusion OptiX collect-k bottleneck direction

## Verdict

After Goal 1565 and Goal 1567, both compact-level materialize+mark fusion
routes are measured negative. The fresh accepted long-case profile at
`fe0570bf` shows the remaining bottleneck is split between merge launches and
merge execution/synchronization, not a pure launch-count problem.

Do not continue compact-level fusion unless a narrower diagnostic first proves
that predecessor lookup or merge-path work can be removed cheaply.

## Scope

- Pod: `root@157.157.221.29 -p 22942`
- Git commit: `fe0570bf`
- Library: `build/librtdl_optix.so`
- Profile artifact: `docs/reports/goal1568_v1_5_4_optix_collect_k_post_fusion_longcase_profile_2026-05-08.json`
- Counts: `65537`, `131072`
- Repeats: `5`
- Flag set:
  `RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT=1`,
  `RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT=1`,
  `RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL=1`,
  `RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE=1`,
  `RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT=1`,
  `RTDL_OPTIX_COLLECT_K_DERIVED_LEVEL_DESCRIPTORS=1`,
  `RTDL_OPTIX_COLLECT_K_DEVICE_LEVEL_COUNTS=1`,
  `RTDL_OPTIX_COLLECT_K_DEVICE_FINAL_COUNTS=1`.

## Current Profile

| candidates | total ms | merge launch ms | merge sync ms | sort sync ms | carry copy ms | merge launches |
|---:|---:|---:|---:|---:|---:|---:|
| 65537 | 0.281784 | 0.082206 | 0.084168 | 0.036219 | 0.035588 | 23 |
| 131072 | 0.308274 | 0.089019 | 0.121229 | 0.054724 | 0.000000 | 23 |

Stage share of total:

| candidates | merge launch | merge sync | sort sync | carry copy | tile metadata |
|---:|---:|---:|---:|---:|---:|
| 65537 | 29.2% | 29.9% | 12.9% | 12.6% | 2.7% |
| 131072 | 28.9% | 39.3% | 17.8% | 0.0% | 2.5% |

## Interpretation

Launch overhead is still material, but it is not dominant enough to justify
expensive fusion. Goal 1565 saved a launch but paid reset and atomic costs.
Goal 1567 saved the same launch without atomics, but paid extra merge-path
binary-search work. Both preserved parity and still lost.

The profile now points to three more plausible directions:

- For odd tile counts such as `65537`, the five carry copies cost about
  `0.035588 ms`, or `12.6%` of total. A carry-reference or carry-alias design
  may be more promising than more compact fusion.
- For both long cases, merge sync time is comparable to or larger than merge
  launch time. A better merge algorithm or less work per merge level may matter
  more than shaving another launch.
- Persistent graph/topology reuse remains plausible only for repeated
  compatible calls. It should not be retried as per-call/per-level graph update,
  which Goal 1560 already rejected.

## Next Direction

The next local design target should be carry-copy elimination for odd tile
counts, because it attacks a measured cost that fusion did not address and does
not require changing duplicate/mark semantics.

The first diagnostic should be a plan or probe for replacing carry segment
copies with segment descriptor aliasing across merge levels. It must preserve
the app-generic `COLLECT_K_BOUNDED` contract, keep production unchanged until
measured, and prove parity on odd tile counts before timing is interpreted.

This result is diagnostic only and does not authorize public speedup wording.
