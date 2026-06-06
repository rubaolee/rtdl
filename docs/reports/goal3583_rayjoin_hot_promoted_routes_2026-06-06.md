# Goal3583: RayJoin Promoted Routes Hot Prepared-Query Measurement

Date: 2026-06-06

## Purpose

Goal3582 promoted the strengthened RayJoin runner from the stale generic
`prepared_optix` route to the newer app-facing promoted routes:

- `prepared_optix_cupy_refined_pip`
- `prepared_optix_left_id_dense_count`
- `prepared_optix_shape_pair_active_count`

The first A5000 rerun exposed a measurement-contract problem rather than a
native performance problem: the strengthened runner repeated cases by launching
fresh Python processes, while these promoted routes are prepared-handle reuse
routes. That made the packet mostly measure CUDA/OptiX/CuPy setup around the
route instead of the hot query contract.

Goal3583 fixes the measurement contract without changing the native engine:

- the three promoted RayJoin routes now accept `--repeat` and `--warmup`;
- the strengthened runner requests `--repeat 5 --warmup 1` for promoted OptiX
  rows;
- the primary metric is now the unified hot prepared-query median
  `phases_sec.prepared_query_sec`;
- each promoted payload records `repeat_protocol` with repeat, warmup, measured
  total, and reported metric.

The native engine remains app-agnostic. RayJoin interpretation, fixture choice,
prepared-handle reuse policy, and CuPy exact PIP refinement remain in the
Python/app layer.

## A5000 Environment

Both clean-source artifacts were run from source commit
`3b845c1085add4ae304123fcd78985359c61acf0` on an NVIDIA RTX A5000 pod:

- GPU: NVIDIA RTX A5000, driver 580.126.09, 24564 MiB
- Python: 3.12.3
- Embree library: `/root/rtdl_goal3556_current/build/librtdl_embree.so`
- OptiX library: `/root/rtdl_goal3556_current/build/librtdl_optix.so`
- OptiX headers: `/opt/optix/include/optix.h`

The artifact environment still lists older untracked pod report directories in
`git_status_short`, but the relevant source files were not dirty after the
Goal3583 source commit was pulled.

## Standard Fixture Results

Artifact:
`docs/reports/goal3583_rayjoin_hot_promoted_routes_a5000/summary.json`

Tier: `standard`, case repeat: `3`, promoted route query repeat/warmup:
`5/1`.

| RayJoin-style contract | Embree sec | OptiX hot prepared-query sec | OptiX speedup vs Embree |
| --- | ---: | ---: | ---: |
| PIP positive assignment count/refinement | 0.010831083 | 0.002115869 | 5.119x |
| LSI dense left-id count | 0.012941647 | 0.000102108 | 126.744x |
| Overlay active pair-dependency count | 0.349695023 | 0.000357255 | 978.838x |

## Stress Fixture Results

Artifact:
`docs/reports/goal3583_rayjoin_hot_promoted_routes_stress_a5000/summary.json`

Tier: `stress`, case repeat: `3`, promoted route query repeat/warmup: `5/1`.

| RayJoin-style contract | Embree sec | OptiX hot prepared-query sec | OptiX speedup vs Embree |
| --- | ---: | ---: | ---: |
| PIP positive assignment count/refinement | 0.034963941 | 0.005896886 | 5.929x |
| LSI dense left-id count | 0.019551154 | 0.000131294 | 148.911x |
| Overlay active pair-dependency count | 5.392689579 | 0.001166145 | 4624.372x |

## Interpretation

The promoted routes are strong when measured under their actual prepared-handle
contract.

The important correction is not merely a better number. It is the measurement
boundary:

- `case_repeat` still launches independent processes to guard whole-case
  repeatability;
- inside each promoted OptiX process, the app now prepares once, warms up once,
  and reports the median of five hot prepared queries;
- Embree continues to report its backend workload elapsed time for the same
  derived tiled fixture;
- the comparison is a hot prepared-query comparison for repeated RayJoin-style
  contracts, not cold end-to-end setup time.

The standard and stress packets now agree directionally:

- PIP remains the least dramatic because it still performs exact CuPy simple-ring
  refinement after RT candidate generation.
- LSI becomes a clear win because the generic segment-pair traversal feeds a
  dense left-id count device-column contract.
- Overlay becomes the strongest win because the generic shape-pair active-count
  continuation avoids materializing full relation rows and only returns the
  scalar active count.

## Boundaries

This goal does not authorize:

- full RayJoin paper reproduction;
- paper-scale performance claims;
- an RTDL-beats-RayJoin claim;
- broad RT-core speedup wording;
- whole-application RayJoin acceleration claims;
- true zero-copy claims;
- release claims.

The fixtures are derived tiled workloads. The overlay row is an active
pair-dependency count, not full polygon overlay materialization. The PIP row
uses a CuPy exact refinement step in the app layer. These are valid v2.x
benchmark contracts, but they are not the full RayJoin paper implementation.

## Validation

Local validation:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal3583_rayjoin_hot_promoted_routes_a5000_test \
  tests.goal3582_rayjoin_promoted_strengthened_runner_test \
  tests.goal2636_strengthen_benchmark_rows_test
```

Result: `Ran 10 tests in 0.942s - OK`.

The Goal3583 artifact test checks:

- both standard and stress artifacts exist;
- all six rows in each packet are `ok`;
- promoted OptiX rows use `phases_sec.prepared_query_sec`;
- promoted OptiX rows record `repeat_protocol` as repeat `5`, warmup `1`;
- all comparable promoted OptiX ratios are faster than Embree;
- claim-boundary flags remain false.

## Next Work

The next useful performance work for RayJoin is no longer generic "measure the
promoted routes" work. The promoted hot routes are now measured correctly.

Useful next targets are:

1. decide whether a single composite RayJoin benchmark score should aggregate
   PIP, LSI, and overlay active-count contracts with fixed weights;
2. add a full-overlay materialization/continuation route if the benchmark needs
   polygon overlay rows rather than active dependency counts;
3. compare against an external RayJoin-style CUDA/OptiX baseline only under a
   separately reviewed same-contract protocol.
